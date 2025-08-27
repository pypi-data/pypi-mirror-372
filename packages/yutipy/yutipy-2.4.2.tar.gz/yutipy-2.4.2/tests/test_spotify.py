import pytest

from tests import BaseResponse
from yutipy.models import MusicInfo, UserPlaying
from yutipy.spotify import Spotify, SpotifyAuth


@pytest.fixture(scope="module")
def spotify():
    def mock_get_access_token():
        return {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "requested_at": 1234567890,
        }

    spotify_instance = Spotify(
        client_id="test_client_id",
        client_secret="test_client_secret",
        defer_load=True
    )

    spotify_instance._get_access_token = mock_get_access_token
    spotify_instance.load_token_after_init()
    return spotify_instance


@pytest.fixture(scope="module")
def spotify_auth():
    def mock_get_access_token(*args, **kwargs):
        return {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "requested_at": 1234567890,
        }

    spotify_instance = SpotifyAuth(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost/callback",
        scopes=["user-read-email", "user-read-private"],
        defer_load=True
    )

    spotify_instance._get_access_token = mock_get_access_token
    spotify_instance.load_token_after_init()
    return spotify_instance


# Custom class to be the mock return value of requests.get()
# for `Spotify` class only ~
class MockResponse(BaseResponse):
    @staticmethod
    def json():
        return {
            "albums": {
                "items": [
                    {
                        "album_type": "album",
                        "total_tracks": 15,
                        "external_urls": {
                            "spotify": "https://open.spotify.com/album/adbjkl234"
                        },
                        "id": "asdfjkl",
                        "images": [{"url": "https://example.com/image/asdfjkl2345"}],
                        "name": "Test Album",
                        "release_date": "1981-12-10",
                        "type": "album",
                        "artists": [{"id": "abc-xyz", "name": "Artist X"}],
                    }
                ]
            },
            "tracks": {
                "items": [
                    {
                        "album": {
                            "album_type": "single",
                            "total_tracks": 1,
                            "id": "lkjfdsa",
                            "images": [
                                {
                                    "url": "https://example.com/image/ewo35623131lf",
                                }
                            ],
                            "name": "Test Album",
                            "release_date": "1981-12-10",
                            "type": "album",
                        },
                        "artists": [
                            {"id": "abc-xyz", "name": "Artist X"},
                            {"id": "123-xyz", "name": "Artist Y"},
                        ],
                        "external_ids": {"isrc": "ISRC", "upc": "UPC"},
                        "external_urls": {
                            "spotify": "https://open.spotify.com/track/abcd123xyz"
                        },
                        "id": "abcd123xyz",
                        "name": "Test Track",
                        "type": "track",
                    }
                ]
            },
            "artists": {
                "items": [
                    {"id": "abc-xyz", "name": "Artist X"},
                    {"id": "123-xyz", "name": "Artist Y"},
                ]
            },
        }


@pytest.fixture
def mock_response(spotify, monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(spotify._session, "get", mock_get)


def test_search(spotify, mock_response):
    artist = "Artist X"
    song = "Test Track"
    result = spotify.search(artist, song, normalize_non_english=False)
    assert result is not None
    assert isinstance(result, MusicInfo)
    assert result.title == song
    assert artist in result.artists


def test_search_advanced_with_isrc(spotify, mock_response):
    artist = "Artist Y"
    song = "Test Track"
    isrc = "ISRC"
    result = spotify.search_advanced(
        artist, song, isrc=isrc, normalize_non_english=False
    )
    assert result is not None
    assert result.isrc == isrc


def test_search_advanced_with_upc(spotify, mock_response):
    artist = "Artist X"
    album = "Test Album"
    upc = "UPC"
    result = spotify.search_advanced(
        artist, album, upc=upc, normalize_non_english=False
    )
    print(result)
    assert result is not None


def test_get_artists_ids(spotify, mock_response):
    artist = "Artist Y"
    artist_ids = spotify._get_artists_ids(artist)
    assert isinstance(artist_ids, list)
    assert len(artist_ids) > 0


def test_close_session(spotify):
    spotify.close_session()
    assert spotify.is_session_closed


def test_get_authorization_url(spotify_auth):
    state = spotify_auth.generate_state()
    auth_url = spotify_auth.get_authorization_url(state=state)
    assert "https://accounts.spotify.com/authorize" in auth_url
    assert "response_type=code" in auth_url
    assert f"client_id={spotify_auth.client_id}" in auth_url


def test_callback_handler(spotify_auth, monkeypatch):
    spotify_auth.callback_handler("test_code", "test_state", "test_state")
    assert spotify_auth._access_token == "test_access_token"
    assert spotify_auth._refresh_token == "test_refresh_token"
    assert spotify_auth._token_expires_in == 3600
    assert spotify_auth._token_requested_at == 1234567890


def test_get_currently_playing(spotify_auth, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse(BaseResponse):
            @staticmethod
            def json():
                return {
                    "timestamp": 1745797530935,
                    "is_playing": False,
                    "item": {
                        "album": {
                            "album_type": "album",
                            "total_tracks": 9,
                            "images": [
                                {
                                    "url": "https://example.com/image/ewo35623131lf",
                                }
                            ],
                            "name": "Test Album",
                            "release_date": "1981-12-10",
                            "type": "album",
                        },
                        "artists": [
                            {"name": "Artist X", "type": "artist"},
                            {"name": "Artist Y", "type": "artist"},
                        ],
                        "external_ids": {"isrc": "ISRC", "upc": "UPC"},
                        "external_urls": {
                            "spotify": "https://open.spotify.com/track/abcd123xyz"
                        },
                        "id": "abcd123xyz",
                        "name": "Test Track",
                        "type": "track",
                    },
                }

        return MockResponse()

    monkeypatch.setattr(spotify_auth._session, "get", mock_get)

    currently_playing = spotify_auth.get_currently_playing()
    assert currently_playing is not None
    assert isinstance(currently_playing, UserPlaying)
    assert currently_playing.title == "Test Track"
    assert currently_playing.artists == "Artist X, Artist Y"
    assert currently_playing.type == "track"


def test_get_user_profile(spotify_auth, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse(BaseResponse):
            @staticmethod
            def json():
                return {
                    "display_name": "Test User",
                    "images": [
                        {
                            "url": "https://example.com/image.jpg",
                            "height": 300,
                            "width": 300,
                        }
                    ],
                }

        return MockResponse()

    monkeypatch.setattr(spotify_auth._session, "get", mock_get)

    user_profile = spotify_auth.get_user_profile()
    assert user_profile is not None
    assert user_profile["display_name"] == "Test User"
    assert len(user_profile["images"]) == 1
    assert user_profile["images"][0]["url"] == "https://example.com/image.jpg"
