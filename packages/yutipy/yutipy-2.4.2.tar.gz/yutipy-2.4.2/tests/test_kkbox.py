import pytest
from pytest import raises

from tests import BaseResponse
from yutipy.exceptions import InvalidValueException
from yutipy.kkbox import KKBox
from yutipy.models import MusicInfo


@pytest.fixture(scope="module")
def kkbox():
    def mock_get_access_token():
        return {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "requested_at": 1234567890,
        }

    kkbox_instance = KKBox(
        client_id="test_client_id", client_secret="test_client_secret", defer_load=True
    )

    kkbox_instance._get_access_token = mock_get_access_token
    kkbox_instance.load_token_after_init()
    return kkbox_instance


class MockResponse(BaseResponse):
    @staticmethod
    def json():
        return {
            "tracks": {
                "data": [
                    {
                        "id": "123456",
                        "name": "Test Track",
                        "isrc": "ISRC",
                        "url": "https://kkbox.com/track/123456",
                        "album": {
                            "id": "78910",
                            "name": "Test Album",
                            "url": "https://kkbox.com/album/78910",
                            "release_date": "2001-10-12",
                            "images": [
                                {"url": "https://example.com/image/78910_128"},
                                {"url": "https://example.com/image/78910_512"},
                                {"url": "https://example.com/image/78910_1000"},
                            ],
                            "artist": {
                                "id": "65791",
                                "name": "Artist X",
                            },
                        },
                    }
                ]
            }
        }


@pytest.fixture
def mock_response(kkbox, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(kkbox._session, "get", mock_get)


def test_search(kkbox, mock_response):
    artist = "Artist X"
    song = "Test Track"
    result = kkbox.search(artist, song, normalize_non_english=False)
    assert result is not None
    assert isinstance(result, MusicInfo)
    assert result.title == song
    assert artist in result.artists


def test_get_html_widget(kkbox):
    html_widget = kkbox.get_html_widget(id="8rceGrek59bDS0HmQH", content_type="song")
    assert html_widget is not None
    assert isinstance(html_widget, str)

    with raises(InvalidValueException):
        kkbox.get_html_widget(id="8rceGrek59bDS0HmQH", content_type="track")

    with raises(InvalidValueException):
        kkbox.get_html_widget(
            id="8rceGrek59bDS0HmQH", content_type="song", territory="US"
        )

    with raises(InvalidValueException):
        kkbox.get_html_widget(
            id="8rceGrek59bDS0HmQH", content_type="song", widget_lang="JP"
        )


def test_close_session(kkbox):
    kkbox.close_session()
    assert kkbox.is_session_closed
