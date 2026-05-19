from typing import Optional, Dict, Any
from src.services.ai_service import AIService
from src.services.github_service import GitHubService
from src.core.logger import logger
from src.models.project import Project, ProjectStatus, ProjectConfig


class ProjectService:
    """Service for managing project generation lifecycle."""

    def __init__(self, ai_service: AIService, github_service: GitHubService):
        self._ai_service = ai_service
        self._github_service = github_service

    async def create_project(self, config: ProjectConfig) -> Project:
        """Create a new project with AI-generated code and GitHub repository.

        Args:
            config: Project configuration including name, description, and tech stack.

        Returns:
            Project: The created project instance.

        Raises:
            ValueError: If project configuration is invalid.
            RuntimeError: If project creation fails.
        """
        logger.info(f"Creating project: {config.name}")
        project = Project(config=config)

        try:
            project.status = ProjectStatus.GENERATING_CODE
            code_content = await self._ai_service.generate_code(config)
            project.code_content = code_content

            project.status = ProjectStatus.CREATING_REPOSITORY
            repo_url = await self._github_service.create_repository(
                name=config.name,
                description=config.description,
                code_content=code_content
            )
            project.repository_url = repo_url

            project.status = ProjectStatus.COMPLETED
            logger.info(f"Project {config.name} created successfully at {repo_url}")
            return project

        except Exception as e:
            project.status = ProjectStatus.FAILED
            project.error_message = str(e)
            logger.error(f"Project creation failed: {e}")
            raise RuntimeError(f"Failed to create project: {e}") from e

    async def get_project_status(self, project_id: str) -> Optional[Project]:
        """Retrieve project status by ID.

        Args:
            project_id: Unique identifier for the project.

        Returns:
            Optional[Project]: Project if found, None otherwise.
        """
        logger.debug(f"Fetching project status: {project_id}")
        # Implementation would typically query a database
        # Placeholder for actual storage retrieval
        return None

    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        """Update an existing project's metadata.

        Args:
            project_id: Unique identifier for the project.
            updates: Dictionary of fields to update.

        Returns:
            Optional[Project]: Updated project if found, None otherwise.

        Raises:
            ValueError: If update data is invalid.
        """
        logger.info(f"Updating project: {project_id}")
        if not updates:
            raise ValueError("No updates provided")

        # Implementation would typically update database record
        # Placeholder for actual storage update
        return None

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and its associated resources.

        Args:
            project_id: Unique identifier for the project.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        logger.info(f"Deleting project: {project_id}")
        try:
            # Implementation would typically:
            # 1. Delete from database
            # 2. Optionally delete GitHub repository
            # 3. Clean up any associated resources
            return True
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            return False

    async def regenerate_code(self, project_id: str) -> Optional[Project]:
        """Regenerate code for an existing project.

        Args:
            project_id: Unique identifier for the project.

        Returns:
            Optional[Project]: Updated project with regenerated code, None if not found.

        Raises:
            RuntimeError: If code regeneration fails.
        """
        logger.info(f"Regenerating code for project: {project_id}")
        project = await self.get_project_status(project_id)
        if not project:
            logger.warning(f"Project {project_id} not found")
            return None

        try:
            project.status = ProjectStatus.GENERATING_CODE
            new_code = await self._ai_service.generate_code(project.config)
            project.code_content = new_code

            project.status = ProjectStatus.UPDATING_REPOSITORY
            await self._github_service.update_repository(
                repo_name=project.config.name,
                code_content=new_code
            )

            project.status = ProjectStatus.COMPLETED
            logger.info(f"Code regenerated for project {project_id}")
            return project

        except Exception as e:
            project.status = ProjectStatus.FAILED
            project.error_message = str(e)
            logger.error(f"Code regeneration failed for {project_id}: {e}")
            raise RuntimeError(f"Failed to regenerate code: {e}") from e