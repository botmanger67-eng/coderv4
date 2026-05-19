"""Core package initialization for the Telegram bot application."""

from typing import Optional
from pathlib import Path
import os

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"No .env file found at {env_path}")


def get_env_variable(key: str, default: Optional[str] = None) -> str:
    """Retrieve an environment variable or raise an error if missing.

    Args:
        key: The environment variable name.
        default: Optional default value if the variable is not set.

    Returns:
        The value of the environment variable.

    Raises:
        ValueError: If the variable is not set and no default is provided.
    """
    value = os.getenv(key, default)
    if value is None:
        error_msg = f"Missing required environment variable: {key}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return value


# Application configuration
BOT_TOKEN: str = get_env_variable("BOT_TOKEN")
OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")
GITHUB_TOKEN: str = get_env_variable("GITHUB_TOKEN")
DATABASE_PATH: str = get_env_variable("DATABASE_PATH", "data/bot.db")

# Ensure data directory exists
data_dir = Path(DATABASE_PATH).parent
data_dir.mkdir(parents=True, exist_ok=True)

logger.info("Core package initialized successfully")