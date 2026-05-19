import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import get_db
from src.repositories.auth_repo import AuthRepository


def add_owner(username: str, db_path: Optional[str] = None) -> bool:
    """
    Add a user as an owner to the authorized users list.

    Args:
        username: GitHub username to add as owner
        db_path: Optional custom database path

    Returns:
        True if user was added successfully, False if already exists

    Raises:
        ValueError: If username is empty or invalid
        Exception: For database errors
    """
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")

    username = username.strip().lower()

    try:
        db = get_db(db_path)
        auth_repo = AuthRepository(db)

        if auth_repo.is_authorized(username):
            logger.info(f"User '{username}' is already authorized")
            return False

        auth_repo.add_authorized_user(username, is_owner=True)
        logger.success(f"Added '{username}' as owner")
        return True

    except Exception as e:
        logger.error(f"Failed to add owner '{username}': {e}")
        raise


def main() -> None:
    """CLI entry point for adding an owner."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/add_owner.py <github_username>")
        sys.exit(1)

    username = sys.argv[1]

    try:
        result = add_owner(username)
        if result:
            print(f"✓ Successfully added '{username}' as owner")
        else:
            print(f"ℹ '{username}' is already an authorized owner")
    except ValueError as e:
        print(f"✗ Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()