import pytest
from pytest import raises

from yutipy.exceptions import InvalidValueException
from yutipy.models import MusicInfo
from yutipy.musicyt import MusicYT


@pytest.fixture
def music_yt():
    return MusicYT()


@pytest.fixture
def mock_ytmusic_search(music_yt, monkeypatch):
    def mock_search(*args, **kwargs):
        return [
            {
                "category": "Songs",
                "resultType": "song",
                "videoId": "ZrOKjDZOtkA",
                "title": "Test Song",
                "artists": [{"name": "Test Artist", "id": "ADlkasoiuUUer34ldb"}],
                "album": {"name": "Test Album", "id": "MIekd34_934"},
                "microformat": {
                    "microformatDataRenderer": {"uploadDate": "1969-12-31"}
                },
                "thumbnails": [{"url": "https://example.com/image/ZrOKjDZOtkA"}],
            }
        ]

    def mock_get_watch_playlist(*args, **kwargs):
        return {"lyrics": "MPLYt_HNNclO0Ddoc-17"}

    def mock_get_lyrics(*args, **kwargs):
        return {"lyrics": "Never Gonna Give You Up!"}

    # Patch the `search` and other methods of the `YTMusic` class
    monkeypatch.setattr("ytmusicapi.YTMusic.search", mock_search)
    monkeypatch.setattr(
        "ytmusicapi.YTMusic.get_watch_playlist", mock_get_watch_playlist
    )
    monkeypatch.setattr("ytmusicapi.YTMusic.get_lyrics", mock_get_lyrics)


def test_search_valid(music_yt, mock_ytmusic_search):
    artist = "Test Artist"
    song = "Test Song"
    result = music_yt.search(artist, song, normalize_non_english=False)
    assert result is not None
    assert isinstance(result, MusicInfo)
    assert artist in result.artists
    assert result.title == song


def test_search_invalid(music_yt, mock_ytmusic_search):
    artist = ";laksjdflkajsdfj;asdjf"
    song = "jaksjd;fljkas;dfkjasldkjf"
    result = music_yt.search(artist, song)
    assert result is None


def test_search_empty_artist(music_yt, mock_ytmusic_search):
    artist = ""
    song = "Song"

    with raises(InvalidValueException):
        music_yt.search(artist, song, normalize_non_english=False)


def test_search_empty_song(music_yt, mock_ytmusic_search):
    artist = "Artist"
    song = ""

    with raises(InvalidValueException):
        music_yt.search(artist, song, normalize_non_english=False)


def test_close_session(music_yt):
    music_yt.close_session()
    assert music_yt.is_session_closed
