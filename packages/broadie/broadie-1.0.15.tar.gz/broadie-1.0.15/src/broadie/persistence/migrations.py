"""
Database migration utilities for Broadie.
Handles schema updates and data migration between versions.
"""

import asyncio
from typing import Callable, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from ..utils.exceptions import PersistenceError
from .models import Base
from .sqlalchemy_backend import SQLAlchemyBackend


class Migration:
    """Represents a single database migration."""

    def __init__(
        self,
        version: str,
        description: str,
        up_sql: str,
        down_sql: Optional[str] = None,
    ):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql


class MigrationManager:
    """Manages database migrations for Broadie."""

    def __init__(self, backend: SQLAlchemyBackend):
        self.backend = backend
        self.migrations = self._get_migrations()

    def _get_migrations(self) -> List[Migration]:
        """Define all migrations in order."""
        return [
            Migration(
                version="001",
                description="Add created_at column to messages table",
                up_sql="ALTER TABLE messages ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
                down_sql="ALTER TABLE messages DROP COLUMN created_at",
            ),
            Migration(
                version="002",
                description="Ensure all tables have proper indexes",
                up_sql="""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
                CREATE INDEX IF NOT EXISTS idx_todos_conversation_id ON todos(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);
                CREATE INDEX IF NOT EXISTS idx_memories_agent_id ON memories(agent_id);
                """,
                down_sql="""
                DROP INDEX IF EXISTS idx_messages_conversation_id;
                DROP INDEX IF EXISTS idx_messages_agent_id;
                DROP INDEX IF EXISTS idx_todos_conversation_id;
                DROP INDEX IF EXISTS idx_todos_status;
                DROP INDEX IF EXISTS idx_memories_agent_id;
                """,
            ),
        ]

    async def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            async with self.backend.get_session() as session:
                result = await session.execute(
                    text(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"
                    ),
                    {"table_name": table_name},
                )
                return result.scalar() is not None
        except Exception:
            return False

    async def _column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        try:
            async with self.backend.get_session() as session:
                result = await session.execute(text(f"PRAGMA table_info({table_name})"))
                columns = result.fetchall()
                return any(col[1] == column_name for col in columns)
        except Exception:
            return False

    async def _migration_exists(self, version: str) -> bool:
        """Check if a migration has been applied."""
        try:
            # First check if migrations table exists
            if not await self._table_exists("schema_migrations"):
                return False

            async with self.backend.get_session() as session:
                result = await session.execute(
                    text(
                        "SELECT version FROM schema_migrations WHERE version = :version"
                    ),
                    {"version": version},
                )
                return result.scalar() is not None
        except Exception:
            return False

    async def _create_migrations_table(self):
        """Create the schema migrations table."""
        try:
            async with self.backend.get_session() as session:
                await session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(10) PRIMARY KEY,
                        description TEXT,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
        except Exception as e:
            raise PersistenceError(f"Failed to create migrations table: {e}")

    async def _record_migration(self, migration: Migration):
        """Record that a migration has been applied."""
        try:
            async with self.backend.get_session() as session:
                await session.execute(
                    text(
                        "INSERT INTO schema_migrations (version, description) VALUES (:version, :description)"
                    ),
                    {
                        "version": migration.version,
                        "description": migration.description,
                    },
                )
        except Exception as e:
            raise PersistenceError(
                f"Failed to record migration {migration.version}: {e}"
            )

    async def migrate(self) -> List[str]:
        """Apply all pending migrations."""
        applied_migrations = []

        try:
            # Ensure migrations table exists
            await self._create_migrations_table()

            for migration in self.migrations:
                if not await self._migration_exists(migration.version):
                    print(
                        f"Applying migration {migration.version}: {migration.description}"
                    )

                    # Execute migration SQL
                    async with self.backend.get_session() as session:
                        # Split multiple statements and execute them separately
                        statements = [
                            stmt.strip()
                            for stmt in migration.up_sql.split(";")
                            if stmt.strip()
                        ]
                        for statement in statements:
                            try:
                                await session.execute(text(statement))
                            except OperationalError as e:
                                # Handle cases where column already exists or other non-critical errors
                                if (
                                    "duplicate column name" in str(e).lower()
                                    or "already exists" in str(e).lower()
                                ):
                                    print(f"  Skipping: {statement} (already exists)")
                                    continue
                                else:
                                    raise

                    # Record successful migration
                    await self._record_migration(migration)
                    applied_migrations.append(
                        f"{migration.version}: {migration.description}"
                    )
                    print(f"  ✓ Applied migration {migration.version}")
                else:
                    print(f"Skipping migration {migration.version}: already applied")

            return applied_migrations

        except Exception as e:
            raise PersistenceError(f"Migration failed: {e}")

    async def reset_database(self):
        """Drop all tables and recreate from models."""
        print("Resetting database schema...")

        try:
            # Drop all tables
            async with self.backend.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            print("✓ Database schema reset complete")

        except Exception as e:
            raise PersistenceError(f"Failed to reset database: {e}")


async def migrate_database(database_url: str) -> List[str]:
    """Convenience function to run migrations on a database."""
    backend = SQLAlchemyBackend(database_url)
    await backend.initialize()

    try:
        manager = MigrationManager(backend)
        applied = await manager.migrate()
        return applied
    finally:
        await backend.close()


async def reset_database_schema(database_url: str):
    """Convenience function to reset a database schema."""
    backend = SQLAlchemyBackend(database_url)
    await backend.initialize()

    try:
        manager = MigrationManager(backend)
        await manager.reset_database()
    finally:
        await backend.close()
