from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Session:
    """
    Represents a user session with authentication and state information.

    Attributes:
        user_id: Unique identifier for the user.
        access_token: OAuth or API access token for the user.
        refresh_token: Token used to refresh the access token when expired.
        token_expiry: Datetime when the current access token expires.
        state: Current state of the session (e.g., 'active', 'expired', 'revoked').
        created_at: Datetime when the session was created.
        updated_at: Datetime when the session was last updated.
    """

    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    state: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """
        Check if the session's access token has expired.

        Returns:
            True if the token has expired or token_expiry is not set, False otherwise.
        """
        if self.token_expiry is None:
            return True
        return datetime.utcnow() > self.token_expiry

    def is_active(self) -> bool:
        """
        Check if the session is currently active.

        Returns:
            True if the session state is 'active' and the token is not expired, False otherwise.
        """
        return self.state == "active" and not self.is_expired()

    def revoke(self) -> None:
        """
        Revoke the session by setting its state to 'revoked'.
        """
        self.state = "revoked"
        self.updated_at = datetime.utcnow()

    def refresh(self, new_access_token: str, new_refresh_token: Optional[str] = None,
                new_token_expiry: Optional[datetime] = None) -> None:
        """
        Refresh the session with new token information.

        Args:
            new_access_token: The new access token.
            new_refresh_token: Optional new refresh token.
            new_token_expiry: Optional new token expiry datetime.
        """
        self.access_token = new_access_token
        if new_refresh_token is not None:
            self.refresh_token = new_refresh_token
        if new_token_expiry is not None:
            self.token_expiry = new_token_expiry
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        Convert the session to a dictionary for serialization.

        Returns:
            Dictionary representation of the session.
        """
        return {
            "user_id": self.user_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """
        Create a Session instance from a dictionary.

        Args:
            data: Dictionary containing session data.

        Returns:
            A new Session instance.
        """
        return cls(
            user_id=data["user_id"],
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_expiry=datetime.fromisoformat(data["token_expiry"]) if data.get("token_expiry") else None,
            state=data.get("state", "active"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )