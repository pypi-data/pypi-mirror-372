from dataclasses import dataclass, field
from typing import Dict, Optional, Union


@dataclass
class MusicInfo:
    """
    A data class to store music information.

    Attributes
    ----------
    album_art : Optional[str]
        URL to the album art.
    album_title : Optional[str]
        Title of the album.
    album_type : Optional[str]
        Type of the album (e.g., album, single).
    artists : str
        Name(s) of the artist(s).
    genre : Optional[str]
        Genre of the music.
    id : Union[int, str, Dict[str, str]]
        Unique identifier(s) for the music from different platforms.
    isrc : Optional[str]
        International Standard Recording Code.
    lyrics : Optional[str]
        Lyrics of the song.
    release_date : Optional[str]
        Release date of the music.
    tempo : Optional[float]
        Tempo of the music in BPM.
    title : str
        Title of the music.
    type : Optional[str]
        Type of the music (e.g., track, album).
    upc : Optional[str]
        Universal Product Code.
    url : Union[str, Dict[str, str]]
        URL(s) to the music on different platforms.
    """

    album_art: Optional[str] = None
    album_title: Optional[str] = None
    album_type: Optional[str] = None
    artists: str = ""
    genre: Optional[str] = None
    id: Union[int, str, Dict[str, int]] = field(default_factory=dict)
    isrc: Optional[str] = None
    lyrics: Optional[str] = None
    release_date: Optional[str] = None
    tempo: Optional[float] = None
    title: str = ""
    type: Optional[str] = None
    upc: Optional[str] = None
    url: Union[str, Dict[str, str]] = field(default_factory=dict)


@dataclass
class MusicInfos(MusicInfo):
    """A data class to store music information from different services.

    Attributes
    ----------
    album_art_source : Optional[str]
        The source of the album art.
    """

    album_art_source: Optional[str] = None


@dataclass
class UserPlaying(MusicInfo):
    """A data class to store users' currently playing music information.

    Attributes
    ----------
    timetamp : Optional[int]
        Unix Timestamp (in seconds) when playback was started.
    is_playing : Optional[bool]
        Whether the music is currently playing or paused.
    """

    timestamp: Optional[int] = None
    is_playing: Optional[bool] = None
