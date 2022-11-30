import config as cfg
from base import _clear_name
from http_get_posts import _get_ino_url


def test_get_ino_url_than_clear_name() -> None:
    ino_name = 'test'
    assert ino_name == _clear_name(_get_ino_url(ino_name))


def test_clear_name_than_get_ino_url() -> None:
    ino_name = 'test'
    ino_url = cfg.INO_URL_PREFIX + ino_name
    assert ino_url == _get_ino_url(_clear_name(ino_url))
