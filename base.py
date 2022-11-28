import config as cfg

import json
import pathlib


def retrieve_inos(chat_id: int) -> dict[str, int]:
    all_chats_inos = _retrieve_all_chats_inos()
    return all_chats_inos.get(chat_id, {})


def _retrieve_all_chats_inos() -> dict[int, dict[str, int]]:
    json_path = pathlib.Path(cfg.INOS_JSON_FILENAME)
    if not json_path.is_file():
        return {}
    with json_path.open() as f:  #TODO what if no file
        dict_with_str_keys = json.load(f)
        return {int(chat_id): v for chat_id, v in dict_with_str_keys.items()}
        
    

def update_inos(chat_id: int, new_inos: dict[str, int]) -> None:

    def _rewrite_all_chats_inos(inos: dict[int, dict[str, int]]) -> None:
        with open(cfg.INOS_JSON_FILENAME, 'w') as f:
            json.dump(inos, f)

    if not new_inos:
        return

    all_chats_inos = _retrieve_all_chats_inos()

    old_inos = all_chats_inos.get(chat_id, {})
    new_inos = old_inos | new_inos
    all_chats_inos[chat_id] = new_inos

    _rewrite_all_chats_inos(all_chats_inos)
