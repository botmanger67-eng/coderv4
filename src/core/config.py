import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        load_dotenv()
        self._validate()

    def _validate(self) -> None:
        """Ensure all required configuration values are present."""
        missing = [key for key in self._required_keys if not getattr(self, key, None)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    @property
    def _required_keys(self) -> list[str]:
        return [
            "telegram_token",
            "openai_api_key",
            "github_token",
            "database_path",
        ]

    @property
    def telegram_token(self) -> str:
        """Telegram bot token from TELEGRAM_TOKEN env var."""
        return os.getenv("TELEGRAM_TOKEN", "")

    @property
    def openai_api_key(self) -> str:
        """OpenAI API key from OPENAI_API_KEY env var."""
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def github_token(self) -> str:
        """GitHub personal access token from GITHUB_TOKEN env var."""
        return os.getenv("GITHUB_TOKEN", "")

    @property
    def database_path(self) -> Path:
        """Path to SQLite database file from DATABASE_PATH env var."""
        path = os.getenv("DATABASE_PATH", "data/app.db")
        return Path(path)

    @property
    def log_level(self) -> str:
        """Logging level from LOG_LEVEL env var (default: INFO)."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def openai_model(self) -> str:
        """OpenAI model name from OPENAI_MODEL env var (default: gpt-4)."""
        return os.getenv("OPENAI_MODEL", "gpt-4")

    @property
    def openai_max_tokens(self) -> int:
        """Maximum tokens for OpenAI responses from OPENAI_MAX_TOKENS env var (default: 1000)."""
        try:
            return int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        except ValueError:
            return 1000

    @property
    def openai_temperature(self) -> float:
        """Temperature for OpenAI responses from OPENAI_TEMPERATURE env var (default: 0.7)."""
        try:
            return float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        except ValueError:
            return 0.7

    @property
    def github_repo(self) -> Optional[str]:
        """GitHub repository in format owner/repo from GITHUB_REPO env var."""
        return os.getenv("GITHUB_REPO") or None

    @property
    def webhook_url(self) -> Optional[str]:
        """Telegram webhook URL from WEBHOOK_URL env var."""
        return os.getenv("WEBHOOK_URL") or None

    @property
    def webhook_port(self) -> int:
        """Port for webhook server from WEBHOOK_PORT env var (default: 8443)."""
        try:
            return int(os.getenv("WEBHOOK_PORT", "8443"))
        except ValueError:
            return 8443

    @property
    def database_pool_size(self) -> int:
        """Database connection pool size from DB_POOL_SIZE env var (default: 5)."""
        try:
            return int(os.getenv("DB_POOL_SIZE", "5"))
        except ValueError:
            return 5

    @property
    def database_timeout(self) -> float:
        """Database timeout in seconds from DB_TIMEOUT env var (default: 30.0)."""
        try:
            return float(os.getenv("DB_TIMEOUT", "30.0"))
        except ValueError:
            return 30.0

    @property
    def request_timeout(self) -> int:
        """HTTP request timeout in seconds from REQUEST_TIMEOUT env var (default: 30)."""
        try:
            return int(os.getenv("REQUEST_TIMEOUT", "30"))
        except ValueError:
            return 30

    @property
    def max_retries(self) -> int:
        """Maximum retry attempts for API calls from MAX_RETRIES env var (default: 3)."""
        try:
            return int(os.getenv("MAX_RETRIES", "3"))
        except ValueError:
            return 3

    @property
    def retry_delay(self) -> float:
        """Delay between retries in seconds from RETRY_DELAY env var (default: 1.0)."""
        try:
            return float(os.getenv("RETRY_DELAY", "1.0"))
        except ValueError:
            return 1.0

    @property
    def environment(self) -> str:
        """Environment name from ENVIRONMENT env var (default: development)."""
        return os.getenv("ENVIRONMENT", "development").lower()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"


config = Config()