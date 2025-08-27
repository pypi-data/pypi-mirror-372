__all__ = ["LrcLib"]

from importlib.metadata import PackageNotFoundError, version
from typing import Optional

import requests

from yutipy.exceptions import InvalidValueException
from yutipy.logger import logger
from yutipy.utils import are_strings_similar, is_valid_string


class LrcLib:
    """
    A class to interact with the `LRCLIB <lrclib.net>`_ API for fetching lyrics.
    """

    def __init__(
        self,
        app_name: str = "yutipy",
        app_version: str = None,
        app_url: str = "https://github.com/CheapNightbot/yutipy",
    ) -> None:
        """
        Parameters
        ----------
        app_name : str
            The name of the application.
        app_version : str, optional
            The version of the application.
        app_url : str, optional
            The URL of the application.

        Notes
        -----
        These are used to set the User-Agent header for requests made to the API as suggested by the API documentation of `LRCLIB <lrclib.net>`_.
        """
        self.api_url = "https://lrclib.net/api"
        self.app_name = app_name
        self.app_url = app_url
        if not app_version:
            try:
                self.app_version = f"v{version('yutipy')}"
            except PackageNotFoundError:
                self.app_version = "N/A"
        else:
            self.app_version = app_version

        self._is_session_closed = False
        self.__session = requests.Session()
        self.__session.headers.update(
            {"User-Agent": f"{self.app_name} {self.app_version} ({self.app_url})"}
        )
        self._translation_session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_session()

    def close_session(self):
        """
        Closes the session if it is not already closed.
        """
        if not self._is_session_closed:
            self.__session.close()
            self._translation_session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        return self._is_session_closed

    def get_lyrics(
        self,
        artist: str,
        song: str,
        album: str = None,
        normalize_non_english: bool = True,
    ) -> Optional[dict]:
        """
        Fetches lyrics for a given artist and song.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        album : str, optional
            The title of the album.
        normalize_non_english : bool, optional
            Whether to normalize non-English characters for comparison (default is True).

        Returns
        -------
        Optional[dict]
            The lyrics information if found, otherwise None.
        """

        if not is_valid_string(artist) or not is_valid_string(song):
            raise InvalidValueException(
                "Artist and song names must be valid strings and can't be empty."
            )

        endpoint = f"{self.api_url}/search"
        query = f"?artist_name={artist}&track_name={song}"
        query += f"&album_name={album}" if album else ""
        query_url = endpoint + query

        try:
            logger.info(
                f"Fetching lyrics for artist: {artist}, song: {song}, album: {album}"
            )
            response = self.__session.get(query_url, timeout=30)
            logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Unexpected error while fetching lyrics: {e}")
            return

        results = response.json()

        for result in results:
            if are_strings_similar(
                result.get("trackName"),
                song,
                use_translation=normalize_non_english,
                translation_session=self._translation_session,
            ) and are_strings_similar(
                result.get("artistName"),
                artist,
                use_translation=normalize_non_english,
                translation_session=self._translation_session,
            ):
                if album and not are_strings_similar(
                    result.get("albumName"),
                    album,
                    use_translation=normalize_non_english,
                    translation_session=self._translation_session,
                ):
                    continue
                return result
        return None


if __name__ == "__main__":
    import logging

    from yutipy.logger import enable_logging

    enable_logging(level=logging.DEBUG)

    with LrcLib() as lyric_lib:
        artist_name = input("Artist Name: ").strip()
        song_title = input("Song Title: ").strip()
        lyrics = lyric_lib.get_lyrics(artist_name, song_title)
        print(f"\nLyrics for '{song_title}' by {artist_name}:\n{'-' * 40}\n")

        if lyrics:
            print(lyrics.get("plainLyrics"))
        else:
            print(
                "It seems that the lyrics were not found! You might have to guess them..."
            )
