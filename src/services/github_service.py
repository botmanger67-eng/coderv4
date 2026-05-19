from typing import Optional
from github import Github, GithubIntegration, Auth
from github.Repository import Repository
from github.GithubException import GithubException, UnknownObjectException
from src.core.config import settings
from src.core.logger import logger


class GitHubService:
    """Service for interacting with GitHub API to create repositories and push code."""

    def __init__(self) -> None:
        """Initialize GitHub service with authentication from settings."""
        self._client: Optional[Github] = None
        self._app_client: Optional[GithubIntegration] = None
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize GitHub API clients based on available authentication methods."""
        try:
            if settings.GITHUB_APP_ID and settings.GITHUB_PRIVATE_KEY:
                auth = Auth.AppAuth(
                    app_id=settings.GITHUB_APP_ID,
                    private_key=settings.GITHUB_PRIVATE_KEY,
                )
                self._app_client = GithubIntegration(auth=auth)
                logger.info("GitHub App authentication initialized")
            elif settings.GITHUB_TOKEN:
                auth = Auth.Token(settings.GITHUB_TOKEN)
                self._client = Github(auth=auth)
                logger.info("GitHub token authentication initialized")
            else:
                self._client = Github()
                logger.warning("No GitHub authentication configured, using unauthenticated client")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub clients: {e}")
            raise

    def _get_client(self) -> Github:
        """Get or create a GitHub client instance.

        Returns:
            Github: Authenticated GitHub client instance.

        Raises:
            RuntimeError: If no authentication method is available.
        """
        if self._client:
            return self._client

        if self._app_client:
            try:
                installation_id = settings.GITHUB_INSTALLATION_ID
                if not installation_id:
                    raise RuntimeError("GitHub installation ID is required for App authentication")
                installation = self._app_client.get_installation(installation_id)
                self._client = installation.get_github_for_installation()
                return self._client
            except Exception as e:
                logger.error(f"Failed to get installation client: {e}")
                raise RuntimeError(f"Could not create authenticated client: {e}")

        raise RuntimeError("No GitHub authentication method available")

    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = False,
        organization: Optional[str] = None,
    ) -> Repository:
        """Create a new GitHub repository.

        Args:
            name: Repository name.
            description: Optional repository description.
            private: Whether the repository should be private.
            auto_init: Whether to initialize with a README.
            organization: Optional organization name to create repo under.

        Returns:
            Repository: The created repository object.

        Raises:
            GithubException: If repository creation fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            if organization:
                org = client.get_organization(organization)
                repo = org.create_repo(
                    name=name,
                    description=description or "",
                    private=private,
                    auto_init=auto_init,
                )
                logger.info(f"Created repository '{name}' under organization '{organization}'")
            else:
                user = client.get_user()
                repo = user.create_repo(
                    name=name,
                    description=description or "",
                    private=private,
                    auto_init=auto_init,
                )
                logger.info(f"Created repository '{name}' under user '{user.login}'")
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository '{name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating repository '{name}': {e}")
            raise

    def get_repository(self, repo_full_name: str) -> Repository:
        """Get an existing repository by full name.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').

        Returns:
            Repository: The repository object.

        Raises:
            UnknownObjectException: If repository does not exist.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            logger.info(f"Retrieved repository '{repo_full_name}'")
            return repo
        except UnknownObjectException:
            logger.error(f"Repository '{repo_full_name}' not found")
            raise
        except GithubException as e:
            logger.error(f"Failed to get repository '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting repository '{repo_full_name}': {e}")
            raise

    def delete_repository(self, repo_full_name: str) -> None:
        """Delete a GitHub repository.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').

        Raises:
            GithubException: If deletion fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            repo.delete()
            logger.info(f"Deleted repository '{repo_full_name}'")
        except GithubException as e:
            logger.error(f"Failed to delete repository '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting repository '{repo_full_name}': {e}")
            raise

    def push_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
    ) -> None:
        """Push a file to a repository.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').
            file_path: Path to the file in the repository.
            content: File content as string.
            commit_message: Commit message.
            branch: Branch to push to (default: 'main').

        Raises:
            GithubException: If push fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            try:
                contents = repo.get_contents(file_path, ref=branch)
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=contents.sha,
                    branch=branch,
                )
                logger.info(f"Updated file '{file_path}' in '{repo_full_name}' on branch '{branch}'")
            except UnknownObjectException:
                repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch,
                )
                logger.info(f"Created file '{file_path}' in '{repo_full_name}' on branch '{branch}'")
        except GithubException as e:
            logger.error(f"Failed to push file '{file_path}' to '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error pushing file '{file_path}' to '{repo_full_name}': {e}")
            raise

    def push_files(
        self,
        repo_full_name: str,
        files: dict[str, str],
        commit_message: str,
        branch: str = "main",
    ) -> None:
        """Push multiple files to a repository in a single commit.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').
            files: Dictionary mapping file paths to their content.
            commit_message: Commit message.
            branch: Branch to push to (default: 'main').

        Raises:
            GithubException: If push fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            ref = repo.get_git_ref(f"heads/{branch}")
            commit = repo.get_git_commit(ref.object.sha)
            tree = repo.get_git_tree(commit.tree.sha, recursive=True)

            elements = []
            for file_path, content in files.items():
                element = repo.create_git_blob(content, "utf-8")
                elements.append(
                    repo.create_git_tree_element(
                        path=file_path,
                        mode="100644",
                        type="blob",
                        sha=element.sha,
                    )
                )

            new_tree = repo.create_git_tree(elements, base_tree=tree)
            new_commit = repo.create_git_commit(commit_message, new_tree, [commit])
            ref.edit(new_commit.sha)

            logger.info(f"Pushed {len(files)} files to '{repo_full_name}' on branch '{branch}'")
        except GithubException as e:
            logger.error(f"Failed to push files to '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error pushing files to '{repo_full_name}': {e}")
            raise

    def create_branch(
        self,
        repo_full_name: str,
        branch_name: str,
        source_branch: str = "main",
    ) -> None:
        """Create a new branch in a repository.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').
            branch_name: Name of the new branch.
            source_branch: Source branch to create from (default: 'main').

        Raises:
            GithubException: If branch creation fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            ref = repo.get_git_ref(f"heads/{source_branch}")
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=ref.object.sha)
            logger.info(f"Created branch '{branch_name}' in '{repo_full_name}' from '{source_branch}'")
        except GithubException as e:
            logger.error(f"Failed to create branch '{branch_name}' in '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating branch '{branch_name}' in '{repo_full_name}': {e}")
            raise

    def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> None:
        """Create a pull request in a repository.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').
            title: Pull request title.
            body: Pull request body/description.
            head: Branch containing changes.
            base: Branch to merge into (default: 'main').

        Raises:
            GithubException: If pull request creation fails.
            RuntimeError: If authentication is not configured.
        """
        client = self._get_client()
        try:
            repo = client.get_repo(repo_full_name)
            repo.create_pull(title=title, body=body, head=head, base=base)
            logger.info(f"Created pull request '{title}' in '{repo_full_name}' from '{head}' to '{base}'")
        except GithubException as e:
            logger.error(f"Failed to create pull request in '{repo_full_name}': {e.data.get('message', str(e))}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating pull request in '{repo_full_name}': {e}")
            raise

    def check_repository_exists(self, repo_full_name: str) -> bool:
        """Check if a repository exists.

        Args:
            repo_full_name: Repository full name (e.g., 'owner/repo').

        Returns:
            bool: True if repository exists, False otherwise.
        """
        try:
            self.get_repository(repo_full_name)
            return True
        except UnknownObjectException:
            return False
        except Exception as e:
            logger.error(f"Error checking repository existence '{repo_full_name}': {e}")
            return False

    def close(self) -> None:
        """Close the GitHub client connection."""
        if self._client:
            self._client.close()
            logger.info("GitHub client connection closed")
        if self._app_client:
            self._app_client.close()
            logger.info("GitHub App client connection closed")

    def __enter__(self) -> "GitHubService":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup."""
        self.close()