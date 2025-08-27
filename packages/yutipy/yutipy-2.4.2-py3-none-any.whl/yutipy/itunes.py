__all__ = ["Itunes", "ItunesException"]

from datetime import datetime
from pprint import pprint
from typing import Optional

import requests

from yutipy.exceptions import InvalidValueException, ItunesException
from yutipy.logger import logger
from yutipy.lrclib import LrcLib
from yutipy.models import MusicInfo
from yutipy.utils.helpers import (
    are_strings_similar,
    guess_album_type,
    is_valid_string,
    separate_artists,
)


class Itunes:
    """A class to interact with the iTunes API."""

    def __init__(self, fetch_lyrics: bool = True) -> None:
        """
        Parameters
        ----------
        fetch_lyrics : bool, optional
            Whether to fetch lyrics (using `LRCLIB <https://lrclib.net>`__) if the music platform does not provide lyrics (default is True).
        """
        self.api_url = "https://itunes.apple.com"
        self.normalize_non_english = True
        self._is_session_closed = False
        self.fetch_lyrics = fetch_lyrics
        self.__session = requests.Session()
        self.__translation_session = requests.Session()

    def __enter__(self):
        """Enters the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Exits the runtime context related to this object."""
        self.close_session()

    def close_session(self) -> None:
        """Closes the current session."""
        if not self.is_session_closed:
            self.__session.close()
            self.__translation_session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        """Checks if the session is closed."""
        return self._is_session_closed

    def search(
        self,
        artist: str,
        song: str,
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

        self.normalize_non_english = normalize_non_english

        entities = ["song", "album"]
        for entity in entities:
            endpoint = f"{self.api_url}/search"
            query = f"?term={artist} - {song}&media=music&entity={entity}&limit={limit}"
            query_url = endpoint + query

            try:
                logger.info(
                    f'Searching iTunes for `artist="{artist}"` and `song="{song}"`'
                )
                logger.debug(f"Query URL: {query_url}")
                response = self.__session.get(query_url, timeout=30)
                logger.debug(f"Response status code: {response.status_code}")
                response.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"Unexpected error while searching iTunes: {e}")
                return None

            try:
                logger.debug("Parsing response JSON.")
                result = response.json()["results"]
            except (IndexError, KeyError, ValueError) as e:
                logger.warning(f"Invalid response structure from iTunes: {e}")
                return None

            music_info = self._parse_result(artist, song, result)
            if music_info:
                return music_info

        logger.warning(
            f"No matching results found for artist='{artist}' and song='{song}'"
        )
        return None

    def _parse_result(
        self, artist: str, song: str, results: list[dict]
    ) -> Optional[MusicInfo]:
        """
        Parses the search results to find a matching song.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        results : list
            The search results from the API.

        Returns
        -------
        Optional[MusicInfo]
            The music information if a match is found, otherwise None.
        """
        for result in results:
            if not (
                are_strings_similar(
                    result.get("trackName", result["collectionName"]),
                    song,
                    use_translation=self.normalize_non_english,
                    translation_session=self.__translation_session,
                )
                and are_strings_similar(
                    result["artistName"],
                    artist,
                    use_translation=self.normalize_non_english,
                    translation_session=self.__translation_session,
                )
            ):
                continue

            album_title, album_type = self._extract_album_info(result)
            release_date = self._format_release_date(result["releaseDate"])
            artists = separate_artists(result["artistName"])

            music_info = MusicInfo(
                album_art=result["artworkUrl100"],
                album_title=album_title,
                album_type=album_type.lower(),
                artists=", ".join(artists),
                genre=result["primaryGenreName"],
                id=result.get("trackId", result["collectionId"]),
                isrc=None,
                lyrics=None,
                release_date=release_date,
                tempo=None,
                title=result.get("trackName", album_title),
                type=result["wrapperType"],
                upc=None,
                url=result.get("trackViewUrl", result["collectionViewUrl"]),
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

    def _extract_album_info(self, result: dict) -> tuple:
        """
        Extracts album information from a search result.

        Parameters
        ----------
        result : dict
            A single search result from the API.

        Returns
        -------
        tuple
            The extracted album title and type.
        """

        guess = guess_album_type(result.get("trackCount", 1))
        guessed_right = are_strings_similar(
            result.get("wrapperType", "x"), guess, use_translation=False
        )
        return result["collectionName"], (
            result["wrapperType"] if guessed_right else guess
        )

    def _format_release_date(self, release_date: str) -> str:
        """
        Formats the release date to a standard format.

        Parameters
        ----------
        release_date : str
            The release date from the API.

        Returns
        -------
        str
            The formatted release date.
        """
        return datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m-%d"
        )


if __name__ == "__main__":
    import logging

    from yutipy.logger import enable_logging

    enable_logging(level=logging.DEBUG)
    itunes = Itunes()

    try:
        artist_name = input("Artist Name: ")
        song_name = input("Song Name: ")
        pprint(itunes.search(artist_name, song_name))
    finally:
        itunes.close_session()
