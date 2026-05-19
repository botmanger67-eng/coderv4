from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """Represents a user in the system.

    Attributes:
        id: Unique identifier for the user.
        telegram_id: Telegram user ID.
        username: Optional Telegram username.
        first_name: Optional first name.
        last_name: Optional last name.
        github_token: Optional GitHub personal access token.
        openai_api_key: Optional OpenAI API key.
        is_active: Whether the user account is active.
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
    """

    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    github_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if self.telegram_id <= 0:
            raise ValueError("telegram_id must be a positive integer")
        if self.id < 0:
            raise ValueError("id must be a non-negative integer")

    @property
    def full_name(self) -> str:
        """Get the full name of the user.

        Returns:
            Combined first and last name, or just first name if last name is None,
            or 'Unknown' if both are None.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return "Unknown"

    @property
    def display_name(self) -> str:
        """Get the display name for the user.

        Returns:
            Username if available, otherwise full name.
        """
        if self.username:
            return f"@{self.username}"
        return self.full_name

    def to_dict(self) -> dict:
        """Convert user to dictionary.

        Returns:
            Dictionary representation of the user.
        """
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "github_token": self.github_token,
            "openai_api_key": self.openai_api_key,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User instance from a dictionary.

        Args:
            data: Dictionary containing user data.

        Returns:
            User instance created from the dictionary.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If data validation fails.
        """
        required_fields = ["id", "telegram_id"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Missing required field: {field}")

        # Parse datetime strings if present
        created_at = None
        updated_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                created_at = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                updated_at = None

        return cls(
            id=data["id"],
            telegram_id=data["telegram_id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            github_token=data.get("github_token"),
            openai_api_key=data.get("openai_api_key"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at,
        )