from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AuthorizedUser:
    """
    Represents an authorized user with their GitHub and Telegram identifiers.

    Attributes:
        github_username: The GitHub username of the authorized user.
        telegram_user_id: The Telegram user ID of the authorized user.
        telegram_username: The optional Telegram username of the authorized user.
    """

    github_username: str
    telegram_user_id: int
    telegram_username: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the AuthorizedUser fields after initialization."""
        if not self.github_username or not self.github_username.strip():
            raise ValueError("github_username must be a non-empty string")
        if self.telegram_user_id <= 0:
            raise ValueError("telegram_user_id must be a positive integer")
        if self.telegram_username is not None and not self.telegram_username.strip():
            raise ValueError("telegram_username must be a non-empty string if provided")