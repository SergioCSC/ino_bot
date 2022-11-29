from enum import Enum, auto
import config as cfg

import json
import pathlib


class Command(Enum):
    UPDATE = auto()
    DELETE = auto()


def retrieve_inos(chat_id: int) -> dict[str, int]:
    all_chats_inos = _retrieve_all_chats_inos()
    return all_chats_inos.get(chat_id, {})


def _retrieve_all_chats_inos() -> dict[int, dict[str, int]]:
    json_path = pathlib.Path(cfg.INOS_JSON_FILENAME)
    if not json_path.is_file():
        return {}
    with json_path.open() as f:  # TODO what if no file
        dict_with_str_keys = json.load(f)
        return {int(chat_id): v for chat_id, v in dict_with_str_keys.items()}


def _manipulate_inos(chat_id: int, new_inos: dict[str, int], command: Command) -> None:

    def _manipulate(_old_inos: dict[str, int], _new_inos: dict[str, int], command: Command) \
            -> dict[str, int]:

        match command:
            case Command.UPDATE:
                return _old_inos | _new_inos
            case Command.DELETE:
                for ino in _new_inos:
                    if ino in _old_inos:
                        del _old_inos[ino]
                return _old_inos
            case _:
                raise NotImplementedError('Unknown database command')

    if not new_inos:
        return

    new_inos = _clear(new_inos)

    all_chats_inos = _retrieve_all_chats_inos()
    old_inos = all_chats_inos.get(chat_id, {}).copy()

    new_inos = _manipulate(old_inos, new_inos, command)

    all_chats_inos[chat_id] = new_inos
    _rewrite_all_chats_inos(all_chats_inos)


def update_inos(chat_id: int, new_inos: dict[str, int]) -> None:
    _manipulate_inos(chat_id, new_inos, Command.UPDATE)


def delete_inos(chat_id: int, del_inos: dict[str, int]) -> None:
    _manipulate_inos(chat_id, del_inos, Command.DELETE)


def _clear_name(name: str) -> str:
    """clear a name of ino from prefix
    >>> _clear_name('ino')
    'ino'
    >>> _clear_name('@ino')
    'ino'
    >>> _clear_name(f'{cfg.TELEGRAM_URL_PREFIX}ino')
    'ino'
    >>> _clear_name(f'{cfg.INO_URL_PREFIX}ino')
    'ino'
    """

    for prefix in cfg.INO_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def _clear(inos: dict[str, int]) -> dict[str, int]:
    return {_clear_name(name): post_id for name, post_id in inos.items()}


def _rewrite_all_chats_inos(inos: dict[int, dict[str, int]]) -> None:
    with open(cfg.INOS_JSON_FILENAME, 'w') as f:
        json.dump(inos, f)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
