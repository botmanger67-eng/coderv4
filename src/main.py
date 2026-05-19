import asyncio
import sys
from typing import NoReturn

from loguru import logger

from src.bot.handlers import setup_handlers
from src.core.config import settings
from src.core.database import Database
from src.core.logger import configure_logging


async def main() -> NoReturn:
    """Initialize and run the Telegram bot application."""
    configure_logging()
    logger.info("Starting bot application")

    try:
        database = Database(settings.database_url)
        await database.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    try:
        application = setup_handlers(database)
        await application.initialize()
        logger.info("Bot handlers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot handlers: {e}")
        await database.close()
        sys.exit(1)

    try:
        logger.info(f"Starting bot polling with token: {settings.bot_token[:8]}...")
        await application.run_polling(allowed_updates=settings.allowed_updates)
    except Exception as e:
        logger.error(f"Bot polling failed: {e}")
    finally:
        await database.close()
        logger.info("Bot application shut down")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)