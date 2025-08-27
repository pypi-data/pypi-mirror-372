from yutipy.models import MusicInfo, MusicInfos, UserPlaying


def test_music_info():
    music_info = MusicInfo(
        album_art="https://example.com/album_art.jpg",
        album_title="Album Title",
        album_type="album",
        artists="Artist Name",
        genre="Pop",
        id="12345",
        isrc="US1234567890",
        lyrics="Some lyrics",
        release_date="2023-01-01",
        tempo=120.0,
        title="Song Title",
        type="track",
        upc="123456789012",
        url="https://example.com/song",
    )

    assert music_info.album_art == "https://example.com/album_art.jpg"
    assert music_info.album_title == "Album Title"
    assert music_info.album_type == "album"
    assert music_info.artists == "Artist Name"
    assert music_info.genre == "Pop"
    assert music_info.id == "12345"
    assert music_info.isrc == "US1234567890"
    assert music_info.lyrics == "Some lyrics"
    assert music_info.release_date == "2023-01-01"
    assert abs(music_info.tempo - 120.0) < 1e-6
    assert music_info.title == "Song Title"
    assert music_info.type == "track"
    assert music_info.upc == "123456789012"
    assert music_info.url == "https://example.com/song"


def test_music_infos():
    music_infos = MusicInfos(album_art_source="Example Source")

    assert music_infos.album_art_source == "Example Source"
    assert isinstance(music_infos.album_art_source, str)


def test_user_playing():
    user_playing = UserPlaying(is_playing=False)

    assert user_playing.is_playing is False
    assert isinstance(user_playing.is_playing, bool)
