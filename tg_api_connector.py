import config as cfg
import model
import base  # TODO refuse to use the database directly in this module

import asyncio
import json
import time

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.ext import TypeHandler, CommandHandler

from telegram.ext import Application


async def get_inos_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    chat_texts = model.get_new_messages(chat_id)
    for ino_texts in chat_texts:  # TODO send many messages in one Update
        for ino_text in ino_texts:
            await context.bot.send_message(  # TODO: reply
                chat_id=chat_id, text=ino_text,
                parse_mode=ParseMode.HTML
            )
        # time.sleep(1)


async def add_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    base.update_inos(chat_id, inos)


async def del_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    base.delete_inos(chat_id, inos)


async def list_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = base.retrieve_inos(chat_id)
    if inos:
        text = ' '.join(ino_name for ino_name in inos)
        await context.bot.send_message(chat_id=chat_id, text=text)  # TODO: reply


async def clear_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # del_ino_command(update, CallbackContext)
    # add_ino_command(update, CallbackContext)
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    _clear_inos(chat_id, inos)


async def clear_all_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = base.retrieve_inos(chat_id)
    _clear_inos(chat_id, inos)


def _clear_inos(chat_id: int, inos: dict[str, int]) -> None:
    base.delete_inos(chat_id, inos)
    inos = {name: -1 for name in inos}
    base.update_inos(chat_id, inos)


def _get_inos_from_update(update: Update) -> dict[str, int]:
    inos = update.effective_message.text.split()[1:]  # type: ignore
    inos = {name: -1 for name in inos}
    return inos


def read_token() -> str:
    with open(cfg.TOKEN_FILENAME) as f:
        return f.read().strip()


def get_application_with_handlers() -> Application:
    # application = ApplicationBuilder().token(read_token()).build()
    application = Application.builder().token(read_token()).build()
    application.add_handler(CommandHandler('add', add_inos_command))
    application.add_handler(CommandHandler('del', del_inos_command))
    application.add_handler(CommandHandler('clear', clear_inos_command))
    application.add_handler(CommandHandler('clearall', clear_all_inos_command))
    application.add_handler(CommandHandler('list', list_inos_command))
    application.add_handler(TypeHandler(Update, get_inos_updates))
    return application


def handle_updates_via_webhook(event, context):
    # application = get_application_with_handlers()
    # update = Update.de_json(json.loads(event['body']), application.bot)
    # await application.process_update(update)
    # return asyncio.get_event_loop().run_until_complete(main(event, context))
    return asyncio.run(main(event, context))


async def main(event, context):
    application = get_application_with_handlers()

    try:
        await application.initialize()
        update = Update.de_json(json.loads(event['body']), application.bot)
        await application.process_update(update)

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }


if __name__ == '__main__':
    application = get_application_with_handlers()
    application.run_polling()
