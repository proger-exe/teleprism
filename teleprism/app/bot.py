"""TelePrism long-polling entrypoint."""

import asyncio
import logging

import structlog

from teleprism.app.bootstrap import create_bot, create_dispatcher, start_workers
from teleprism.app.config import load_settings
from teleprism.app.db.connection import Database


async def run() -> None:
    """Run migrations, workers, and Telegram long polling."""

    settings = load_settings()
    logging.basicConfig(level=settings.log_level)
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(settings.log_level))
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required.")
    database = Database(settings.database_path)
    bot = create_bot(settings)
    dispatcher = await create_dispatcher(settings, database)
    workers = await start_workers(settings, database, bot)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await workers.stop()
        await bot.session.close()


def main() -> None:
    """Console-script entrypoint."""

    asyncio.run(run())


if __name__ == "__main__":
    main()
