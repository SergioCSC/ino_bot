import base
import http_get_posts
import utils

@utils.time_measure
def get_new_messages(chat_id: int) -> list[list[str]]:
    inos = base.retrieve_inos(chat_id)
    new_inos = {}
    new_messages = []
    for ino in inos.items():
        texts, new_last_post_id = http_get_posts.get_last_posts_and_last_post_id(ino)
        ino_name, old_last_post_id = ino
        if new_last_post_id > old_last_post_id:
            new_inos[ino_name] = new_last_post_id
        new_messages.append(texts)
    base.update_inos(chat_id, new_inos)
    return new_messages
