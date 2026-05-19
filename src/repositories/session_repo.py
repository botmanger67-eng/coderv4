from typing import Optional, List
from src.repositories.base import BaseRepository
from src.models.session import Session


class SessionRepository(BaseRepository):
    """Repository for managing Session records in the database."""

    def create(self, session: Session) -> Session:
        """Insert a new session into the database.

        Args:
            session: Session object to create.

        Returns:
            The created Session object with its assigned id.

        Raises:
            ValueError: If session already has an id.
        """
        if session.id is not None:
            raise ValueError("Cannot create a session that already has an id.")

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (user_id, chat_id, state, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.user_id,
                session.chat_id,
                session.state,
                session.data,
                session.created_at,
                session.updated_at,
            ),
        )
        self.connection.commit()
        session.id = cursor.lastrowid
        return session

    def get_by_id(self, session_id: int) -> Optional[Session]:
        """Retrieve a session by its id.

        Args:
            session_id: The id of the session.

        Returns:
            Session object if found, else None.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, user_id, chat_id, state, data, created_at, updated_at FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Session(
            id=row[0],
            user_id=row[1],
            chat_id=row[2],
            state=row[3],
            data=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def get_by_user_id(self, user_id: int) -> List[Session]:
        """Retrieve all sessions for a given user.

        Args:
            user_id: The user's id.

        Returns:
            List of Session objects.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, user_id, chat_id, state, data, created_at, updated_at FROM sessions WHERE user_id = ?",
            (user_id,),
        )
        rows = cursor.fetchall()
        return [
            Session(
                id=row[0],
                user_id=row[1],
                chat_id=row[2],
                state=row[3],
                data=row[4],
                created_at=row[5],
                updated_at=row[6],
            )
            for row in rows
        ]

    def get_by_chat_id(self, chat_id: int) -> List[Session]:
        """Retrieve all sessions for a given chat.

        Args:
            chat_id: The chat's id.

        Returns:
            List of Session objects.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, user_id, chat_id, state, data, created_at, updated_at FROM sessions WHERE chat_id = ?",
            (chat_id,),
        )
        rows = cursor.fetchall()
        return [
            Session(
                id=row[0],
                user_id=row[1],
                chat_id=row[2],
                state=row[3],
                data=row[4],
                created_at=row[5],
                updated_at=row[6],
            )
            for row in rows
        ]

    def update(self, session: Session) -> Session:
        """Update an existing session.

        Args:
            session: Session object with updated fields.

        Returns:
            The updated Session object.

        Raises:
            ValueError: If session has no id.
        """
        if session.id is None:
            raise ValueError("Cannot update a session without an id.")

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE sessions
            SET user_id = ?, chat_id = ?, state = ?, data = ?, created_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                session.user_id,
                session.chat_id,
                session.state,
                session.data,
                session.created_at,
                session.updated_at,
                session.id,
            ),
        )
        self.connection.commit()
        return session

    def delete(self, session_id: int) -> bool:
        """Delete a session by its id.

        Args:
            session_id: The id of the session to delete.

        Returns:
            True if a row was deleted, False otherwise.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all sessions for a given user.

        Args:
            user_id: The user's id.

        Returns:
            Number of deleted rows.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        self.connection.commit()
        return cursor.rowcount

    def delete_by_chat_id(self, chat_id: int) -> int:
        """Delete all sessions for a given chat.

        Args:
            chat_id: The chat's id.

        Returns:
            Number of deleted rows.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE chat_id = ?", (chat_id,))
        self.connection.commit()
        return cursor.rowcount