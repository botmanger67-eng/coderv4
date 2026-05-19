import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.project_service import ProjectService


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = MagicMock()
    client.get_repo = AsyncMock()
    client.create_issue = AsyncMock()
    client.get_issues = AsyncMock()
    return client


@pytest.fixture
def project_service(mock_github_client):
    """Create a ProjectService instance with mocked dependencies."""
    return ProjectService(github_client=mock_github_client)


class TestProjectService:
    """Test suite for ProjectService."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_service, mock_github_client):
        """Test successful project creation."""
        repo_name = "test-repo"
        project_name = "Test Project"
        mock_repo = MagicMock()
        mock_repo.name = repo_name
        mock_github_client.get_repo.return_value = mock_repo

        result = await project_service.create_project(repo_name, project_name)

        assert result["status"] == "success"
        assert result["repo_name"] == repo_name
        assert result["project_name"] == project_name
        mock_github_client.get_repo.assert_called_once_with(repo_name)

    @pytest.mark.asyncio
    async def test_create_project_repo_not_found(self, project_service, mock_github_client):
        """Test project creation with non-existent repository."""
        mock_github_client.get_repo.side_effect = Exception("Repository not found")

        with pytest.raises(Exception, match="Repository not found"):
            await project_service.create_project("non-existent-repo", "Test Project")

    @pytest.mark.asyncio
    async def test_create_issue_success(self, project_service, mock_github_client):
        """Test successful issue creation."""
        repo_name = "test-repo"
        issue_title = "Test Issue"
        issue_body = "This is a test issue"
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = issue_title
        mock_github_client.create_issue.return_value = mock_issue

        result = await project_service.create_issue(repo_name, issue_title, issue_body)

        assert result["status"] == "success"
        assert result["issue_number"] == 1
        assert result["issue_title"] == issue_title
        mock_github_client.create_issue.assert_called_once_with(
            repo_name, issue_title, issue_body
        )

    @pytest.mark.asyncio
    async def test_create_issue_failure(self, project_service, mock_github_client):
        """Test issue creation failure."""
        mock_github_client.create_issue.side_effect = Exception("Failed to create issue")

        with pytest.raises(Exception, match="Failed to create issue"):
            await project_service.create_issue("test-repo", "Test Issue", "Body")

    @pytest.mark.asyncio
    async def test_get_issues_success(self, project_service, mock_github_client):
        """Test successful retrieval of issues."""
        repo_name = "test-repo"
        mock_issues = [
            MagicMock(number=1, title="Issue 1", state="open"),
            MagicMock(number=2, title="Issue 2", state="closed"),
        ]
        mock_github_client.get_issues.return_value = mock_issues

        result = await project_service.get_issues(repo_name)

        assert result["status"] == "success"
        assert len(result["issues"]) == 2
        assert result["issues"][0]["number"] == 1
        assert result["issues"][1]["state"] == "closed"
        mock_github_client.get_issues.assert_called_once_with(repo_name)

    @pytest.mark.asyncio
    async def test_get_issues_empty(self, project_service, mock_github_client):
        """Test retrieval of issues when none exist."""
        mock_github_client.get_issues.return_value = []

        result = await project_service.get_issues("test-repo")

        assert result["status"] == "success"
        assert len(result["issues"]) == 0

    @pytest.mark.asyncio
    async def test_get_issues_failure(self, project_service, mock_github_client):
        """Test issue retrieval failure."""
        mock_github_client.get_issues.side_effect = Exception("Failed to fetch issues")

        with pytest.raises(Exception, match="Failed to fetch issues"):
            await project_service.get_issues("test-repo")

    @pytest.mark.asyncio
    async def test_update_issue_success(self, project_service, mock_github_client):
        """Test successful issue update."""
        repo_name = "test-repo"
        issue_number = 1
        update_data = {"title": "Updated Title", "state": "closed"}
        mock_issue = MagicMock()
        mock_issue.number = issue_number
        mock_github_client.update_issue = AsyncMock(return_value=mock_issue)

        result = await project_service.update_issue(repo_name, issue_number, update_data)

        assert result["status"] == "success"
        assert result["issue_number"] == issue_number
        mock_github_client.update_issue.assert_called_once_with(
            repo_name, issue_number, **update_data
        )

    @pytest.mark.asyncio
    async def test_update_issue_failure(self, project_service, mock_github_client):
        """Test issue update failure."""
        mock_github_client.update_issue = AsyncMock(
            side_effect=Exception("Failed to update issue")
        )

        with pytest.raises(Exception, match="Failed to update issue"):
            await project_service.update_issue("test-repo", 1, {"title": "New Title"})

    @pytest.mark.asyncio
    async def test_delete_issue_success(self, project_service, mock_github_client):
        """Test successful issue deletion."""
        repo_name = "test-repo"
        issue_number = 1
        mock_github_client.delete_issue = AsyncMock(return_value=True)

        result = await project_service.delete_issue(repo_name, issue_number)

        assert result["status"] == "success"
        assert result["issue_number"] == issue_number
        mock_github_client.delete_issue.assert_called_once_with(repo_name, issue_number)

    @pytest.mark.asyncio
    async def test_delete_issue_failure(self, project_service, mock_github_client):
        """Test issue deletion failure."""
        mock_github_client.delete_issue = AsyncMock(
            side_effect=Exception("Failed to delete issue")
        )

        with pytest.raises(Exception, match="Failed to delete issue"):
            await project_service.delete_issue("test-repo", 1)

    @pytest.mark.asyncio
    async def test_get_project_details_success(self, project_service, mock_github_client):
        """Test successful retrieval of project details."""
        repo_name = "test-repo"
        mock_repo = MagicMock()
        mock_repo.name = repo_name
        mock_repo.description = "Test repository"
        mock_repo.html_url = f"https://github.com/test/{repo_name}"
        mock_github_client.get_repo.return_value = mock_repo

        result = await project_service.get_project_details(repo_name)

        assert result["status"] == "success"
        assert result["name"] == repo_name
        assert result["description"] == "Test repository"
        assert result["url"] == f"https://github.com/test/{repo_name}"
        mock_github_client.get_repo.assert_called_once_with(repo_name)

    @pytest.mark.asyncio
    async def test_get_project_details_failure(self, project_service, mock_github_client):
        """Test project details retrieval failure."""
        mock_github_client.get_repo.side_effect = Exception("Repository not accessible")

        with pytest.raises(Exception, match="Repository not accessible"):
            await project_service.get_project_details("test-repo")

    @pytest.mark.asyncio
    async def test_list_projects_success(self, project_service, mock_github_client):
        """Test successful listing of projects."""
        mock_repos = [
            MagicMock(name="repo1", description="First repo"),
            MagicMock(name="repo2", description="Second repo"),
        ]
        mock_github_client.get_user_repos = AsyncMock(return_value=mock_repos)

        result = await project_service.list_projects()

        assert result["status"] == "success"
        assert len(result["projects"]) == 2
        assert result["projects"][0]["name"] == "repo1"
        assert result["projects"][1]["description"] == "Second repo"

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, project_service, mock_github_client):
        """Test listing projects when none exist."""
        mock_github_client.get_user_repos = AsyncMock(return_value=[])

        result = await project_service.list_projects()

        assert result["status"] == "success"
        assert len(result["projects"]) == 0

    @pytest.mark.asyncio
    async def test_list_projects_failure(self, project_service, mock_github_client):
        """Test project listing failure."""
        mock_github_client.get_user_repos = AsyncMock(
            side_effect=Exception("Failed to list repositories")
        )

        with pytest.raises(Exception, match="Failed to list repositories"):
            await project_service.list_projects()