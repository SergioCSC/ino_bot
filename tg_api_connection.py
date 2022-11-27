import http_get_ino
import base

from telegram import Update
from telegram import ParseMode
from telegram.ext import Updater, CallbackContext, TypeHandler, CommandHandler


def send_ino_updates(update: Update, context: CallbackContext) -> None:
    inos = base.retrieve_inos()
    new_inos = {}
    for ino in inos.items():
        texts, last_post_id = http_get_ino.get_last_posts_and_last_post_id(ino)
        ino_name, _ = ino
        new_inos[ino_name] = last_post_id
        for text in texts:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text,
                parse_mode=ParseMode.HTML
            )
    base.update_inos(new_inos)


def add_ino_command(update: Update, context: CallbackContext) -> None:
    inos = update.message.text.split()[1:]
    inos = {name: -1 for name in inos}
    base.update_inos(inos)


def main() -> None:
    updater = Updater('5781055986:AAGuGUbgTk0MtZlydHFPltp2DEBHFX_QDTM')
    updater.dispatcher.add_handler(CommandHandler('add', add_ino_command))
    updater.dispatcher.add_handler(TypeHandler(Update, send_ino_updates))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == '__main__':
    main()
