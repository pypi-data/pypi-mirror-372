import pytest

from tests import BaseResponse
from yutipy.deezer import Deezer
from yutipy.models import MusicInfo


@pytest.fixture
def deezer():
    return Deezer()


# Mock response only for the search endpoint
class MockSearchResponse(BaseResponse):
    @staticmethod
    def json():
        return {
            "data": [
                {
                    "id": "1234567",
                    "title": "Test Track",
                    "link": "https://www.deezer.com/track/1234567",
                    "type": "track",
                    "artist": {"id": "1", "name": "Artist X"},
                    "album": {
                        "id": "110678",
                        "title": "Test Album",
                        "cover_xl": "https://example.com/image/1234567",
                        "type": "album",
                    },
                },
                {
                    "id": "789253",
                    "title": "Test Album",
                    "link": "https://www.deezer.com/track/789253",
                    "type": "album",
                    "cover_xl": "https://example.com/image/789253",
                    "record_type": "album",
                    "artist": {"id": "2", "name": "Artist Y"},
                },
            ]
        }


# Mock response for requesting individual track or album
class MockResponse(BaseResponse):
    @staticmethod
    def json():
        return {
            "id": "1234567",
            "isrc": "ISRC",
            "upc": "UPC",
            "release_date": "2001-03-12",
            "bpm": 0,
            "genres": {
                "data": [
                    {
                        "id": 113,
                        "name": "Dance",
                        "type": "genre",
                    }
                ]
            },
        }


@pytest.fixture
def mock_response(deezer, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockSearchResponse()

    monkeypatch.setattr(deezer._Deezer__session, "get", mock_get)


def test_search_valid(deezer, mock_response):
    result = deezer.search("Artist X", "Test Track", normalize_non_english=False)
    assert result is not None
    assert isinstance(result, MusicInfo)
    assert result.title == "Test Track"


def test_search_invalid(deezer, mock_response):
    result = deezer.search(
        "Nonexistent Artist", "Nonexistent Song", normalize_non_english=False
    )
    assert result is None


def test_get_upc_isrc_track(deezer, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(deezer._Deezer__session, "get", mock_get)

    track_id = 1234567
    result = deezer._get_upc_isrc(track_id, "track")
    assert result is not None
    assert "isrc" in result
    assert "release_date" in result


def test_get_upc_isrc_album(deezer, monkeypatch):

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(deezer._Deezer__session, "get", mock_get)

    album_id = 1234567
    result = deezer._get_upc_isrc(album_id, "album")
    assert result is not None
    assert "upc" in result
    assert "release_date" in result


def test_search_no_results(deezer, mock_response):
    result = deezer.search("Adele", "Nonexistent Song", normalize_non_english=False)
    assert result is None


def test_close_session(deezer):
    deezer.close_session()
    assert deezer.is_session_closed
