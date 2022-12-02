
REGEXP_MANY_LINE_BREAKS = r'\s*(\n\s*){3,}'
REGEXP_EBALA = r'(ДАННОЕ СООБЩЕНИЕ|НАСТОЯЩИЙ МАТЕРИАЛ) [-,\.()\w ]+ ИНОСТРАНН(ОГО|ЫХ) АГЕНТ(А|ОВ)[\.)]*'

INOS_JSON_FILENAME = 'inos.json'
TOKEN_FILENAME = 'token.txt'

TELEGRAM_URL_PREFIX = 'https://t.me/'
INO_URL_PREFIX = f'{TELEGRAM_URL_PREFIX}s/'
INO_PREFIXES = (INO_URL_PREFIX, TELEGRAM_URL_PREFIX, '@')

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
