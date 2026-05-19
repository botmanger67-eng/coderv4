import pytest
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.database import Database


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database file path for testing."""
    return tmp_path / "test_database.db"


@pytest.fixture
def database(temp_db_path: Path) -> Database:
    """Create a Database instance with a temporary file for testing."""
    db = Database(db_path=str(temp_db_path))
    db.initialize()
    yield db
    db.close()
    if temp_db_path.exists():
        temp_db_path.unlink()


@pytest.fixture
def mock_telegram_update() -> MagicMock:
    """Create a mock Telegram update object."""
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_chat.id = 67890
    update.message.text = "/start"
    update.message.chat.id = 67890
    return update


@pytest.fixture
def mock_telegram_context() -> MagicMock:
    """Create a mock Telegram context object."""
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_document = AsyncMock()
    context.user_data = {}
    context.chat_data = {}
    return context


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create a mock OpenAI client."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))]
    )
    return client


@pytest.fixture
def mock_github_client() -> MagicMock:
    """Create a mock GitHub client."""
    client = MagicMock()
    client.get_user = MagicMock()
    client.get_repo = MagicMock()
    return client


@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user data for testing."""
    return {
        "user_id": 12345,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "language_code": "en",
        "is_bot": False,
    }


@pytest.fixture
def sample_chat_data() -> dict:
    """Provide sample chat data for testing."""
    return {
        "chat_id": 67890,
        "chat_type": "private",
        "title": None,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_message_data() -> dict:
    """Provide sample message data for testing."""
    return {
        "message_id": 1,
        "chat_id": 67890,
        "user_id": 12345,
        "text": "/start",
        "date": 1234567890,
    }


@pytest.fixture
def async_mock() -> AsyncMock:
    """Create an AsyncMock instance for async testing."""
    return AsyncMock()


@pytest.fixture
def mock_aiohttp_session() -> Generator[MagicMock, None, None]:
    """Create a mock aiohttp ClientSession."""
    with patch("aiohttp.ClientSession") as mock_session:
        session_instance = MagicMock()
        session_instance.get = AsyncMock()
        session_instance.post = AsyncMock()
        session_instance.put = AsyncMock()
        session_instance.delete = AsyncMock()
        session_instance.close = AsyncMock()
        mock_session.return_value = session_instance
        yield mock_session


@pytest.fixture
def mock_environment_variables() -> Generator[None, None, None]:
    """Set up mock environment variables for testing."""
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENAI_API_KEY": "test_openai_key",
            "GITHUB_TOKEN": "test_github_token",
            "DATABASE_URL": "sqlite:///test.db",
        },
        clear=True,
    ):
        yield


@pytest.fixture
async def async_database(temp_db_path: Path) -> AsyncGenerator[Database, None]:
    """Create an async Database instance with a temporary file for testing."""
    db = Database(db_path=str(temp_db_path))
    await db.initialize_async()
    yield db
    await db.close_async()
    if temp_db_path.exists():
        temp_db_path.unlink()


@pytest.fixture
def database_with_data(database: Database, sample_user_data: dict, sample_chat_data: dict) -> Database:
    """Create a Database instance pre-populated with test data."""
    database.add_user(**sample_user_data)
    database.add_chat(**sample_chat_data)
    return database