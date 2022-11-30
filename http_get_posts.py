import config as cfg
import exceptions

import http
import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional


def get_last_posts_and_last_post_id(ino: tuple[str, int]) -> tuple[list[str], int]:
    ino_name, ino_last_post_id = ino
    ino_url = _get_ino_url(ino_name)

    response = requests.get(ino_url, allow_redirects=False)

    if (status := response.status_code) != 200:
        status_name = 'Redirect' if status == 302 else http.client.responses[status]
        ino_output = f'{ino_url} returned status code: {status} ({status_name}). Sorry'
        return [ino_output], -1

    last_posts = []

    soup = BeautifulSoup(response.text, 'html5lib')  # 'html.parser')
    posts, new_last_post_id = _get_new_posts(soup, ino_name, ino_last_post_id)
    for post in posts:
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

        _clear_ebala(post)
        _simplify_html(post)
        ino_output += _get_str_without_surrounding_tag(post)
        ino_output = '@' + ino_name + '\n\n' + ino_output
        last_posts.append(ino_output)

    return last_posts, new_last_post_id


def _clear_ebala(post_tag: Tag) -> None:
    for tag in post_tag.contents + post_tag.find_all(True):
        if tag.string and cfg.EBALA in tag.string:
            string = str(tag.string)
            position = string.find(cfg.EBALA)
            new_string = string[0:position] \
                + string[position + len(cfg.EBALA):]
            tag.string.replace_with(new_string)
    else:
        pass
        # raise exceptions.NoEbalaError('All inos must have ebala')


def _simplify_html(html_tag: Tag) -> None:
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

    def _tag_is_not_allowed(tag):
        if tag.name not in allowed_tags:
            return True

    for tag in html_tag.find_all(_tag_is_not_allowed, recursive=True):
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
    children_strs = [str(x).strip() for x in post_tag.children]
    joined_children_str = '\n'.join(x for x in children_strs if x)
    return joined_children_str


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
            new_posts.append(post)
        prev_post = post
    return new_posts, max_post_id
