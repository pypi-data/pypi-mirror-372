__all__ = ["KKBox", "KKBoxException"]

import os
from dataclasses import asdict
from pprint import pprint
from typing import Optional

import requests
from dotenv import load_dotenv

from yutipy.base_clients import BaseClient
from yutipy.exceptions import InvalidValueException, KKBoxException
from yutipy.logger import logger
from yutipy.lrclib import LrcLib
from yutipy.models import MusicInfo
from yutipy.utils.helpers import are_strings_similar, is_valid_string

load_dotenv()

KKBOX_CLIENT_ID = os.getenv("KKBOX_CLIENT_ID")
KKBOX_CLIENT_SECRET = os.getenv("KKBOX_CLIENT_SECRET")


class KKBox(BaseClient):
    """
    A class to interact with KKBOX Open API.

    This class reads the ``KKBOX_CLIENT_ID`` and ``KKBOX_CLIENT_SECRET`` from environment variables or the ``.env`` file by default.
    Alternatively, you can manually provide these values when creating an object.
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        defer_load: bool = False,
        fetch_lyrics: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        client_id : str, optional
            The Client ID for the KKBOX Open API. Defaults to ``KKBOX_CLIENT_ID`` from .env file.
        client_secret : str, optional
            The Client secret for the KKBOX Open API. Defaults to ``KKBOX_CLIENT_SECRET`` from .env file.
        defer_load : bool, optional
            Whether to defer loading the access token during initialization. Default is ``False``.
        fetch_lyrics : bool, optional
            Whether to fetch lyrics (using `LRCLIB <https://lrclib.net>`__) if the music platform does not provide lyrics (default is True).
        """
        self.client_id = client_id or KKBOX_CLIENT_ID
        self.client_secret = client_secret or KKBOX_CLIENT_SECRET
        self.fetch_lyrics = fetch_lyrics

        if not self.client_id:
            raise KKBoxException(
                "Client ID was not found. Set it in environment variable or directly pass it when creating object."
            )

        if not self.client_secret:
            raise KKBoxException(
                "Client Secret was not found. Set it in environment variable or directly pass it when creating object."
            )

        super().__init__(
            service_name="KKBox",
            access_token_url="https://account.kkbox.com/oauth2/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            defer_load=defer_load,
        )

        self.__api_url = "https://api.kkbox.com/v1.1"
        self._valid_territories = ["HK", "JP", "MY", "SG", "TW"]

    def search(
        self,
        artist: str,
        song: str,
        territory: str = "TW",
        limit: int = 10,
        normalize_non_english: bool = True,
    ) -> Optional[MusicInfo]:
        """
        Searches for a song by artist and title.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        territory : str
            Two-letter country codes from ISO 3166-1 alpha-2.
            Allowed values: ``HK``, ``JP``, ``MY``, ``SG``, ``TW``.
        limit: int, optional
            The number of items to retrieve from API. ``limit >=1 and <= 50``. Default is ``10``.
        normalize_non_english : bool, optional
            Whether to normalize non-English characters for comparison. Default is ``True``.

        Returns
        -------
        Optional[MusicInfo_]
            The music information if found, otherwise None.
        """
        if not is_valid_string(artist) or not is_valid_string(song):
            raise InvalidValueException(
                "Artist and song names must be valid strings and can't be empty."
            )

        self._normalize_non_english = normalize_non_english
        self._refresh_access_token()

        query = (
            f"?q={artist} - {song}&type=track,album&territory={territory}&limit={limit}"
        )
        query_url = f"{self.__api_url}/search{query}"

        logger.info(f"Searching KKBOX for `artist='{artist}'` and `song='{song}'`")
        logger.debug(f"Query URL: {query_url}")

        try:
            response = self._session.get(
                query_url, headers=self._authorization_header(), timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Unexpected error while searching KKBox: {e}")
            return None

        return self._find_music_info(artist, song, response.json())

    def get_html_widget(
        self,
        id: str,
        content_type: str,
        territory: str = "TW",
        widget_lang: str = "EN",
        autoplay: bool = False,
        loop: bool = False,
    ) -> str:
        """
        Return KKBOX HTML widget for "Playlist", "Album" or "Song". It does not return actual HTML code,
        the URL returned can be used in an HTML ``iframe`` with the help of ``src`` attribute.

        Parameters
        ----------
        id : str
             ``ID`` of playlist, album or track.
        content_type : str
            Content type can be ``playlist``, ``album`` or ``song``.
        territory : str, optional
            Territory code, i.e. "TW", "HK", "JP", "SG", "MY", by default "TW"
        widget_lang : str, optional
            The display language of the widget. Can be "TC", "SC", "JA", "EN", "MS", by default "EN"
        autoplay : bool, optional
            Whether to start playing music automatically in widget, by default False
        loop : bool, optional
            Repeat/loop song(s), by default False

        Returns
        -------
        str
            KKBOX HTML widget URL.
        """
        valid_content_types = ["playlist", "album", "song"]
        valid_widget_langs = ["TC", "SC", "JA", "EN", "MS"]
        if content_type not in valid_content_types:
            raise InvalidValueException(
                f"`content_type` must be one of these: {valid_content_types} !"
            )

        if territory not in self._valid_territories:
            raise InvalidValueException(
                f"`territory` must be one of these: {self._valid_territories} !"
            )

        if widget_lang not in valid_widget_langs:
            raise InvalidValueException(
                f"`widget_lang` must be one of these: {valid_widget_langs} !"
            )

        return f"https://widget.kkbox.com/v1/?id={id}&type={content_type}&terr={territory}&lang={widget_lang}&autoplay={autoplay}&loop={loop}"

    def _find_music_info(
        self, artist: str, song: str, response_json: dict
    ) -> Optional[MusicInfo]:
        """
        Finds the music information from the search results.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        response_json : dict
            The JSON response from the API.

        Returns
        -------
        Optional[MusicInfo]
            The music information if found, otherwise None.
        """
        try:
            for track in response_json["tracks"]["data"]:
                music_info = self._find_track(song, artist, track)
                if music_info:
                    return music_info
        except KeyError:
            pass

        try:
            for album in response_json["albums"]["data"]:
                music_info = self._find_album(song, artist, album)
                if music_info:
                    return music_info
        except KeyError:
            pass

        logger.warning(
            f"No matching results found for artist='{artist}' and song='{song}'"
        )
        return None

    def _find_track(self, song: str, artist: str, track: dict) -> Optional[MusicInfo]:
        """
        Finds the track information from the search results.

        Parameters
        ----------
        song : str
            The title of the song.
        artist : str
            The name of the artist.
        track : dict
            A single track from the search results.

        Returns
        -------
        Optional[MusicInfo]
            The music information if found, otherwise None.
        """
        if not are_strings_similar(
            track["name"],
            song,
            use_translation=self._normalize_non_english,
            translation_session=self._translation_session,
        ):
            return None

        artists_name = track.get("album", {}).get("artist", {}).get("name")
        matching_artists = (
            artists_name
            if are_strings_similar(
                artists_name,
                artist,
                use_translation=self._normalize_non_english,
                translation_session=self._translation_session,
            )
            else None
        )

        if matching_artists:
            music_info = MusicInfo(
                album_art=track.get("album", {}).get("images", [])[2]["url"],
                album_title=track.get("album", {}).get("name"),
                album_type=None,
                artists=artists_name,
                genre=None,
                id=track.get("id"),
                isrc=track.get("isrc"),
                lyrics=None,
                release_date=track.get("album", {}).get("release_date"),
                tempo=None,
                title=track.get("name"),
                type="track",
                upc=None,
                url=track.get("url"),
            )

            if self.fetch_lyrics:
                with LrcLib() as lrc_lib:
                    lyrics = lrc_lib.get_lyrics(
                        artist=music_info.artists, song=music_info.title
                    )
                if lyrics:
                    music_info.lyrics = lyrics.get("plainLyrics")
            return music_info
        return None

    def _find_album(self, song: str, artist: str, album: dict) -> Optional[MusicInfo]:
        """
        Finds the album information from the search results.

        Parameters
        ----------
        song : str
            The title of the song.
        artist : str
            The name of the artist.
        album : dict
            A single album from the search results.

        Returns
        -------
        Optional[MusicInfo]
            The music information if found, otherwise None.
        """
        if not are_strings_similar(
            album["name"],
            song,
            use_translation=self._normalize_non_english,
            translation_session=self._translation_session,
        ):
            return None

        artists_name = album.get("artist", {}).get("name")
        matching_artists = (
            artists_name
            if are_strings_similar(
                artists_name,
                artist,
                use_translation=self._normalize_non_english,
                translation_session=self._translation_session,
            )
            else None
        )

        if matching_artists:
            return MusicInfo(
                album_art=album.get("images", [])[2]["url"],
                album_title=album.get("name"),
                album_type=None,
                artists=artists_name,
                genre=None,
                id=album.get("id"),
                isrc=None,
                lyrics=None,
                release_date=album.get("release_date"),
                tempo=None,
                title=album.get("name"),
                type="album",
                upc=None,
                url=album.get("url"),
            )

        return None


if __name__ == "__main__":
    import logging

    from yutipy.logger import enable_logging

    enable_logging(level=logging.DEBUG)
    kkbox = KKBox()

    try:
        artist_name = input("Artist Name: ")
        song_name = input("Song Name: ")
        result = kkbox.search(artist_name, song_name)
        pprint(asdict(result))
    finally:
        kkbox.close_session()
