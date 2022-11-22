# import json
import requests
import config as cfg
from bs4 import BeautifulSoup, Tag
from telegram import Update
from telegram import ParseMode
from telegram.ext import Updater, CallbackContext, TypeHandler


# def sanitize_tags(html: BeautifulSoup) -> BeautifulSoup:
#     # l = [data for data in html]
#     for data in html(['br']):
#         data.decompose()
#     return '\n\n'.join(html.stripped_strings)


def clear_ebala(message_tag: Tag) -> None:
    for tag in message_tag.contents + message_tag.find_all(True):
        if tag.string and cfg.EBALA in tag.string:
            string = str(tag.string)
            position = string.find(cfg.EBALA)
            new_string = string[0:position] + string[position + len(cfg.EBALA):]
            tag.string.replace_with(new_string)


def simplify_html(html_tag: Tag) -> None:
    allowed_tags = {'b', 'strong', 'i', 'em', 'u', 'ins', 's',
                 'strike', 'del', 'tg-spoiler',
                 'code', 'pre',
                 'a', 'span'
                 }

    def tag_is_not_allowed(tag):
        if tag.name not in allowed_tags:
            return True
        

    # print(soup)
    # soup.unwrap()
    # last_message.name
    for tag in html_tag.find_all(tag_is_not_allowed, recursive=True):
        # print(tag.name)
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
    result = ''.join(x for x in result if x)
    return result
    

def get_last_schulmann_post_text() -> str:
    url = 'https://t.me/s/eschulmann'
    # url = 'https://t.me/s/yurydud'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html5lib')  # 'html.parser')
    messages = soup.find_all(attrs={'class': 'tgme_widget_message_text'})
    last_msg = messages[-1]

    clear_ebala(last_msg)
    simplify_html(last_msg)
    result_text = get_str_without_surrounding_tag(last_msg)
    return result_text


    # last_msg_sanitized_html = sanitize_tags(last_msg)
    # last_msg_html = last_msg.prettify()
    # return last_msg_html
    # cleared_last_msg_strings = [s.replace(cfg.EBALA, '')
    #                             for s in last_msg.strings]
    # cleared_last_msg_strings = [s for s in cleared_last_msg_strings if s]
    return '\n\n'.join(cleared_last_msg_strings)


def echo(update: Update, context: CallbackContext) -> None:
    # text = json.dumps(update.to_dict(), indent=2)
    text = get_last_schulmann_post_text()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text, parse_mode=ParseMode.HTML)


def main() -> None:
    updater = Updater('5781055986:AAGuGUbgTk0MtZlydHFPltp2DEBHFX_QDTM')
    updater.dispatcher.add_handler(TypeHandler(Update, echo))
    updater.start_polling()
    print('Started')
    updater.idle()


if __name__ == '__main__':
    main()
