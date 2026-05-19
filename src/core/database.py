import sqlite3
from pathlib import Path
from typing import Optional, Any
from src.core.config import settings


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize database manager with optional custom path.

        Args:
            db_path: Path to SQLite database file. Defaults to settings.DATABASE_PATH.
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get or create database connection.

        Returns:
            Active SQLite connection with row factory set.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection

    def close(self) -> None:
        """Close database connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> sqlite3.Cursor:
        """Execute a query with parameters.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            Cursor object after execution.

        Raises:
            sqlite3.Error: If query execution fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise

    def execute_many(
        self, query: str, params_list: list[tuple[Any, ...]]
    ) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets.

        Args:
            query: SQL query string.
            params_list: List of parameter tuples.

        Returns:
            Cursor object after execution.

        Raises:
            sqlite3.Error: If query execution fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise

    def fetch_one(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> Optional[sqlite3.Row]:
        """Fetch a single row from query.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            Single row or None if no results.
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetch_all(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> list[sqlite3.Row]:
        """Fetch all rows from query.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            List of rows.
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def commit(self) -> None:
        """Commit current transaction."""
        if self._connection is not None:
            self._connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._connection is not None:
            self._connection.rollback()

    def __enter__(self) -> "DatabaseManager":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Context manager exit with cleanup."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()


def get_database() -> DatabaseManager:
    """Get database manager instance.

    Returns:
        DatabaseManager instance configured from settings.
    """
    return DatabaseManager()