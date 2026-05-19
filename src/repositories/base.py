from typing import Any, Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

from src.core.database import Database

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository providing common database operations.

    This class defines the interface for repository pattern implementations,
    providing standard CRUD operations with type safety.

    Attributes:
        db: Database instance for executing queries.
        table_name: Name of the database table.
    """

    def __init__(self, db: Database, table_name: str) -> None:
        """Initialize the repository with a database connection.

        Args:
            db: Database instance.
            table_name: Name of the table this repository manages.

        Raises:
            ValueError: If table_name is empty.
        """
        if not table_name:
            raise ValueError("table_name must not be empty")
        self.db = db
        self.table_name = table_name

    @abstractmethod
    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """Convert a database row dictionary to a model instance.

        Args:
            row: Dictionary representing a database row.

        Returns:
            Model instance of type T.
        """
        ...

    @abstractmethod
    def _model_to_dict(self, model: T) -> Dict[str, Any]:
        """Convert a model instance to a dictionary for database operations.

        Args:
            model: Model instance to convert.

        Returns:
            Dictionary representation of the model.
        """
        ...

    async def create(self, model: T) -> Optional[T]:
        """Insert a new record into the database.

        Args:
            model: Model instance to insert.

        Returns:
            The created model instance with generated ID, or None if creation failed.
        """
        try:
            data = self._model_to_dict(model)
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = list(data.values())

            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            row_id = await self.db.execute_insert(query, values)

            if row_id is not None:
                return await self.get_by_id(row_id)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to create record in {self.table_name}: {e}") from e

    async def get_by_id(self, record_id: int) -> Optional[T]:
        """Retrieve a record by its ID.

        Args:
            record_id: Primary key value.

        Returns:
            Model instance if found, None otherwise.
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?"
            row = await self.db.fetch_one(query, (record_id,))
            if row:
                return self._row_to_model(row)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get record by ID from {self.table_name}: {e}") from e

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Retrieve all records with pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            List of model instances.
        """
        try:
            query = f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?"
            rows = await self.db.fetch_all(query, (limit, offset))
            return [self._row_to_model(row) for row in rows]
        except Exception as e:
            raise RuntimeError(f"Failed to get all records from {self.table_name}: {e}") from e

    async def update(self, model: T) -> Optional[T]:
        """Update an existing record.

        Args:
            model: Model instance with updated data. Must have an 'id' attribute.

        Returns:
            Updated model instance if successful, None otherwise.
        """
        try:
            data = self._model_to_dict(model)
            if "id" not in data:
                raise ValueError("Model must have an 'id' field for update")

            record_id = data.pop("id")
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values()) + [record_id]

            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
            affected = await self.db.execute(query, values)

            if affected > 0:
                return await self.get_by_id(record_id)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to update record in {self.table_name}: {e}") from e

    async def delete(self, record_id: int) -> bool:
        """Delete a record by its ID.

        Args:
            record_id: Primary key value of the record to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = ?"
            affected = await self.db.execute(query, (record_id,))
            return affected > 0
        except Exception as e:
            raise RuntimeError(f"Failed to delete record from {self.table_name}: {e}") from e

    async def count(self) -> int:
        """Get the total number of records in the table.

        Returns:
            Total record count.
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            result = await self.db.fetch_one(query)
            if result:
                return result["count"]
            return 0
        except Exception as e:
            raise RuntimeError(f"Failed to count records in {self.table_name}: {e}") from e

    async def exists(self, record_id: int) -> bool:
        """Check if a record exists by its ID.

        Args:
            record_id: Primary key value to check.

        Returns:
            True if record exists, False otherwise.
        """
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE id = ?"
            result = await self.db.fetch_one(query, (record_id,))
            return result is not None
        except Exception as e:
            raise RuntimeError(f"Failed to check existence in {self.table_name}: {e}") from e

    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find records by a specific field value.

        Args:
            field: Column name to search.
            value: Value to match.

        Returns:
            List of matching model instances.

        Raises:
            ValueError: If field name is empty.
        """
        if not field:
            raise ValueError("Field name must not be empty")

        try:
            query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
            rows = await self.db.fetch_all(query, (value,))
            return [self._row_to_model(row) for row in rows]
        except Exception as e:
            raise RuntimeError(f"Failed to find by field in {self.table_name}: {e}") from e

    async def find_one_by_field(self, field: str, value: Any) -> Optional[T]:
        """Find a single record by a specific field value.

        Args:
            field: Column name to search.
            value: Value to match.

        Returns:
            First matching model instance or None.

        Raises:
            ValueError: If field name is empty.
        """
        if not field:
            raise ValueError("Field name must not be empty")

        try:
            query = f"SELECT * FROM {self.table_name} WHERE {field} = ? LIMIT 1"
            row = await self.db.fetch_one(query, (value,))
            if row:
                return self._row_to_model(row)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to find one by field in {self.table_name}: {e}") from e