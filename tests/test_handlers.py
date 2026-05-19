import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext
from src.bot.handlers import start, help_command, handle_message, error_handler


@pytest.fixture
def mock_update():
    """Create a mock Update object for testing."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.from_user = MagicMock(spec=User)
    update.message.from_user.id = 12345
    update.message.from_user.first_name = "TestUser"
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 12345
    update.message.reply_text = AsyncMock()
    update.message.reply_markdown = AsyncMock()
    update.effective_user = update.message.from_user
    update.effective_chat = update.message.chat
    return update


@pytest.fixture
def mock_context():
    """Create a mock CallbackContext object for testing."""
    context = MagicMock(spec=CallbackContext)
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    context.args = []
    return context


@pytest.mark.asyncio
async def test_start_handler(mock_update, mock_context):
    """Test the /start command handler."""
    await start(mock_update, mock_context)
    mock_update.message.reply_markdown.assert_called_once()
    call_args = mock_update.message.reply_markdown.call_args[0][0]
    assert "Welcome" in call_args or "Hello" in call_args
    assert "TestUser" in call_args


@pytest.mark.asyncio
async def test_help_handler(mock_update, mock_context):
    """Test the /help command handler."""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_markdown.assert_called_once()
    call_args = mock_update.message.reply_markdown.call_args[0][0]
    assert "/start" in call_args
    assert "/help" in call_args


@pytest.mark.asyncio
async def test_handle_message_text(mock_update, mock_context):
    """Test handling a text message."""
    mock_update.message.text = "Hello bot"
    mock_update.message.entities = []
    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert call_args is not None


@pytest.mark.asyncio
async def test_handle_message_empty_text(mock_update, mock_context):
    """Test handling a message with empty text."""
    mock_update.message.text = ""
    mock_update.message.entities = []
    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_no_text(mock_update, mock_context):
    """Test handling a message without text (e.g., photo, sticker)."""
    mock_update.message.text = None
    mock_update.message.entities = []
    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_error_handler(mock_update, mock_context):
    """Test the error handler."""
    test_error = Exception("Test error occurred")
    await error_handler(mock_update, mock_context)
    mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_error_handler_with_update(mock_update, mock_context):
    """Test the error handler with a valid update object."""
    test_error = Exception("Test error")
    mock_update.effective_chat.id = 12345
    await error_handler(mock_update, mock_context)
    mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_start_handler_with_args(mock_update, mock_context):
    """Test the /start command handler with additional arguments."""
    mock_context.args = ["arg1", "arg2"]
    await start(mock_update, mock_context)
    mock_update.message.reply_markdown.assert_called_once()


@pytest.mark.asyncio
async def test_help_handler_response_format(mock_update, mock_context):
    """Test that help handler returns properly formatted response."""
    await help_command(mock_update, mock_context)
    call_args = mock_update.message.reply_markdown.call_args[0][0]
    assert isinstance(call_args, str)
    assert len(call_args) > 0


@pytest.mark.asyncio
async def test_handle_message_with_entities(mock_update, mock_context):
    """Test handling a message with entities (e.g., mentions, hashtags)."""
    mock_update.message.text = "Hello @user"
    mock_update.message.entities = [MagicMock()]
    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_error_handler_logs_error(mock_update, mock_context):
    """Test that error handler properly logs the error."""
    with patch('src.bot.handlers.logger') as mock_logger:
        await error_handler(mock_update, mock_context)
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_concurrent_handlers(mock_update, mock_context):
    """Test that handlers can be called concurrently without issues."""
    import asyncio
    tasks = [
        start(mock_update, mock_context),
        help_command(mock_update, mock_context),
        handle_message(mock_update, mock_context)
    ]
    await asyncio.gather(*tasks)
    assert mock_update.message.reply_markdown.call_count >= 2
    assert mock_update.message.reply_text.call_count >= 1


@pytest.mark.asyncio
async def test_handle_message_special_characters(mock_update, mock_context):
    """Test handling messages with special characters."""
    mock_update.message.text = "Hello! @#$%^&*()"
    mock_update.message.entities = []
    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert call_args is not None


@pytest.mark.asyncio
async def test_start_handler_no_user_name(mock_update, mock_context):
    """Test start handler when user has no first name."""
    mock_update.message.from_user.first_name = None
    await start(mock_update, mock_context)
    mock_update.message.reply_markdown.assert_called_once()


@pytest.mark.asyncio
async def test_error_handler_without_update():
    """Test error handler when update is None."""
    context = MagicMock(spec=CallbackContext)
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    await error_handler(None, context)
    context.bot.send_message.assert_not_called()