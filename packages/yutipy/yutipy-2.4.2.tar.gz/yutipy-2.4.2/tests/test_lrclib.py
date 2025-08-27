import pytest
from yutipy.lrclib import LrcLib
from yutipy.exceptions import InvalidValueException

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

def test_init_default():
    lib = LrcLib()
    assert lib.api_url == "https://lrclib.net/api"
    assert lib.app_name == "yutipy"
    assert lib.app_url == "https://github.com/CheapNightbot/yutipy"
    assert not lib.is_session_closed


def test_init_custom():
    lib = LrcLib(app_name="foo", app_version="1.2.3", app_url="bar")
    assert lib.app_name == "foo"
    assert lib.app_version == "1.2.3"
    assert lib.app_url == "bar"


def test_get_lyrics_success(monkeypatch):
    # Simulate a successful API response with a matching result
    def mock_get(self, url, timeout):
        return DummyResponse([
            {"trackName": "Song", "artistName": "Artist", "plainLyrics": "Lyrics here"}
        ])
    monkeypatch.setattr("requests.Session.get", mock_get)
    lib = LrcLib()
    result = lib.get_lyrics("Artist", "Song")
    assert result is not None
    assert result["plainLyrics"] == "Lyrics here"


def test_get_lyrics_no_match(monkeypatch):
    def mock_get(self, url, timeout):
        return DummyResponse([])
    monkeypatch.setattr("requests.Session.get", mock_get)
    lib = LrcLib()
    result = lib.get_lyrics("Artist", "Song")
    assert result is None


def test_get_lyrics_invalid(monkeypatch):
    lib = LrcLib()
    with pytest.raises(InvalidValueException):
        lib.get_lyrics("", "Song")
    with pytest.raises(InvalidValueException):
        lib.get_lyrics("Artist", " ")


def test_context_manager(monkeypatch):
    lib = LrcLib()
    with lib as l:
        assert l is lib
    assert lib.is_session_closed


def test_close_session():
    lib = LrcLib()
    lib.close_session()
    assert lib.is_session_closed
    lib.close_session()
    assert lib.is_session_closed
