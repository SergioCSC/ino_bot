# import json
import requests
import config as cfg
from bs4 import BeautifulSoup, Tag
from telegram import Update
from telegram import ParseMode
from telegram.ext import Updater, CallbackContext, TypeHandler, CommandHandler


def clear_ebala(message_tag: Tag) -> None:
    for tag in message_tag.contents + message_tag.find_all(True):
        if tag.string and cfg.EBALA in tag.string:
            string = str(tag.string)
            position = string.find(cfg.EBALA)
            new_string = string[0:position] + string[position + len(cfg.EBALA) :]
            tag.string.replace_with(new_string)


def simplify_html(html_tag: Tag) -> None:
    allowed_tags = {
        "b",
        "strong",
        "i",
        "em",
        "u",
        "ins",
        "s",
        "strike",
        "del",
        "tg-spoiler",
        "code",
        "pre",
        "a",
        "span",
    }

    def tag_is_not_allowed(tag):
        if tag.name not in allowed_tags:
            return True

    # print(soup)
    # soup.unwrap()
    # last_message.name
    # TODO 'br' --> '\n'
    for tag in html_tag.find_all(tag_is_not_allowed, recursive=True):
        # print(tag.name)
        tag.unwrap()
    for tag in html_tag.find_all("a"):
        if "href" not in tag.attrs:
            tag.unwrap()
        else:
            tag.attrs = {"href": tag.attrs["href"]}

    for tag in html_tag.find_all("span"):
        if "class" not in tag.attrs or tag.attrs["class"] != ["tg-spoiler"]:
            tag.unwrap()


def get_str_without_surrounding_tag(message_tag: Tag) -> str:
    result = [str(x).strip() for x in message_tag.children]
    result = "\n\n".join(x for x in result if x)
    return result


def retrieve_inos() -> list[str]:
    with open(cfg.INOS_FILENAME) as f:
        return [ino.strip() for ino in f if ino.strip()]


def update_inos(inos: list[str]) -> None:
    pass


def get_ino_urls(inos: list[str]) -> list[str]:
    urls = [cfg.INO_URL_PREFIX + ino for ino in inos]
    return urls


def get_last_inos_posts_text() -> str:
    inos = retrieve_inos()
    ino_urls = get_ino_urls(inos)
    ino_texts = []
    for ino, ino_url in zip(inos, ino_urls):
        # url = 'https://t.me/s/eschulmann'
        # url = 'https://t.me/s/yurydud'
        response = requests.get(ino_url)
        soup = BeautifulSoup(response.text, "html5lib")  # 'html.parser')
        messages = soup.find_all(attrs={"class": "tgme_widget_message_text"})
        last_msg = messages[-1]

        clear_ebala(last_msg)
        simplify_html(last_msg)
        text = get_str_without_surrounding_tag(last_msg)
        text = '@' + ino + '\n\n' + text
        ino_texts.append(text)
    return ino_texts


def echo(update: Update, context: CallbackContext) -> None:
    texts = get_last_inos_posts_text()
    for text in texts:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML
        )


def add_ino_command(update: Update, context: CallbackContext) -> None:
    # print(update.message)
    inos = update.message.text.split()[1:]
    update_inos(inos)


def main() -> None:
    updater = Updater("5781055986:AAGuGUbgTk0MtZlydHFPltp2DEBHFX_QDTM")
    updater.dispatcher.add_handler(CommandHandler("add", add_ino_command))
    updater.dispatcher.add_handler(TypeHandler(Update, echo))
    updater.start_polling()
    print("Started")
    updater.idle()


if __name__ == "__main__":
    main()
