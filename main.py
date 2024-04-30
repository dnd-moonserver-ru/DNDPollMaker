import asyncio
import datetime
import logging
import sys
import locale
from os import getenv

import ResourceBundle as rb
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("DND_POLL_MAKER_BOT_TOKEN")
LOCALE = getenv("DND_POLL_MAKER_LOCALE")

locale.setlocale(locale.LC_TIME, LOCALE)
bundle = rb.get_bundle("resources/messages", LOCALE)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(bundle.get("start").format(hbold(message.from_user.full_name)))


@dp.message(F.text, Command("poll"))
async def command_poll(message: Message) -> None:
    args = message.text.split()

    if len(args) != 3:
        await message.answer(bundle.get("commandPollUsage"))
        return

    date_format = '%d.%m.%y'

    try:
        date_start = datetime.datetime.strptime(args[1], date_format)
        date_end = datetime.datetime.strptime(args[2], date_format)
    except ValueError:
        await message.answer(bundle.get("commandPollFormat"))
        return

    days = (date_end - date_start).days

    print(days)

    if days < 2 or days > 10:
        await message.answer(bundle.get("commandPollOverflow"))
        return

    options = list()
    date_current = date_start
    while date_current <= date_end:
        options.append(date_current.strftime("%d.%m.%y (%A)"))
        date_current += datetime.timedelta(days=1)

    await message.reply_poll(
        question=bundle.get("pollTitle").format(message.from_user.full_name),
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
