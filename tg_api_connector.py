import config as cfg
import model
import base  # TODO refuse to use the database directly in this module
import utils

import asyncio
import json
# import yappi
import time
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.ext import TypeHandler, CommandHandler
from telegram.ext import Application


def time_measure_of_handler(handler):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # cProfile.runctx('handler(update, context)', globals(), locals())
        start_time = time.time()
        result = await handler(update, context)
        t = time.time() - start_time
        chat_id = update.effective_chat.id  # type: ignore
        time_text = f'{t:.1f} sec  handler: {handler.__name__}()'  # for {chat_id = }
        print(time_text)
        await context.bot.send_message(  # TODO: reply
            chat_id=chat_id, text=time_text,
            parse_mode=ParseMode.HTML
        )
        return result

    return wrapper


@utils.time_measure
async def _send_messages_to_chat(context: ContextTypes.DEFAULT_TYPE,
                                 chat_id: int, chat_texts: list[list[str]]):
    # for ino_texts in chat_texts:
    #     for ino_text in ino_texts:
    #         await context.bot.send_message(  # TODO: reply
    #             chat_id=chat_id, text=ino_text,
    #             parse_mode=ParseMode.HTML
    #         )

    delimeter = '\n\n\n\n'
    for ino_texts in chat_texts:  # TODO send many messages in one Update
        ino_all_texts_in_one = ''
        for ino_text in reversed(ino_texts):
            new_ino_all_texts_in_one = ino_text + delimeter + ino_all_texts_in_one
            if len(new_ino_all_texts_in_one) > cfg.TELEGRAM_MAX_POST_LENGTH:
                break
            ino_all_texts_in_one = new_ino_all_texts_in_one

        if ino_all_texts_in_one:
            await context.bot.send_message(  # TODO: reply
                chat_id=chat_id, text=ino_all_texts_in_one,
                parse_mode=ParseMode.HTML
            )


@time_measure_of_handler
async def get_inos_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    chat_texts = model.get_new_messages(chat_id)

    await _send_messages_to_chat(context, chat_id=chat_id, chat_texts=chat_texts)


@time_measure_of_handler
async def add_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    base.update_inos(chat_id, inos)


@time_measure_of_handler
async def del_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    base.delete_inos(chat_id, inos)


@time_measure_of_handler
async def list_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore
    inos = base.retrieve_inos(chat_id)
    if inos:
        text = ' '.join(ino_name for ino_name in inos)
        await context.bot.send_message(chat_id=chat_id, text=text)  # TODO: reply


@time_measure_of_handler
async def clear_inos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # del_ino_command(update, CallbackContext)
    # add_ino_command(update, CallbackContext)
    chat_id = update.effective_chat.id  # type: ignore
    inos = _get_inos_from_update(update)
    _clear_inos(chat_id, inos)


@time_measure_of_handler
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
    # yappi.set_clock_type("WALL")
    # with yappi.run():
    #     result = asyncio.run(main(event, context))
    # if cfg.IN_AWS_LAMBDA:
    #     yappi.get_func_stats().print_all()
    # else:
    #     current_time = time.strftime("%H_%M_%S___%d_%b_%Y", time.localtime())
    #     out_filedir = Path(__file__).parent / 'profiler'
    #     out_filedir.mkdir(exist_ok=True)
    #     out_filepath = out_filedir / f'{current_time}.txt'
    #     with open(out_filepath, 'w') as f:
    #         yappi.get_func_stats().print_all(out=f)
    # return result


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


def simulate_webhook_call() -> None:

    aws_body_file = Path(__file__).parent / 'aws_examples' / 'event_body.json'
    with open(aws_body_file) as f:
        event = json.load(f)

    handle_updates_via_webhook(event, None)


if __name__ == '__main__':

    simulate_webhook_call()

    # application = get_application_with_handlers()
    # application.run_polling()
