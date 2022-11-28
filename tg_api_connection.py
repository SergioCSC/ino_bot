import http_get_ino
import base

import time
from telegram import Update
from telegram import ParseMode
from telegram.ext import Updater, CallbackContext, TypeHandler, CommandHandler


def send_ino_updates(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = base.retrieve_inos(chat_id)
    new_inos = {}
    for ino in inos.items():
        texts, new_last_post_id = http_get_ino.get_last_posts_and_last_post_id(ino)
        ino_name, old_last_post_id = ino
        if new_last_post_id > old_last_post_id:
            new_inos[ino_name] = new_last_post_id
        for text in texts:
            context.bot.send_message(
                chat_id=chat_id, text=text,
                parse_mode=ParseMode.HTML
            )
            time.sleep(1)
    base.update_inos(chat_id, new_inos)


def _get_inos_from_update(update: Update) -> dict[str, int]:
    inos = update.effective_message.text.split()[1:]
    inos = {name: -1 for name in inos}
    return inos


def add_ino_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = _get_inos_from_update(update)
    base.update_inos(chat_id, inos)

def del_ino_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = _get_inos_from_update(update)
    base.delete_inos(chat_id, inos)

def list_ino_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    inos = base.retrieve_inos(chat_id)
    text = ' '.join(ino_name for ino_name in inos)
    context.bot.send_message(
                chat_id=chat_id, text=text
            )


def main() -> None:
    updater = Updater('5781055986:AAGuGUbgTk0MtZlydHFPltp2DEBHFX_QDTM')
    updater.dispatcher.add_handler(CommandHandler('add', add_ino_command))
    updater.dispatcher.add_handler(CommandHandler('del', del_ino_command))
    updater.dispatcher.add_handler(CommandHandler('list', list_ino_command))
    updater.dispatcher.add_handler(TypeHandler(Update, send_ino_updates))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == '__main__':
    main()
