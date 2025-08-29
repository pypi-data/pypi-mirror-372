"""Filesystem-based snapshot repository implementation."""

from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.domain.entities.instance_config import InstanceConfig
from snapshot.domain.entities.snapshot_metadata import (
    ModuleSnapshot,
    RepositorySnapshot,
    SnapshotMetadata,
)
from snapshot.domain.repositories.snapshot_repository import SnapshotRepository

# Note: FilesystemBackupRepository removed - snapshots no longer depend on
# backup implementation


class FilesystemSnapshotRepository(SnapshotRepository):
    """
    Filesystem-based implementation of snapshot repository.

    Stores snapshots as JSON metadata files with optional backup references.
    """

    def __init__(self, base_snapshot_dir: str = "/opt/dooservice/snapshots"):
        """Initialize the filesystem snapshot repository."""
        self.base_snapshot_dir = Path(base_snapshot_dir)
        self.base_snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create metadata index file if it doesn't exist
        self.metadata_file = self.base_snapshot_dir / "snapshots.json"
        if not self.metadata_file.exists():
            self._save_metadata_index([])

        # Backup functionality disabled until new simplified backup system integration
        self.backup_repository = None

    def create_snapshot(
        self,
        instance_config: InstanceConfig,
        instance_name: str,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        include_backup: bool = True,
    ) -> SnapshotMetadata:
        """Create a complete snapshot of instance state."""
        snapshot_id = str(uuid4())
        created_at = datetime.now()

        # Create backup if requested (disabled until new backup system integration)
        backup_id = None
        if include_backup:
            # TODO: Integrate with new simplified backup system
            print(
                "⚠️  Backup functionality disabled. Use new 'dooservice backup "
                "create' command instead.",
            )
            backup_id = None

        # Capture repository states
        repository_snapshots = self._capture_repository_states(instance_config)

        # Capture module states
        module_snapshots = self._capture_module_states(instance_config, instance_name)

        # Create configuration checksum
        config_checksum = self._calculate_config_checksum(instance_config)

        # Create snapshot metadata
        snapshot = SnapshotMetadata(
            snapshot_id=snapshot_id,
            instance_name=instance_name,
            tag=tag,
            created_at=created_at,
            description=description,
            odoo_version=instance_config.odoo_version,
            configuration_checksum=config_checksum,
            repositories=repository_snapshots,
            installed_modules=module_snapshots,
            backup_id=backup_id,
            python_dependencies=instance_config.python_dependencies.copy(),
            env_vars={k: str(v) for k, v in instance_config.env_vars.items()},
        )

        # Save snapshot metadata to file
        snapshot_file = self.base_snapshot_dir / f"{snapshot_id}.json"
        snapshot.file_path = str(snapshot_file)

        with open(snapshot_file, "w") as f:
            json.dump(self._snapshot_to_dict(snapshot), f, indent=2)

        snapshot.file_size = snapshot_file.stat().st_size

        # Add to index
        self._add_snapshot_to_index(snapshot)

        return snapshot

    def restore_snapshot(
        self,
        snapshot_id: str,
        target_instance: str,
        restore_data: bool = True,
        restore_modules: bool = True,
    ) -> None:
        """Restore instance from snapshot."""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Restore backup data if requested and available
        # (disabled until new backup system integration)
        if restore_data and snapshot.backup_id:
            # TODO: Integrate with new simplified backup system for restore
            print(
                "⚠️  Backup restore functionality disabled. Use new backup "
                "system for restore operations.",
            )

        # Restore repository states
        self._restore_repository_states(snapshot.repositories, target_instance)

        # Restore module states if requested
        if restore_modules:
            self._restore_module_states(snapshot.installed_modules, target_instance)

    def list_snapshots(
        self,
        instance_name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[SnapshotMetadata]:
        """List available snapshots with optional filtering."""
        snapshots = self._load_metadata_index()

        # Filter by instance name
        if instance_name:
            snapshots = [s for s in snapshots if s.instance_name == instance_name]

        # Filter by tag
        if tag:
            snapshots = [s for s in snapshots if s.tag == tag]

        # Sort by creation date, newest first
        snapshots.sort(key=lambda s: s.created_at, reverse=True)

        return snapshots

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot by ID."""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Delete snapshot file
        snapshot_file = Path(snapshot.file_path)
        if snapshot_file.exists():
            snapshot_file.unlink()

        # Delete associated backup if exists
        # (disabled until new backup system integration)
        if snapshot.backup_id:
            # TODO: Integrate with new simplified backup system for deletion
            print("⚠️  Backup deletion functionality disabled.")

        # Remove from index
        snapshots = self._load_metadata_index()
        updated_snapshots = [s for s in snapshots if s.snapshot_id != snapshot_id]
        self._save_metadata_index(updated_snapshots)

    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotMetadata]:
        """Get snapshot metadata by ID."""
        # Check if it's a short ID and try to find full match
        snapshots = self._load_metadata_index()

        # First try exact match
        for snapshot in snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return snapshot

        # Then try prefix match for short IDs
        matches = [s for s in snapshots if s.snapshot_id.startswith(snapshot_id)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(
                f"Ambiguous snapshot ID {snapshot_id}: matches "
                f"{len(matches)} snapshots",
            )

        return None

    def _capture_repository_states(
        self,
        instance_config: InstanceConfig,
    ) -> List[RepositorySnapshot]:
        """Capture current state of repositories."""
        repo_snapshots = []

        for repo_name, repo_config in instance_config.repositories.items():
            if hasattr(repo_config, "url"):
                # Try to get commit hash if repository is cloned
                container_name = instance_config.deployment.docker.web.container_name
                repo_path = (
                    f"/opt/odoo-data/{container_name.replace('web_', '')}/addons/"
                    f"{repo_name}"
                )
                commit_hash = self._get_repository_commit(repo_path)

                repo_snapshot = RepositorySnapshot(
                    name=repo_name,
                    url=repo_config.url,
                    branch=getattr(repo_config, "branch", "main"),
                    commit_hash=commit_hash,
                    path=repo_path,
                )
                repo_snapshots.append(repo_snapshot)

        return repo_snapshots

    def _capture_module_states(
        self,
        instance_config: InstanceConfig,
        instance_name: str,
    ) -> List[ModuleSnapshot]:
        """Capture current state of installed modules."""
        module_snapshots = []

        try:
            # Query module states from database
            db_container = instance_config.deployment.docker.db.container_name

            query = """
                SELECT name, latest_version, state, auto_install
                FROM ir_module_module
                WHERE state IN ('installed', 'to_upgrade', 'to_remove')
            """

            cmd = [
                "docker",
                "exec",
                db_container,
                "psql",
                "-U",
                "odoo",
                "-d",
                "postgres",
                "-t",
                "-c",
                query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 4:
                            module_snapshot = ModuleSnapshot(
                                name=parts[0],
                                version=parts[1] or "unknown",
                                state=parts[2],
                                auto_install=parts[3].lower() == "t",
                            )
                            module_snapshots.append(module_snapshot)

        except (subprocess.SubprocessError, OSError) as e:
            # If module state capture fails, continue without it
            self.logger.warning("Failed to capture module states: %s", e)

        return module_snapshots

    def _get_repository_commit(self, repo_path: str) -> str:
        """Get current commit hash of a repository."""
        try:
            if Path(repo_path).exists():
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except (subprocess.SubprocessError, OSError) as e:
            self.logger.warning(
                "Failed to get repository commit for %s: %s", repo_path, e
            )

        return "unknown"

    def _calculate_config_checksum(self, instance_config: InstanceConfig) -> str:
        """Calculate checksum of instance configuration."""
        from dataclasses import asdict

        config_dict = asdict(instance_config)
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def _restore_repository_states(
        self,
        repositories: List[RepositorySnapshot],
        target_instance: str,
    ) -> None:
        """Restore repository states to specific commits."""
        for repo_snapshot in repositories:
            try:
                # Check if repository exists and checkout specific commit
                if Path(repo_snapshot.path).exists():
                    # Checkout specific commit
                    subprocess.run(
                        ["git", "checkout", repo_snapshot.commit_hash],
                        cwd=repo_snapshot.path,
                        capture_output=True,
                        check=False,
                    )
            except (subprocess.SubprocessError, OSError) as e:
                # If restore fails, continue with next repository
                self.logger.warning(
                    "Failed to restore repository %s: %s", repo_snapshot.path, e
                )
                continue

    def _restore_module_states(
        self,
        modules: List[ModuleSnapshot],
        target_instance: str,
    ) -> None:
        """Restore module states (simplified implementation)."""
        # This is a simplified implementation
        # In a full implementation, you would:
        # 1. Connect to Odoo via XML-RPC or direct database
        # 2. Install/uninstall/upgrade modules as needed
        # 3. Handle module dependencies

        # For now, we'll just log what would be restored
        print(f"Would restore {len(modules)} module states for {target_instance}")

    def _snapshot_to_dict(self, snapshot: SnapshotMetadata) -> Dict[str, Any]:
        """Convert snapshot metadata to dictionary for JSON serialization."""
        return {
            "snapshot_id": snapshot.snapshot_id,
            "instance_name": snapshot.instance_name,
            "tag": snapshot.tag,
            "created_at": snapshot.created_at.isoformat(),
            "description": snapshot.description,
            "odoo_version": snapshot.odoo_version,
            "configuration_checksum": snapshot.configuration_checksum,
            "repositories": [
                {
                    "name": repo.name,
                    "url": repo.url,
                    "branch": repo.branch,
                    "commit_hash": repo.commit_hash,
                    "path": repo.path,
                }
                for repo in snapshot.repositories
            ],
            "installed_modules": [
                {
                    "name": mod.name,
                    "version": mod.version,
                    "state": mod.state,
                    "auto_install": mod.auto_install,
                    "repository": mod.repository,
                }
                for mod in snapshot.installed_modules
            ],
            "backup_id": snapshot.backup_id,
            "python_dependencies": snapshot.python_dependencies,
            "env_vars": snapshot.env_vars,
            "file_path": snapshot.file_path,
            "file_size": snapshot.file_size,
            "version": snapshot.version,
        }

    def _dict_to_snapshot(self, data: Dict[str, Any]) -> SnapshotMetadata:
        """Convert dictionary to snapshot metadata."""
        repositories = [
            RepositorySnapshot(
                name=repo_data["name"],
                url=repo_data["url"],
                branch=repo_data["branch"],
                commit_hash=repo_data["commit_hash"],
                path=repo_data["path"],
            )
            for repo_data in data.get("repositories", [])
        ]

        modules = [
            ModuleSnapshot(
                name=mod_data["name"],
                version=mod_data["version"],
                state=mod_data["state"],
                auto_install=mod_data["auto_install"],
                repository=mod_data.get("repository"),
            )
            for mod_data in data.get("installed_modules", [])
        ]

        return SnapshotMetadata(
            snapshot_id=data["snapshot_id"],
            instance_name=data["instance_name"],
            tag=data.get("tag"),
            created_at=datetime.fromisoformat(data["created_at"]),
            description=data.get("description"),
            odoo_version=data["odoo_version"],
            configuration_checksum=data["configuration_checksum"],
            repositories=repositories,
            installed_modules=modules,
            backup_id=data.get("backup_id"),
            python_dependencies=data.get("python_dependencies", []),
            env_vars=data.get("env_vars", {}),
            file_path=data.get("file_path", ""),
            file_size=data.get("file_size", 0),
            version=data.get("version", "1.0"),
        )

    def _load_metadata_index(self) -> List[SnapshotMetadata]:
        """Load snapshot metadata from index file."""
        if not self.metadata_file.exists():
            return []

        try:
            with open(self.metadata_file) as f:
                data = json.load(f)

            return [self._dict_to_snapshot(item) for item in data]

        except (json.JSONDecodeError, KeyError, ValueError):
            return []

    def _save_metadata_index(self, snapshots: List[SnapshotMetadata]) -> None:
        """Save snapshot metadata to index file."""
        data = [self._snapshot_to_dict(snapshot) for snapshot in snapshots]

        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def _add_snapshot_to_index(self, snapshot: SnapshotMetadata) -> None:
        """Add new snapshot to index."""
        snapshots = self._load_metadata_index()
        snapshots.append(snapshot)
        self._save_metadata_index(snapshots)
