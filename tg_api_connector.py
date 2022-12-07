import config as cfg
import model
import base  # TODO refuse to use the database directly in this module

import time
from telegram import Update
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import TypeHandler, CommandHandler


def get_inos_updates(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    texts = model.get_new_messages(chat_id)
    for text in texts:
        context.bot.send_message(
            chat_id=chat_id, text=text,
            parse_mode=ParseMode.HTML
        )
        time.sleep(1)


def add_inos_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = _get_inos_from_update(update)
    base.update_inos(chat_id, inos)


def del_inos_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = _get_inos_from_update(update)
    base.delete_inos(chat_id, inos)


def list_inos_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = base.retrieve_inos(chat_id)
    text = ' '.join(ino_name for ino_name in inos)
    context.bot.send_message(chat_id=chat_id, text=text)


def clear_inos_command(update: Update, context: CallbackContext) -> None:
    # del_ino_command(update, CallbackContext)
    # add_ino_command(update, CallbackContext)
    chat_id = update.effective_chat.id
    inos = _get_inos_from_update(update)
    _clear_inos(chat_id, inos)


def clear_all_inos_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = base.retrieve_inos(chat_id)
    _clear_inos(chat_id, inos)


def _clear_inos(chat_id: int, inos: dict[str, int]) -> None:
    base.delete_inos(chat_id, inos)
    inos = {name: -1 for name in inos}
    base.update_inos(chat_id, inos)


def _get_inos_from_update(update: Update) -> dict[str, int]:
    inos = update.effective_message.text.split()[1:]
    inos = {name: -1 for name in inos}
    return inos


def read_token() -> str:
    with open(cfg.TOKEN_FILENAME) as f:
        return f.read().strip()


def start_long_polling():
    updater = Updater(read_token())
    updater.dispatcher.add_handler(CommandHandler('add', add_inos_command))
    updater.dispatcher.add_handler(CommandHandler('del', del_inos_command))
    updater.dispatcher.add_handler(CommandHandler('clear', clear_inos_command))
    updater.dispatcher.add_handler(CommandHandler('clearall', clear_all_inos_command))
    updater.dispatcher.add_handler(CommandHandler('list', list_inos_command))
    updater.dispatcher.add_handler(TypeHandler(Update, get_inos_updates))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == '__main__':
    start_long_polling()
