import config as cfg

import requests
from bs4 import BeautifulSoup, Tag


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


def get_ino_url(ino_name: str) -> str:
    return cfg.INO_URL_PREFIX + ino_name


def get_new_messages(soup: BeautifulSoup, last_seen_post_id: int) -> list[Tag]:
    messages = soup.find_all(attrs={'class': 'tgme_widget_message_text'})
    last_msg = messages[-1]
    return [last_msg]


def get_last_posts_and_last_post_id(ino) -> str:
    ino_name, ino_last_post_id = ino
    ino_url = get_ino_url(ino_name)
    
    response = requests.get(ino_url, allow_redirects=False)
    
    if (status := response.status_code) != 200:
        ino_output = f'{ino_url} returned status code: {status}. Sorry'
        return [ino_output]

    last_posts = []

    soup = BeautifulSoup(response.text, 'html5lib')  # 'html.parser')
    messages, new_last_post_id = get_new_messages(soup, ino_last_post_id)
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
        last_posts.append(ino_output)

    return last_posts, new_last_post_id
