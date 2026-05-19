from typing import Optional
from datetime import datetime, timedelta
import hashlib
import secrets
from loguru import logger

from src.core.database import Database
from src.models.authorized_user import AuthorizedUser


class AuthError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidTokenError(AuthError):
    """Raised when token is invalid or expired."""
    pass


class UnauthorizedUserError(AuthError):
    """Raised when user is not authorized."""
    pass


class AuthManager:
    """Manages authorization and token generation for users."""

    def __init__(self, database: Database, token_expiry_days: int = 30) -> None:
        """Initialize AuthManager.

        Args:
            database: Database instance for user storage.
            token_expiry_days: Number of days until token expires.

        Raises:
            ValueError: If token_expiry_days is less than 1.
        """
        if token_expiry_days < 1:
            raise ValueError("token_expiry_days must be at least 1")

        self._database = database
        self._token_expiry_days = token_expiry_days
        logger.info("AuthManager initialized with token expiry of {} days", token_expiry_days)

    def _generate_token(self) -> str:
        """Generate a secure random token.

        Returns:
            A hex string token.
        """
        return secrets.token_hex(32)

    def _hash_token(self, token: str) -> str:
        """Hash a token using SHA-256.

        Args:
            token: The token to hash.

        Returns:
            Hashed token string.
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def create_authorized_user(self, telegram_id: int, username: Optional[str] = None) -> AuthorizedUser:
        """Create a new authorized user with a token.

        Args:
            telegram_id: Telegram user ID.
            username: Optional Telegram username.

        Returns:
            AuthorizedUser instance with generated token.

        Raises:
            AuthError: If user creation fails.
        """
        try:
            token = self._generate_token()
            hashed_token = self._hash_token(token)
            expires_at = datetime.utcnow() + timedelta(days=self._token_expiry_days)

            user = AuthorizedUser(
                telegram_id=telegram_id,
                username=username,
                token_hash=hashed_token,
                expires_at=expires_at,
                is_active=True
            )

            self._database.save_authorized_user(user)
            user.token = token  # Set raw token for return
            logger.info("Created authorized user: telegram_id={}", telegram_id)
            return user

        except Exception as e:
            logger.error("Failed to create authorized user: {}", e)
            raise AuthError(f"Failed to create authorized user: {e}") from e

    def validate_token(self, token: str) -> AuthorizedUser:
        """Validate a token and return the associated user.

        Args:
            token: The token to validate.

        Returns:
            AuthorizedUser if token is valid.

        Raises:
            InvalidTokenError: If token is invalid or expired.
            UnauthorizedUserError: If user is not authorized.
        """
        if not token:
            raise InvalidTokenError("Token is empty")

        hashed_token = self._hash_token(token)
        user = self._database.get_authorized_user_by_token_hash(hashed_token)

        if user is None:
            raise InvalidTokenError("Token not found")

        if not user.is_active:
            raise UnauthorizedUserError("User is deactivated")

        if user.expires_at and user.expires_at < datetime.utcnow():
            raise InvalidTokenError("Token has expired")

        logger.debug("Token validated for telegram_id={}", user.telegram_id)
        return user

    def revoke_user_token(self, telegram_id: int) -> None:
        """Revoke a user's authorization.

        Args:
            telegram_id: Telegram user ID.

        Raises:
            AuthError: If revocation fails.
        """
        try:
            user = self._database.get_authorized_user(telegram_id)
            if user is None:
                logger.warning("User not found for revocation: telegram_id={}", telegram_id)
                return

            user.is_active = False
            user.expires_at = datetime.utcnow()
            self._database.save_authorized_user(user)
            logger.info("Revoked authorization for telegram_id={}", telegram_id)

        except Exception as e:
            logger.error("Failed to revoke user token: {}", e)
            raise AuthError(f"Failed to revoke user token: {e}") from e

    def refresh_token(self, telegram_id: int) -> AuthorizedUser:
        """Refresh a user's token.

        Args:
            telegram_id: Telegram user ID.

        Returns:
            AuthorizedUser with new token.

        Raises:
            UnauthorizedUserError: If user is not found or deactivated.
            AuthError: If token refresh fails.
        """
        user = self._database.get_authorized_user(telegram_id)

        if user is None:
            raise UnauthorizedUserError(f"User not found: telegram_id={telegram_id}")

        if not user.is_active:
            raise UnauthorizedUserError(f"User is deactivated: telegram_id={telegram_id}")

        try:
            new_token = self._generate_token()
            hashed_token = self._hash_token(new_token)
            user.token_hash = hashed_token
            user.expires_at = datetime.utcnow() + timedelta(days=self._token_expiry_days)
            self._database.save_authorized_user(user)
            user.token = new_token
            logger.info("Refreshed token for telegram_id={}", telegram_id)
            return user

        except Exception as e:
            logger.error("Failed to refresh token: {}", e)
            raise AuthError(f"Failed to refresh token: {e}") from e

    def is_authorized(self, telegram_id: int) -> bool:
        """Check if a user is authorized.

        Args:
            telegram_id: Telegram user ID.

        Returns:
            True if user is authorized and active, False otherwise.
        """
        try:
            user = self._database.get_authorized_user(telegram_id)
            if user is None:
                return False
            return user.is_active and (user.expires_at is None or user.expires_at >= datetime.utcnow())

        except Exception as e:
            logger.error("Error checking authorization: {}", e)
            return False