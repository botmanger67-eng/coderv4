from typing import Optional, List
from src.repositories.base import BaseRepository
from src.models.authorized_user import AuthorizedUser


class AuthorizedUserRepository(BaseRepository):
    """Repository for managing authorized users in the database."""

    def __init__(self, db_path: str = "bot.db") -> None:
        """Initialize the authorized user repository.

        Args:
            db_path: Path to the SQLite database file.
        """
        super().__init__(db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the authorized_users table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS authorized_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        """
        self.execute(query)

    def add_user(self, user: AuthorizedUser) -> bool:
        """Add a new authorized user.

        Args:
            user: The authorized user to add.

        Returns:
            True if the user was added, False if already exists.
        """
        query = """
        INSERT OR IGNORE INTO authorized_users (user_id, username, first_name, last_name, is_active)
        VALUES (?, ?, ?, ?, ?)
        """
        result = self.execute(
            query,
            (user.user_id, user.username, user.first_name, user.last_name, user.is_active),
        )
        return result > 0

    def get_user(self, user_id: int) -> Optional[AuthorizedUser]:
        """Get an authorized user by their user ID.

        Args:
            user_id: The Telegram user ID.

        Returns:
            The authorized user if found, None otherwise.
        """
        query = "SELECT * FROM authorized_users WHERE user_id = ?"
        row = self.fetchone(query, (user_id,))
        if row:
            return AuthorizedUser(**dict(row))
        return None

    def get_all_users(self) -> List[AuthorizedUser]:
        """Get all authorized users.

        Returns:
            A list of all authorized users.
        """
        query = "SELECT * FROM authorized_users ORDER BY created_at DESC"
        rows = self.fetchall(query)
        return [AuthorizedUser(**dict(row)) for row in rows]

    def get_active_users(self) -> List[AuthorizedUser]:
        """Get all active authorized users.

        Returns:
            A list of active authorized users.
        """
        query = "SELECT * FROM authorized_users WHERE is_active = 1 ORDER BY created_at DESC"
        rows = self.fetchall(query)
        return [AuthorizedUser(**dict(row)) for row in rows]

    def update_user(self, user: AuthorizedUser) -> bool:
        """Update an existing authorized user.

        Args:
            user: The authorized user with updated fields.

        Returns:
            True if the user was updated, False if not found.
        """
        query = """
        UPDATE authorized_users
        SET username = ?, first_name = ?, last_name = ?, is_active = ?, updated_at = datetime('now')
        WHERE user_id = ?
        """
        result = self.execute(
            query,
            (user.username, user.first_name, user.last_name, user.is_active, user.user_id),
        )
        return result > 0

    def remove_user(self, user_id: int) -> bool:
        """Remove an authorized user.

        Args:
            user_id: The Telegram user ID to remove.

        Returns:
            True if the user was removed, False if not found.
        """
        query = "DELETE FROM authorized_users WHERE user_id = ?"
        result = self.execute(query, (user_id,))
        return result > 0

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate an authorized user.

        Args:
            user_id: The Telegram user ID to deactivate.

        Returns:
            True if the user was deactivated, False if not found.
        """
        query = """
        UPDATE authorized_users
        SET is_active = 0, updated_at = datetime('now')
        WHERE user_id = ?
        """
        result = self.execute(query, (user_id,))
        return result > 0

    def activate_user(self, user_id: int) -> bool:
        """Activate a previously deactivated authorized user.

        Args:
            user_id: The Telegram user ID to activate.

        Returns:
            True if the user was activated, False if not found.
        """
        query = """
        UPDATE authorized_users
        SET is_active = 1, updated_at = datetime('now')
        WHERE user_id = ?
        """
        result = self.execute(query, (user_id,))
        return result > 0

    def user_exists(self, user_id: int) -> bool:
        """Check if a user is authorized.

        Args:
            user_id: The Telegram user ID to check.

        Returns:
            True if the user exists and is active, False otherwise.
        """
        query = "SELECT 1 FROM authorized_users WHERE user_id = ? AND is_active = 1"
        row = self.fetchone(query, (user_id,))
        return row is not None

    def count_users(self) -> int:
        """Get the total number of authorized users.

        Returns:
            The count of authorized users.
        """
        query = "SELECT COUNT(*) as count FROM authorized_users"
        row = self.fetchone(query)
        return row["count"] if row else 0

    def count_active_users(self) -> int:
        """Get the number of active authorized users.

        Returns:
            The count of active authorized users.
        """
        query = "SELECT COUNT(*) as count FROM authorized_users WHERE is_active = 1"
        row = self.fetchone(query)
        return row["count"] if row else 0