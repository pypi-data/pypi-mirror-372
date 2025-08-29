"""Consolidated database management service for instances."""

import logging
from typing import List, Optional

from instance.domain.repositories.instance_repository import InstanceRepository


class DatabaseManager:
    """
    Consolidated service for managing database operations in instances.

    This service provides a clean interface for database management with
    improved error handling, logging, and credential synchronization.
    """

    def __init__(
        self,
        instance_repository: InstanceRepository,
        logger: Optional[logging.Logger] = None,
    ):
        self._instance_repository = instance_repository
        self._logger = logger or logging.getLogger(__name__)

    def sync_credentials(
        self,
        db_container_name: str,
        old_user: Optional[str],
        new_user: str,
        new_password: str,
        superuser: Optional[str] = None,
    ) -> None:
        """
        Synchronize database credentials with improved error handling.

        Args:
            db_container_name: Name of the database container
            old_user: Previous username (None if creating new user)
            new_user: New username
            new_password: New password
            superuser: Database superuser to connect as (defaults to new_user)

        Raises:
            DatabaseError: If credential sync fails
        """
        self._logger.info(
            "Synchronizing database credentials for container '%s' "
            "(old_user: %s, new_user: %s)",
            db_container_name,
            old_user,
            new_user,
        )

        # Use new_user as superuser if not specified (PostgreSQL container setup)
        db_superuser = superuser or new_user

        try:
            sql_commands = self._generate_credential_sync_sql(
                old_user, new_user, new_password
            )

            for i, sql_command in enumerate(sql_commands, 1):
                self._logger.debug("Executing SQL command %d/%d", i, len(sql_commands))
                self._execute_sql_in_container(
                    db_container_name, sql_command, db_superuser
                )

            self._logger.info(
                "Successfully synchronized credentials for user '%s' in container '%s'",
                new_user,
                db_container_name,
            )

        except Exception as e:
            self._logger.error(
                "Failed to sync credentials for container '%s': %s",
                db_container_name,
                e,
            )
            raise

    def execute_sql(
        self,
        db_container_name: str,
        sql_command: str,
        database_user: str,
        database_name: str = "postgres",
    ) -> str:
        """
        Execute a SQL command in the database container.

        Args:
            db_container_name: Name of the database container
            sql_command: SQL command to execute
            database_user: Database user to connect as
            database_name: Database name to connect to

        Returns:
            Command output

        Raises:
            DatabaseError: If SQL execution fails
        """
        self._logger.debug(
            "Executing SQL in container '%s' as user '%s'",
            db_container_name,
            database_user,
        )

        try:
            result = self._execute_sql_in_container(
                db_container_name, sql_command, database_user, database_name
            )
            self._logger.debug("SQL command executed successfully")
            return result

        except Exception as e:
            self._logger.error("Failed to execute SQL command: %s", e)
            raise

    def test_connection(
        self,
        db_container_name: str,
        database_user: str,
        database_name: str = "postgres",
    ) -> bool:
        """
        Test database connection for a given user.

        Args:
            db_container_name: Name of the database container
            database_user: Database user to test
            database_name: Database name to connect to

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._execute_sql_in_container(
                db_container_name, "SELECT 1;", database_user, database_name
            )
            return True
        except (ConnectionError, TimeoutError, ValueError) as e:
            self._logger.debug(
                "Connection test failed for user '%s': %s", database_user, e
            )
            return False

    def list_databases(self, db_container_name: str, database_user: str) -> List[str]:
        """
        List all databases in the PostgreSQL instance.

        Args:
            db_container_name: Name of the database container
            database_user: Database user to connect as

        Returns:
            List of database names
        """
        try:
            result = self._execute_sql_in_container(
                db_container_name,
                "SELECT datname FROM pg_database WHERE datistemplate = false;",
                database_user,
            )

            # Parse the output to extract database names
            databases = []
            for line in result.split("\n"):
                cleaned_line = line.strip()
                if (
                    cleaned_line
                    and not cleaned_line.startswith("-")
                    and cleaned_line != "datname"
                ):
                    databases.append(cleaned_line)

            return databases

        except Exception as e:
            self._logger.error("Failed to list databases: %s", e)
            raise

    def create_database(
        self, db_container_name: str, database_name: str, owner: str, database_user: str
    ) -> None:
        """
        Create a new database with specified owner.

        Args:
            db_container_name: Name of the database container
            database_name: Name of the new database
            owner: Database user who will own the database
            database_user: Database user to connect as (must have CREATEDB privilege)
        """
        sql_command = f"CREATE DATABASE {database_name} OWNER {owner};"

        try:
            self._execute_sql_in_container(
                db_container_name, sql_command, database_user
            )
            self._logger.info(
                "Created database '%s' with owner '%s'", database_name, owner
            )
        except Exception as e:
            self._logger.error("Failed to create database '%s': %s", database_name, e)
            raise

    def _generate_credential_sync_sql(
        self, old_user: Optional[str], new_user: str, new_password: str
    ) -> List[str]:
        """
        Generate SQL commands for credential synchronization.

        Args:
            old_user: Previous username (None if creating new user)
            new_user: New username
            new_password: New password

        Returns:
            List of SQL commands to execute
        """
        sql_commands = []

        if old_user and old_user != new_user:
            # Rename existing user
            sql_commands.append(f"ALTER USER {old_user} RENAME TO {new_user};")

        # Check if user exists, create if not
        user_check = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_user
                          WHERE usename = '{new_user}') THEN
                CREATE USER {new_user};
            END IF;
        END
        $$;
        """
        sql_commands.append(user_check)

        # Set password and privileges
        sql_commands.append(f"ALTER USER {new_user} WITH PASSWORD '{new_password}';")
        sql_commands.append(f"ALTER USER {new_user} CREATEDB;")

        return sql_commands

    def _execute_sql_in_container(
        self,
        container_name: str,
        sql_command: str,
        database_user: str,
        database_name: str = "postgres",
    ) -> str:
        """
        Execute SQL command inside a PostgreSQL container.

        Args:
            container_name: Name of the database container
            sql_command: SQL command to execute
            database_user: Database user to connect as
            database_name: Database name to connect to

        Returns:
            Command output
        """
        # Build psql command
        psql_command = [
            "psql",
            f"-U{database_user}",
            f"-d{database_name}",
            "-c",
            sql_command,
        ]

        return self._instance_repository.exec_command(
            container_name, psql_command, service="db"
        )
