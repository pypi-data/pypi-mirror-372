"""Pure domain service for database credential operations."""

from typing import List, Optional

from instance.domain.repositories.instance_repository import InstanceRepository


class DatabaseCredentialSyncService:
    """
    Pure domain service for executing database credential synchronization operations.

    This service provides methods to generate and execute SQL commands for
    updating PostgreSQL user credentials. It does not handle configuration
    logic or diff detection - that belongs in the application/infrastructure layers.
    """

    def __init__(self, instance_repository: InstanceRepository):
        """
        Initialize the service with required repositories.

        Args:
            instance_repository: Repository for container operations.
        """
        self._instance_repository = instance_repository

    def sync_database_credentials(
        self,
        db_container_name: str,
        old_user: Optional[str],
        new_user: str,
        new_password: str,
        superuser: Optional[str] = None,
    ) -> None:
        """
        Execute database credential synchronization for given parameters.

        Args:
            db_container_name: Name of the database container.
            old_user: Previous username (None if creating new user).
            new_user: New username.
            new_password: New password.
            superuser: Database superuser to connect as (defaults to new_user).
        """
        # Use new_user as superuser if not specified (PostgreSQL container setup)
        db_superuser = superuser or new_user

        sql_commands = self.generate_credential_sync_sql(
            old_user, new_user, new_password
        )

        for sql_command in sql_commands:
            self.execute_sql_in_container(db_container_name, sql_command, db_superuser)

    def generate_credential_sync_sql(
        self,
        old_user: Optional[str],
        new_user: str,
        new_password: str,
    ) -> List[str]:
        """
        Generate SQL commands to update database credentials.

        Args:
            old_user: Previous username (if available).
            new_user: New username.
            new_password: New password.

        Returns:
            List of SQL commands to execute.
        """
        commands = []

        if old_user and old_user != new_user:
            # User changed: rename the user and update password
            commands.extend(
                [
                    f"ALTER USER {old_user} RENAME TO {new_user};",
                    f"ALTER USER {new_user} WITH PASSWORD '{new_password}';",
                ]
            )
        elif old_user == new_user:
            # Same user: just update password
            commands.append(
                f"ALTER USER {new_user} WITH PASSWORD '{new_password}';",
            )
        else:
            # New user: create user (this shouldn't happen in sync, but just in case)
            commands.extend(
                [
                    f"CREATE USER {new_user} WITH PASSWORD '{new_password}';",
                    f"GRANT ALL PRIVILEGES ON DATABASE postgres TO {new_user};",
                ]
            )

        return commands

    def execute_sql_in_container(
        self,
        container_name: str,
        sql_command: str,
        db_user: str,
    ) -> None:
        """
        Execute a SQL command inside the database container.

        Args:
            container_name: Name of the database container.
            sql_command: SQL command to execute.
            db_user: Database user to connect as (should be a superuser).

        Raises:
            Exception: If the SQL command execution fails.
        """
        # Use psql to execute the SQL command with the specified user on postgres
        # database
        psql_command = f'psql -U {db_user} -d postgres -c "{sql_command}"'

        exit_code, output = self._instance_repository.exec_command(
            container_name,
            psql_command,
        )

        if exit_code != 0:
            raise Exception(
                f"Failed to execute SQL command in container '{container_name}': "
                f"Exit code: {exit_code}, Output: {output}",
            )
