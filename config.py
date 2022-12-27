from pathlib import Path
from sys import path
from os import environ

AWS_LAMBDA_FUNCTION_NAME_ENV = 'AWS_LAMBDA_FUNCTION_NAME'
IN_AWS_LAMBDA = AWS_LAMBDA_FUNCTION_NAME_ENV in environ
if IN_AWS_LAMBDA:
    lib_folder = Path(__file__).parent / 'libs_for_aws_lambda'
    path.append(str(lib_folder))


REGEXP_MANY_LINE_BREAKS = r'\s*(\n\s*){3,}'
REGEXP_EBALA = r'(18\+  )?(ДАННОЕ СООБЩЕНИЕ|НАСТОЯЩИЙ МАТЕРИАЛ) [-,\.()\w ]+ ИНОСТРАНН(ОГО|ЫХ|ЫМ) АГЕНТ(А|ОВ|ОМ)[^<\r\n]*'

INOS_JSON_FILENAME = 'inos.json'
TOKEN_FILENAME = 'token.txt'

TELEGRAM_URL_PREFIX = 'https://t.me/'
INO_URL_PREFIX = f'{TELEGRAM_URL_PREFIX}s/'
INO_PREFIXES = (INO_URL_PREFIX, TELEGRAM_URL_PREFIX, '@')

TELEGRAM_MAX_POST_LENGTH = 4_096

ALLOWED_BLOCK_TAGS = {"code", "pre"}
ALLOWED_NON_BLOCK_TAGS = {
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
    "a",
    "span",
}
ALLOWED_TAGS = ALLOWED_BLOCK_TAGS | ALLOWED_NON_BLOCK_TAGS
