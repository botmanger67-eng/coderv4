"""Initialize the database schema and create tables if they don't exist."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import DatabaseManager, DatabaseError


def init_database(db_path: Optional[str] = None) -> bool:
    """Initialize the database with required tables.

    Args:
        db_path: Optional path to database file. If None, uses default.

    Returns:
        True if initialization successful, False otherwise.

    Raises:
        DatabaseError: If database initialization fails critically.
    """
    try:
        logger.info("Starting database initialization")
        db_manager = DatabaseManager(db_path=db_path)
        db_manager.initialize()
        logger.success("Database initialized successfully")
        return True
    except DatabaseError as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise DatabaseError(f"Failed to initialize database: {e}") from e


def main() -> None:
    """Main entry point for database initialization script."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    try:
        success = init_database()
        if not success:
            logger.error("Database initialization returned False")
            sys.exit(1)
    except DatabaseError:
        logger.critical("Critical database initialization failure")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()