from typing import Optional, List
from src.repositories.base import BaseRepository
from src.models.user import User


class UserRepository(BaseRepository):
    """Repository for managing User entities in the database."""

    def create(self, user: User) -> User:
        """Insert a new user into the database.

        Args:
            user: User instance to create.

        Returns:
            The created User instance with its assigned id.

        Raises:
            ValueError: If a user with the same telegram_id already exists.
        """
        existing = self.get_by_telegram_id(user.telegram_id)
        if existing:
            raise ValueError(f"User with telegram_id {user.telegram_id} already exists.")

        query = """
            INSERT INTO users (telegram_id, username, first_name, last_name, language_code, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user.telegram_id,
            user.username,
            user.first_name,
            user.last_name,
            user.language_code,
            user.is_active,
            user.created_at,
            user.updated_at,
        )
        cursor = self.execute(query, params)
        user.id = cursor.lastrowid
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by its primary key.

        Args:
            user_id: The user's database id.

        Returns:
            User instance if found, else None.
        """
        query = "SELECT * FROM users WHERE id = ?"
        row = self.fetchone(query, (user_id,))
        return User.from_dict(row) if row else None

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Retrieve a user by their Telegram ID.

        Args:
            telegram_id: The Telegram user ID.

        Returns:
            User instance if found, else None.
        """
        query = "SELECT * FROM users WHERE telegram_id = ?"
        row = self.fetchone(query, (telegram_id,))
        return User.from_dict(row) if row else None

    def get_all_active(self) -> List[User]:
        """Retrieve all active users.

        Returns:
            List of active User instances.
        """
        query = "SELECT * FROM users WHERE is_active = 1"
        rows = self.fetchall(query)
        return [User.from_dict(row) for row in rows]

    def update(self, user: User) -> User:
        """Update an existing user's data.

        Args:
            user: User instance with updated fields. Must have an id set.

        Returns:
            The updated User instance.

        Raises:
            ValueError: If no user with the given id exists.
        """
        existing = self.get_by_id(user.id)
        if not existing:
            raise ValueError(f"User with id {user.id} does not exist.")

        query = """
            UPDATE users
            SET telegram_id = ?, username = ?, first_name = ?, last_name = ?,
                language_code = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        """
        params = (
            user.telegram_id,
            user.username,
            user.first_name,
            user.last_name,
            user.language_code,
            user.is_active,
            user.updated_at,
            user.id,
        )
        self.execute(query, params)
        return user

    def delete(self, user_id: int) -> None:
        """Delete a user by its primary key.

        Args:
            user_id: The user's database id.

        Raises:
            ValueError: If no user with the given id exists.
        """
        existing = self.get_by_id(user_id)
        if not existing:
            raise ValueError(f"User with id {user_id} does not exist.")

        query = "DELETE FROM users WHERE id = ?"
        self.execute(query, (user_id,))

    def deactivate(self, user_id: int) -> None:
        """Set a user's is_active flag to False.

        Args:
            user_id: The user's database id.

        Raises:
            ValueError: If no user with the given id exists.
        """
        existing = self.get_by_id(user_id)
        if not existing:
            raise ValueError(f"User with id {user_id} does not exist.")

        query = "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute(query, (user_id,))