from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    """Represents a project entity with metadata and status information."""

    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    github_repo: Optional[str] = None
    github_url: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0

    def __post_init__(self) -> None:
        """Validate project data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")
        if self.stars < 0:
            raise ValueError("Stars count cannot be negative")
        if self.forks < 0:
            raise ValueError("Forks count cannot be negative")
        if self.created_at > self.updated_at:
            raise ValueError("Created date cannot be after updated date")

    @property
    def full_name(self) -> str:
        """Get the full project name with owner prefix if available."""
        if self.github_repo:
            return f"{self.owner_id}/{self.name}"
        return self.name

    @property
    def is_github_linked(self) -> bool:
        """Check if the project is linked to a GitHub repository."""
        return bool(self.github_repo and self.github_url)

    def to_dict(self) -> dict:
        """Convert project to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "github_repo": self.github_repo,
            "github_url": self.github_url,
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create a Project instance from a dictionary.

        Args:
            data: Dictionary containing project data.

        Returns:
            Project instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If date strings are invalid.
        """
        required_fields = ["id", "name", "description", "owner_id", "created_at", "updated_at"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Missing required field: {field}")

        created_at = data["created_at"]
        updated_at = data["updated_at"]

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            owner_id=data["owner_id"],
            created_at=created_at,
            updated_at=updated_at,
            is_active=data.get("is_active", True),
            github_repo=data.get("github_repo"),
            github_url=data.get("github_url"),
            language=data.get("language"),
            stars=data.get("stars", 0),
            forks=data.get("forks", 0),
        )