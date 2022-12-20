import config as cfg
import exceptions

import re
import http
import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional


REGEXP_COMPILED_EBALA = re.compile(cfg.REGEXP_EBALA)
REGEXP_COMPILED_MANY_LINE_BREAKS = re.compile(cfg.REGEXP_MANY_LINE_BREAKS)
SESSION = requests.Session()


def http_get(ino_url):
    return SESSION.get(ino_url, allow_redirects=False)


def get_last_posts_and_last_post_id(ino: tuple[str, int]) -> tuple[list[str], int]:
    ino_name, ino_last_post_id = ino
    ino_url = _get_ino_url(ino_name)

    response = http_get(ino_url)

    if (status := response.status_code) != 200:
        status_name = 'Redirect' if status == 302 else http.client.responses[status]
        ino_output = f'{ino_url} returned status code: {status} ({status_name}). Sorry'
        return [ino_output], -1

    last_posts = []

    soup = BeautifulSoup(response.text, 'lxml')  # 'lxml' 'html.parser' 'html5lib'
    posts, new_last_post_id = _get_new_posts(soup, ino_name, ino_last_post_id)
    for post, post_id in posts:
        ino_output = ''
        for tag in list(post.previous_siblings) \
                + list(post.next_siblings):
            if tag.name == 'a' and 'href' in tag.attrs and 'class' in tag.attrs:
                href = tag.attrs['href']
                class_values = tag.attrs['class']
                if 'tgme_widget_message_photo_wrap' in class_values:
                    ino_output += f'<a href="{href}">photo\n\n</a>'
                if 'tgme_widget_message_video_wrap' in class_values or \
                        'tgme_widget_message_video_player' in class_values:
                    ino_output += f'<a href="{href}">video\n\n</a>'

        _simplify_html(post)
        ino_output += _get_str_without_surrounding_tag(post)
        ino_output = _clear_ebala(ino_output)
        href = f'{cfg.TELEGRAM_URL_PREFIX}{ino_name}/{post_id}'
        ino_output = f'<a href="{href}">{ino_name}</a>' + '\n\n' + ino_output
        ino_output = REGEXP_COMPILED_MANY_LINE_BREAKS.sub('\n\n', ino_output)
        last_posts.append(ino_output)

    return last_posts, new_last_post_id


def _clear_ebala(string: str) -> str:
    clean_string = REGEXP_COMPILED_EBALA.sub('', string)
    # if clean_string == string:
    #     raise exceptions.NoEbalaError('All inos must have ebala')
    return clean_string


def _simplify_html(html_tag: Tag) -> None:
    def _tag_is_not_allowed(tag):
        if tag.name not in cfg.ALLOWED_TAGS:
            return True

    for tag in html_tag.find_all(_tag_is_not_allowed, recursive=True):
        # if tag.name != 'br':  # deal with 'br' tag after str(tag)
        #     tag.unwrap()
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


def _get_str_without_surrounding_tag(post_tag: Tag) -> str:
    # children_strs = [str(x).strip() for x in post_tag.children]
    # joined_children_str = '\n'.join(x for x in children_strs if x)
    result = ''
    for tag in post_tag.children:
        # _simplify_html(tag)
        str_tag = str(tag)
        # str_tag = str_tag.replace('<br/>', '\n\n')
        # str_tag = str_tag.replace('<br>', '\n\n')
        if tag.name in cfg.ALLOWED_BLOCK_TAGS:
            result += f'\n\n{str_tag}\n\n'
        else:
            result += str_tag

    return result


def _get_ino_url(ino_name: str) -> str:
    return cfg.INO_URL_PREFIX + ino_name


def _get_post_id(post: Tag, ino_name: str) -> int:

    def _get_post_id_from_sibling_widget(tag: Tag) \
            -> Optional[int]:
        for s in tag.next_siblings:
            if s.name == 'div' and 'class' in s.attrs \
                    and 'tgme_widget_message_footer' in s.attrs['class']:
                tag_date = s.find('a', class_='tgme_widget_message_date')
                href = tag_date.attrs['href']
                post_id_str = href.replace(f'{cfg.TELEGRAM_URL_PREFIX}{ino_name}/', '')
                post_id = int(post_id_str)
                return post_id
        else:
            return None

    if post_id := _get_post_id_from_sibling_widget(post):
        return post_id

    p = post.parent
    if p.name == 'div' and 'class' in p.attrs \
            and 'media_supported_cont' in p.attrs['class'] \
            and (post_id := _get_post_id_from_sibling_widget(p)):
        return post_id

    raise exceptions.TelegramSiteParsingError(
        f'Cannot find post id in the post. ino: {ino_name}')


def _get_new_posts(soup: BeautifulSoup, ino_name: str,
                   last_seen_post_id: int) -> tuple[list[Tag], int]:
    posts = soup.find_all(attrs={'class': 'tgme_widget_message_text'})
    new_posts = []
    max_post_id = -1
    prev_post = None
    for post in posts:
        if post.parent == prev_post:
            continue
        post_id = _get_post_id(post, ino_name)
        max_post_id = max(max_post_id, post_id)
        if post_id > last_seen_post_id:
            new_posts.append((post, post_id))
        prev_post = post
    return new_posts, max_post_id
