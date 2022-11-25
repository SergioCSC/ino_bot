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
            new_string = string[0:position] \
                + string[position + len(cfg.EBALA):]
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

    for tag in html_tag.find_all(tag_is_not_allowed, recursive=True):
        # print(tag.name)
        if tag.name == 'br':
            tag.replace_with('\n\n')
        else:
            tag.unwrap()
    for tag in html_tag.find_all('a'):
        if 'href' not in tag.attrs:
            tag.unwrap()
        else:
            tag.attrs = {'href': tag.attrs['href']}

    for tag in html_tag.find_all('span'):
        if 'class' not in tag.attrs or tag.attrs['class'] != ['tg-spoiler']:
            tag.unwrap()


def get_str_without_surrounding_tag(message_tag: Tag) -> str:
    result = [str(x).strip() for x in message_tag.children]
    result = '\n\n'.join(x for x in result if x)
    return result


def clear_inos(inos: dict[str, int]) -> dict[str, int]:
    cleared_inos = {name.strip(): post_id for name, post_id in inos.items()}
    if '' in cleared_inos:
        del cleared_inos['']
    return cleared_inos


def retrieve_inos() -> dict[str, int]:
    with open(cfg.INOS_FILENAME) as f:
        result = (ino.strip().split() for ino in f if ino.strip())
        result = (ino if len(ino) > 1 else (ino[0], -1) for ino in result)
        result = {name: int(post_id) for name, post_id in result}
        return result


def update_inos(new_inos: dict[str, int]) -> None:
    
    def rewrite_inos(inos: dict[str, int]) -> None:
        with open(cfg.INOS_FILENAME, 'w') as f:
            for ino_name, ino_post_id in inos.items():
                f.write(f'{ino_name} {ino_post_id}\n')

    old_inos = retrieve_inos()
    all_inos = old_inos | new_inos
    rewrite_inos(all_inos)


def get_ino_url(ino_name: str) -> str:
    return cfg.INO_URL_PREFIX + ino_name


def get_new_messages(soup: BeautifulSoup, last_seen_post_id: int) -> list[Tag]:
    messages = soup.find_all(attrs={'class': 'tgme_widget_message_text'})
    last_msg = messages[-1]
    return [last_msg]


def get_last_inos_posts_text() -> str:
    inos = retrieve_inos()
    ino_outputs = []
    for ino_name, last_seen_post_id in inos.items():
        ino_url = get_ino_url(ino_name)
        response = requests.get(ino_url, allow_redirects=False)
        if (status := response.status_code) != 200:
            ino_output = f'{ino_url} returned status code: {status}. Sorry'
            ino_outputs.append(ino_output)
            continue
        soup = BeautifulSoup(response.text, 'html5lib')  # 'html.parser')
        messages = get_new_messages(soup, last_seen_post_id)
        for message in messages:
            ino_output = ''
            for tag in list(message.previous_siblings) \
                    + list(message.next_siblings):
                if tag.name == 'a' and 'class' in tag.attrs:
                    href = tag.attrs['href']
                    class_values = tag.attrs['class']
                    if 'tgme_widget_message_photo_wrap' in class_values:
                        # ino_output_text += f'photo: {href}\n\n'
                        ino_output += f'<a href="{href}">photo\n\n</a>'
                    if 'tgme_widget_message_video_wrap' in class_values or \
                            'tgme_widget_message_video_player' in class_values:
                        ino_output += f'<a href="{href}">video\n\n</a>'

            clear_ebala(message)
            simplify_html(message)
            ino_output += get_str_without_surrounding_tag(message)
            ino_output = '@' + ino_name + '\n\n' + ino_output
            ino_outputs.append(ino_output)
    return ino_outputs


def send_ino_updates(update: Update, context: CallbackContext) -> None:
    texts = get_last_inos_posts_text()
    for text in texts:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text,
            parse_mode=ParseMode.HTML
        )


def add_ino_command(update: Update, context: CallbackContext) -> None:
    inos = update.message.text.split()[1:]
    inos = {name: -1 for name in inos}
    update_inos(inos)


def main() -> None:
    updater = Updater('5781055986:AAGuGUbgTk0MtZlydHFPltp2DEBHFX_QDTM')
    updater.dispatcher.add_handler(CommandHandler('add', add_ino_command))
    updater.dispatcher.add_handler(TypeHandler(Update, send_ino_updates))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == '__main__':
    main()
