import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    """Fixture providing an AuthService instance with mocked dependencies."""
    service = AuthService()
    service.github_client = MagicMock()
    service.github_client.get_user = AsyncMock()
    service.github_client.get_installation = AsyncMock()
    return service


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service):
        """Test successful user authentication."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.id = 12345
        auth_service.github_client.get_user.return_value = mock_user

        result = await auth_service.authenticate_user("valid_token")
        assert result is True
        auth_service.github_client.get_user.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, auth_service):
        """Test user authentication failure with invalid token."""
        auth_service.github_client.get_user.side_effect = Exception("Invalid token")

        result = await auth_service.authenticate_user("invalid_token")
        assert result is False
        auth_service.github_client.get_user.assert_called_once_with("invalid_token")

    @pytest.mark.asyncio
    async def test_authenticate_installation_success(self, auth_service):
        """Test successful installation authentication."""
        mock_installation = MagicMock()
        mock_installation.id = 67890
        auth_service.github_client.get_installation.return_value = mock_installation

        result = await auth_service.authenticate_installation(67890)
        assert result is True
        auth_service.github_client.get_installation.assert_called_once_with(67890)

    @pytest.mark.asyncio
    async def test_authenticate_installation_failure(self, auth_service):
        """Test installation authentication failure."""
        auth_service.github_client.get_installation.side_effect = Exception("Installation not found")

        result = await auth_service.authenticate_installation(99999)
        assert result is False
        auth_service.github_client.get_installation.assert_called_once_with(99999)

    @pytest.mark.asyncio
    async def test_authenticate_user_with_empty_token(self, auth_service):
        """Test authentication with empty token."""
        result = await auth_service.authenticate_user("")
        assert result is False
        auth_service.github_client.get_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_user_with_none_token(self, auth_service):
        """Test authentication with None token."""
        result = await auth_service.authenticate_user(None)
        assert result is False
        auth_service.github_client.get_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_installation_with_invalid_id(self, auth_service):
        """Test installation authentication with invalid ID."""
        result = await auth_service.authenticate_installation(-1)
        assert result is False
        auth_service.github_client.get_installation.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_installation_with_none_id(self, auth_service):
        """Test installation authentication with None ID."""
        result = await auth_service.authenticate_installation(None)
        assert result is False
        auth_service.github_client.get_installation.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_github_token_format(self, auth_service):
        """Test GitHub token format validation."""
        valid_tokens = [
            "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        ]
        invalid_tokens = [
            "",
            "invalid",
            "token_without_prefix",
            "ghp_short",
        ]

        for token in valid_tokens:
            assert auth_service._validate_token_format(token) is True

        for token in invalid_tokens:
            assert auth_service._validate_token_format(token) is False

    @pytest.mark.asyncio
    async def test_authenticate_user_with_network_error(self, auth_service):
        """Test authentication with network error."""
        auth_service.github_client.get_user.side_effect = ConnectionError("Network error")

        result = await auth_service.authenticate_user("valid_token")
        assert result is False
        auth_service.github_client.get_user.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_authenticate_installation_with_network_error(self, auth_service):
        """Test installation authentication with network error."""
        auth_service.github_client.get_installation.side_effect = ConnectionError("Network error")

        result = await auth_service.authenticate_installation(12345)
        assert result is False
        auth_service.github_client.get_installation.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_authenticate_user_returns_user_data(self, auth_service):
        """Test that authenticate_user returns user data on success."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.id = 12345
        mock_user.avatar_url = "https://avatars.githubusercontent.com/u/12345"
        auth_service.github_client.get_user.return_value = mock_user

        result = await auth_service.authenticate_user("valid_token", return_data=True)
        assert result is not False
        assert result["login"] == "testuser"
        assert result["id"] == 12345
        assert result["avatar_url"] == "https://avatars.githubusercontent.com/u/12345"

    @pytest.mark.asyncio
    async def test_authenticate_user_returns_false_on_failure_with_data(self, auth_service):
        """Test that authenticate_user returns False on failure even with return_data flag."""
        auth_service.github_client.get_user.side_effect = Exception("Invalid token")

        result = await auth_service.authenticate_user("invalid_token", return_data=True)
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_installation_returns_data(self, auth_service):
        """Test that authenticate_installation returns installation data on success."""
        mock_installation = MagicMock()
        mock_installation.id = 67890
        mock_installation.account.login = "testorg"
        auth_service.github_client.get_installation.return_value = mock_installation

        result = await auth_service.authenticate_installation(67890, return_data=True)
        assert result is not False
        assert result["id"] == 67890
        assert result["account"]["login"] == "testorg"

    @pytest.mark.asyncio
    async def test_authenticate_installation_returns_false_on_failure_with_data(self, auth_service):
        """Test that authenticate_installation returns False on failure even with return_data flag."""
        auth_service.github_client.get_installation.side_effect = Exception("Installation not found")

        result = await auth_service.authenticate_installation(99999, return_data=True)
        assert result is False