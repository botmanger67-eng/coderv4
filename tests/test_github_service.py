"""Tests for the GitHub service module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from github import GithubException, UnknownObjectException

from src.services.github_service import GitHubService


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    with patch("src.services.github_service.Github") as mock:
        yield mock


@pytest.fixture
def github_service(mock_github_client):
    """Create a GitHubService instance with mocked client."""
    service = GitHubService(token="test_token")
    service.client = mock_github_client.return_value
    return service


class TestGitHubService:
    """Test suite for GitHubService."""

    def test_init_success(self, mock_github_client):
        """Test successful initialization of GitHubService."""
        service = GitHubService(token="test_token")
        mock_github_client.assert_called_once_with("test_token")
        assert service.client is not None

    def test_init_without_token(self):
        """Test initialization without token raises error."""
        with pytest.raises(ValueError, match="GitHub token is required"):
            GitHubService(token="")

    def test_get_repo_success(self, github_service):
        """Test successful repository retrieval."""
        mock_repo = MagicMock()
        github_service.client.get_repo.return_value = mock_repo

        result = github_service.get_repo("owner/repo")

        github_service.client.get_repo.assert_called_once_with("owner/repo")
        assert result == mock_repo

    def test_get_repo_not_found(self, github_service):
        """Test repository not found raises error."""
        github_service.client.get_repo.side_effect = UnknownObjectException(
            404, "Not Found"
        )

        with pytest.raises(ValueError, match="Repository owner/repo not found"):
            github_service.get_repo("owner/repo")

    def test_get_repo_api_error(self, github_service):
        """Test API error during repository retrieval."""
        github_service.client.get_repo.side_effect = GithubException(
            500, "Internal Server Error"
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            github_service.get_repo("owner/repo")

    @pytest.mark.asyncio
    async def test_get_repo_async_success(self, github_service):
        """Test successful async repository retrieval."""
        mock_repo = MagicMock()
        github_service.client.get_repo = AsyncMock(return_value=mock_repo)

        result = await github_service.get_repo_async("owner/repo")

        github_service.client.get_repo.assert_called_once_with("owner/repo")
        assert result == mock_repo

    @pytest.mark.asyncio
    async def test_get_repo_async_not_found(self, github_service):
        """Test async repository not found raises error."""
        github_service.client.get_repo = AsyncMock(
            side_effect=UnknownObjectException(404, "Not Found")
        )

        with pytest.raises(ValueError, match="Repository owner/repo not found"):
            await github_service.get_repo_async("owner/repo")

    @pytest.mark.asyncio
    async def test_get_repo_async_api_error(self, github_service):
        """Test async API error during repository retrieval."""
        github_service.client.get_repo = AsyncMock(
            side_effect=GithubException(500, "Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            await github_service.get_repo_async("owner/repo")

    def test_get_file_content_success(self, github_service):
        """Test successful file content retrieval."""
        mock_repo = MagicMock()
        mock_content = MagicMock()
        mock_content.decoded_content = b"file content"
        mock_repo.get_contents.return_value = mock_content

        result = github_service.get_file_content(mock_repo, "path/to/file.py")

        mock_repo.get_contents.assert_called_once_with("path/to/file.py")
        assert result == "file content"

    def test_get_file_content_not_found(self, github_service):
        """Test file not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = UnknownObjectException(
            404, "Not Found"
        )

        with pytest.raises(
            ValueError, match="File path/to/file.py not found in repository"
        ):
            github_service.get_file_content(mock_repo, "path/to/file.py")

    def test_get_file_content_api_error(self, github_service):
        """Test API error during file content retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = GithubException(
            500, "Internal Server Error"
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            github_service.get_file_content(mock_repo, "path/to/file.py")

    @pytest.mark.asyncio
    async def test_get_file_content_async_success(self, github_service):
        """Test successful async file content retrieval."""
        mock_repo = MagicMock()
        mock_content = MagicMock()
        mock_content.decoded_content = b"file content"
        mock_repo.get_contents = AsyncMock(return_value=mock_content)

        result = await github_service.get_file_content_async(
            mock_repo, "path/to/file.py"
        )

        mock_repo.get_contents.assert_called_once_with("path/to/file.py")
        assert result == "file content"

    @pytest.mark.asyncio
    async def test_get_file_content_async_not_found(self, github_service):
        """Test async file not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_contents = AsyncMock(
            side_effect=UnknownObjectException(404, "Not Found")
        )

        with pytest.raises(
            ValueError, match="File path/to/file.py not found in repository"
        ):
            await github_service.get_file_content_async(
                mock_repo, "path/to/file.py"
            )

    @pytest.mark.asyncio
    async def test_get_file_content_async_api_error(self, github_service):
        """Test async API error during file content retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_contents = AsyncMock(
            side_effect=GithubException(500, "Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            await github_service.get_file_content_async(
                mock_repo, "path/to/file.py"
            )

    def test_get_repo_structure_success(self, github_service):
        """Test successful repository structure retrieval."""
        mock_repo = MagicMock()
        mock_file = MagicMock()
        mock_file.type = "file"
        mock_file.path = "src/main.py"
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = "src"
        mock_repo.get_contents.return_value = [mock_file, mock_dir]

        result = github_service.get_repo_structure(mock_repo, "src")

        mock_repo.get_contents.assert_called_once_with("src")
        assert result == [
            {"type": "file", "path": "src/main.py"},
            {"type": "dir", "path": "src"},
        ]

    def test_get_repo_structure_not_found(self, github_service):
        """Test repository structure not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = UnknownObjectException(
            404, "Not Found"
        )

        with pytest.raises(
            ValueError, match="Path src not found in repository"
        ):
            github_service.get_repo_structure(mock_repo, "src")

    def test_get_repo_structure_api_error(self, github_service):
        """Test API error during repository structure retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = GithubException(
            500, "Internal Server Error"
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            github_service.get_repo_structure(mock_repo, "src")

    @pytest.mark.asyncio
    async def test_get_repo_structure_async_success(self, github_service):
        """Test successful async repository structure retrieval."""
        mock_repo = MagicMock()
        mock_file = MagicMock()
        mock_file.type = "file"
        mock_file.path = "src/main.py"
        mock_dir = MagicMock()
        mock_dir.type = "dir"
        mock_dir.path = "src"
        mock_repo.get_contents = AsyncMock(return_value=[mock_file, mock_dir])

        result = await github_service.get_repo_structure_async(
            mock_repo, "src"
        )

        mock_repo.get_contents.assert_called_once_with("src")
        assert result == [
            {"type": "file", "path": "src/main.py"},
            {"type": "dir", "path": "src"},
        ]

    @pytest.mark.asyncio
    async def test_get_repo_structure_async_not_found(self, github_service):
        """Test async repository structure not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_contents = AsyncMock(
            side_effect=UnknownObjectException(404, "Not Found")
        )

        with pytest.raises(
            ValueError, match="Path src not found in repository"
        ):
            await github_service.get_repo_structure_async(mock_repo, "src")

    @pytest.mark.asyncio
    async def test_get_repo_structure_async_api_error(self, github_service):
        """Test async API error during repository structure retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_contents = AsyncMock(
            side_effect=GithubException(500, "Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            await github_service.get_repo_structure_async(mock_repo, "src")

    def test_create_issue_success(self, github_service):
        """Test successful issue creation."""
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_repo.create_issue.return_value = mock_issue

        result = github_service.create_issue(
            mock_repo, "Test Issue", "Issue body"
        )

        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue", body="Issue body"
        )
        assert result == mock_issue

    def test_create_issue_api_error(self, github_service):
        """Test API error during issue creation."""
        mock_repo = MagicMock()
        mock_repo.create_issue.side_effect = GithubException(
            500, "Internal Server Error"
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            github_service.create_issue(mock_repo, "Test Issue", "Issue body")

    @pytest.mark.asyncio
    async def test_create_issue_async_success(self, github_service):
        """Test successful async issue creation."""
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_repo.create_issue = AsyncMock(return_value=mock_issue)

        result = await github_service.create_issue_async(
            mock_repo, "Test Issue", "Issue body"
        )

        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue", body="Issue body"
        )
        assert result == mock_issue

    @pytest.mark.asyncio
    async def test_create_issue_async_api_error(self, github_service):
        """Test async API error during issue creation."""
        mock_repo = MagicMock()
        mock_repo.create_issue = AsyncMock(
            side_effect=GithubException(500, "Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            await github_service.create_issue_async(
                mock_repo, "Test Issue", "Issue body"
            )

    def test_get_issue_success(self, github_service):
        """Test successful issue retrieval."""
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_repo.get_issue.return_value = mock_issue

        result = github_service.get_issue(mock_repo, 1)

        mock_repo.get_issue.assert_called_once_with(1)
        assert result == mock_issue

    def test_get_issue_not_found(self, github_service):
        """Test issue not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_issue.side_effect = UnknownObjectException(
            404, "Not Found"
        )

        with pytest.raises(ValueError, match="Issue 1 not found"):
            github_service.get_issue(mock_repo, 1)

    def test_get_issue_api_error(self, github_service):
        """Test API error during issue retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_issue.side_effect = GithubException(
            500, "Internal Server Error"
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            github_service.get_issue(mock_repo, 1)

    @pytest.mark.asyncio
    async def test_get_issue_async_success(self, github_service):
        """Test successful async issue retrieval."""
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_repo.get_issue = AsyncMock(return_value=mock_issue)

        result = await github_service.get_issue_async(mock_repo, 1)

        mock_repo.get_issue.assert_called_once_with(1)
        assert result == mock_issue

    @pytest.mark.asyncio
    async def test_get_issue_async_not_found(self, github_service):
        """Test async issue not found raises error."""
        mock_repo = MagicMock()
        mock_repo.get_issue = AsyncMock(
            side_effect=UnknownObjectException(404, "Not Found")
        )

        with pytest.raises(ValueError, match="Issue 1 not found"):
            await github_service.get_issue_async(mock_repo, 1)

    @pytest.mark.asyncio
    async def test_get_issue_async_api_error(self, github_service):
        """Test async API error during issue retrieval."""
        mock_repo = MagicMock()
        mock_repo.get_issue = AsyncMock(
            side_effect=GithubException(500, "Internal Server Error")
        )

        with pytest.raises(RuntimeError, match="GitHub API error"):
            await github_service.get_issue_async(mock_repo, 1)