from typing import Optional
from src.repositories.auth_repo import AuthRepository
from src.core.config import settings
from loguru import logger


class AuthService:
    """
    Service layer for authorization logic.
    Handles token validation, user authentication, and permission checks.
    """

    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo
        self._token_cache: dict[str, dict] = {}

    async def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate an authentication token.

        Args:
            token: The token string to validate.

        Returns:
            User data dict if token is valid, None otherwise.
        """
        if not token or not isinstance(token, str):
            logger.warning("Invalid token format provided")
            return None

        # Check cache first
        if token in self._token_cache:
            cached = self._token_cache[token]
            if cached.get("expires_at", 0) > settings.get_current_timestamp():
                logger.debug("Token validated from cache")
                return cached.get("user_data")
            else:
                # Expired cache entry
                del self._token_cache[token]

        try:
            user_data = await self.auth_repo.get_user_by_token(token)
            if user_data:
                # Cache the result
                self._token_cache[token] = {
                    "user_data": user_data,
                    "expires_at": settings.get_current_timestamp() + settings.TOKEN_CACHE_TTL,
                }
                logger.info(f"Token validated for user: {user_data.get('username', 'unknown')}")
                return user_data
            else:
                logger.warning("Token validation failed: token not found")
                return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None

    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username.
            password: The password.

        Returns:
            User data dict with token on success, None on failure.
        """
        if not username or not password:
            logger.warning("Authentication attempt with empty credentials")
            return None

        try:
            user_data = await self.auth_repo.authenticate(username, password)
            if user_data:
                logger.info(f"User authenticated: {username}")
                return user_data
            else:
                logger.warning(f"Authentication failed for user: {username}")
                return None
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None

    async def check_permission(self, user_id: int, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user_id: The user ID.
            permission: The permission string to check.

        Returns:
            True if user has permission, False otherwise.
        """
        if not user_id or not permission:
            logger.warning("Permission check with invalid parameters")
            return False

        try:
            has_permission = await self.auth_repo.user_has_permission(user_id, permission)
            if has_permission:
                logger.debug(f"User {user_id} has permission: {permission}")
                return True
            else:
                logger.debug(f"User {user_id} lacks permission: {permission}")
                return False
        except Exception as e:
            logger.error(f"Error checking permission for user {user_id}: {e}")
            return False

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.

        Args:
            token: The token to revoke.

        Returns:
            True if token was revoked, False otherwise.
        """
        if not token:
            logger.warning("Revoke token called with empty token")
            return False

        # Remove from cache
        self._token_cache.pop(token, None)

        try:
            success = await self.auth_repo.revoke_token(token)
            if success:
                logger.info(f"Token revoked successfully")
                return True
            else:
                logger.warning("Token revocation failed")
                return False
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    async def create_token(self, user_id: int) -> Optional[str]:
        """
        Create a new authentication token for a user.

        Args:
            user_id: The user ID to create token for.

        Returns:
            The new token string, or None on failure.
        """
        if not user_id:
            logger.warning("Create token called with invalid user ID")
            return None

        try:
            token = await self.auth_repo.create_token(user_id)
            if token:
                logger.info(f"Token created for user {user_id}")
                return token
            else:
                logger.error(f"Failed to create token for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error creating token for user {user_id}: {e}")
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Get user data by user ID.

        Args:
            user_id: The user ID.

        Returns:
            User data dict if found, None otherwise.
        """
        if not user_id:
            logger.warning("Get user by ID called with invalid ID")
            return None

        try:
            user_data = await self.auth_repo.get_user_by_id(user_id)
            if user_data:
                return user_data
            else:
                logger.debug(f"User not found: {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """
        Get user data by Telegram ID.

        Args:
            telegram_id: The Telegram user ID.

        Returns:
            User data dict if found, None otherwise.
        """
        if not telegram_id:
            logger.warning("Get user by Telegram ID called with invalid ID")
            return None

        try:
            user_data = await self.auth_repo.get_user_by_telegram_id(telegram_id)
            if user_data:
                return user_data
            else:
                logger.debug(f"User not found for Telegram ID: {telegram_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user by Telegram ID {telegram_id}: {e}")
            return None

    async def register_user(self, username: str, password: str, telegram_id: Optional[int] = None) -> Optional[dict]:
        """
        Register a new user.

        Args:
            username: The username.
            password: The password.
            telegram_id: Optional Telegram ID to link.

        Returns:
            User data dict on success, None on failure.
        """
        if not username or not password:
            logger.warning("Registration attempt with empty credentials")
            return None

        try:
            user_data = await self.auth_repo.create_user(username, password, telegram_id)
            if user_data:
                logger.info(f"User registered: {username}")
                return user_data
            else:
                logger.warning(f"Registration failed for user: {username}")
                return None
        except Exception as e:
            logger.error(f"Error registering user {username}: {e}")
            return None

    async def update_user_telegram_id(self, user_id: int, telegram_id: int) -> bool:
        """
        Update the Telegram ID for a user.

        Args:
            user_id: The user ID.
            telegram_id: The new Telegram ID.

        Returns:
            True if updated, False otherwise.
        """
        if not user_id or not telegram_id:
            logger.warning("Update Telegram ID with invalid parameters")
            return False

        try:
            success = await self.auth_repo.update_telegram_id(user_id, telegram_id)
            if success:
                logger.info(f"Telegram ID updated for user {user_id}")
                return True
            else:
                logger.warning(f"Failed to update Telegram ID for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating Telegram ID for user {user_id}: {e}")
            return False

    def clear_token_cache(self) -> None:
        """Clear the token cache."""
        self._token_cache.clear()
        logger.debug("Token cache cleared")