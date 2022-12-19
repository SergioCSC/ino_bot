from enum import Enum, auto
import config as cfg

import json
import pathlib

if cfg.IN_AWS_LAMBDA:
    import boto3


class Command(Enum):
    UPDATE = auto()
    DELETE = auto()


def _load_json() -> dict[str, dict[str, int]]:
    if not cfg.IN_AWS_LAMBDA:
        json_path = pathlib.Path(cfg.INOS_JSON_FILENAME)
        if not json_path.is_file():
            return {}
        with json_path.open() as f:  # TODO what if no file
            json_dict = json.load(f)
        return json_dict
    else:
        table = boto3.resource("dynamodb").Table("inobot")
        response = table.get_item(Key={'my_partition_key_0': "mu"})['Item']
        json_dict = json.loads(response['json']) if 'json' in response else {}
        return json_dict


def _retrieve_all_chats_inos() -> dict[int, dict[str, int]]:
    dict_with_str_keys = _load_json()
    return {int(chat_id): v for chat_id, v in dict_with_str_keys.items()}


def retrieve_inos(chat_id: int) -> dict[str, int]:
    all_chats_inos = _retrieve_all_chats_inos()
    return all_chats_inos.get(chat_id, {})


def _rewrite_all_chats_inos(inos: dict[int, dict[str, int]]) -> None:
    if not cfg.IN_AWS_LAMBDA:
        with open(cfg.INOS_JSON_FILENAME, 'w') as f:
            json.dump(inos, f)
    else:
        table = boto3.resource("dynamodb").Table("inobot")
        table.put_item(
            Item={
                'my_partition_key_0': "mu",
                'json': json.dumps(inos)
            }
        )


def _manipulate_inos(chat_id: int, new_inos: dict[str, int], command: Command) -> None:

    def _manipulate(_old_inos: dict[str, int], _new_inos: dict[str, int], command: Command) \
            -> dict[str, int]:

        if command is Command.UPDATE:
            return _old_inos | _new_inos
        if command is Command.DELETE:
            for ino in _new_inos:
                if ino in _old_inos:
                    del _old_inos[ino]
            return _old_inos
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
