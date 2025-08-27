import pytest

from yutipy.lastfm import LastFm
from yutipy.models import UserPlaying
from tests import BaseResponse


@pytest.fixture
def lastfm():
    return LastFm(api_key="test_api_key")


class MockResponseActivity(BaseResponse):
    @staticmethod
    def json():
        return {
            "recenttracks": {
                "track": [
                    {
                        "artist": {"mbid": "", "#text": "Test Artist"},
                        "image": [
                            {
                                "size": "small",
                                "#text": "https://example.com/image/small.jpg",
                            },
                            {
                                "size": "extralarge",
                                "#text": "https://example.com/image/extralarge.jpg",
                            },
                        ],
                        "mbid": "",
                        "album": {
                            "mbid": "",
                            "#text": "Test Album",
                        },
                        "name": "Test Track",
                        "@attr": {"nowplaying": "true"},
                        "url": "https://www.last.fm/music/test+track",
                    }
                ]
            }
        }


class MockResponseProfile(BaseResponse):
    @staticmethod
    def json():
        return {
            "user": {
                "name": "john",
                "realname": "Real John",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://example.com/image/john",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://example.com/image/john",
                    },
                ],
                "url": "https://example.com/john",
                "type": "user",
            }
        }


@pytest.fixture
def mock_response_activity(lastfm, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseActivity()

    monkeypatch.setattr(lastfm._LastFm__session, "get", mock_get)


@pytest.fixture
def mock_response_profile(lastfm, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseProfile()

    monkeypatch.setattr(lastfm._LastFm__session, "get", mock_get)


def test_get_currently_playing(lastfm, mock_response_activity):
    username = "bob"
    currently_playing = lastfm.get_currently_playing(username=username)
    assert currently_playing is not None
    assert isinstance(currently_playing, UserPlaying)
    assert currently_playing.title == "Test Track"
    assert currently_playing.album_title == "Test Album"
    assert "extralarge" in currently_playing.album_art
    assert currently_playing.is_playing is True


def test_get_user_profile(lastfm, mock_response_profile):
    username = "john"
    profile = lastfm.get_user_profile(username=username)
    assert profile is not None
    assert profile["username"] == username
    assert profile["name"] == "Real John"
    assert profile["type"] == "user"


def test_invalid_username(lastfm, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse(BaseResponse):
            @staticmethod
            def json():
                return {"message": "User not found", "error": 6}

        return MockResponse()

    monkeypatch.setattr(lastfm._LastFm__session, "get", mock_get)

    username = "alksdjfalsjdfweurppqoweiuwu"
    profile = lastfm.get_user_profile(username=username)
    assert profile is not None
    assert "error" in profile
