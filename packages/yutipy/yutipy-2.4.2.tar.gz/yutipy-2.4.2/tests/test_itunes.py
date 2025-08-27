import pytest
from pytest import raises

from tests import BaseResponse
from yutipy.exceptions import InvalidValueException
from yutipy.itunes import Itunes
from yutipy.models import MusicInfo


@pytest.fixture
def itunes():
    return Itunes()


class MockResponse(BaseResponse):
    @staticmethod
    def json():
        return {
            "results": [
                {
                    "wrapperType": "track",
                    "kind": "song",
                    "collectionId": 12345678,
                    "trackId": 91011123,
                    "artistName": "Artist X",
                    "collectionName": "Test Album",
                    "trackName": "Test Track",
                    "collectionViewUrl": "https://itunes.apple.com/12345678",
                    "trackViewUrl": "https://itunes.apple.com/91011123",
                    "artworkUrl100": "https://example.com/image/12345678",
                    "trackCount": 14,
                    "releaseDate": "2016-08-11T12:00:00Z",
                    "primaryGenreName": "Rock",
                }
            ]
        }


@pytest.fixture
def mock_response(itunes, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(itunes._Itunes__session, "get", mock_get)


def test_search_valid(itunes, mock_response):
    artist = "Artist X"
    song = "Test Track"
    result = itunes.search(artist, song, normalize_non_english=False)
    assert result is not None
    assert isinstance(result, MusicInfo)
    assert result.artists == artist
    assert result.title == song


def test_search_invalid(itunes, mock_response):
    artist = "Nonexistent Artist"
    song = "Nonexistent Song"
    result = itunes.search(artist, song, normalize_non_english=False)
    assert result is None


def test_search_empty_artist(itunes, mock_response):
    artist = ""
    song = "Test Track"

    with raises(InvalidValueException):
        itunes.search(artist, song)


def test_search_empty_song(itunes, mock_response):
    artist = "Artist X"
    song = ""

    with raises(InvalidValueException):
        itunes.search(artist, song)


def test_close_session(itunes):
    itunes.close_session()
    assert itunes.is_session_closed
