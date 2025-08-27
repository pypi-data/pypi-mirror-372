__all__ = ["Deezer", "DeezerException"]

from pprint import pprint
from typing import Dict, List, Optional

import requests

from yutipy.exceptions import DeezerException, InvalidValueException
from yutipy.logger import logger
from yutipy.models import MusicInfo
from yutipy.utils.helpers import are_strings_similar, is_valid_string
from yutipy.lrclib import LrcLib


class Deezer:
    """A class to interact with the Deezer API."""

    def __init__(self, fetch_lyrics: bool = True) -> None:
        """
        Parameters
        ----------
        fetch_lyrics : bool, optional
            Whether to fetch lyrics (using `LRCLIB <https://lrclib.net>`__) if the music platform does not provide lyrics (default is True).
        """
        self.api_url = "https://api.deezer.com"
        self._is_session_closed = False
        self.normalize_non_english = True
        self.fetch_lyrics = fetch_lyrics
        self.__session = requests.Session()
        self._translation_session = requests.Session()

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
            self._translation_session.close()
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

        search_types = ["track", "album"]
        for search_type in search_types:
            endpoint = f"{self.api_url}/search/{search_type}"
            query = f'?q=artist:"{artist}" {search_type}:"{song}"&limit={limit}'
            query_url = endpoint + query

            try:
                logger.info(
                    f'Searching music info for `artist="{artist}"` and `song="{song}"`'
                )
                logger.debug(f"Query URL: {query_url}")
                response = self.__session.get(query_url, timeout=30)
                logger.debug(f"Response status code: {response.status_code}")
                response.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"Unexpected error while searching Deezer: {e}")
                return None

            try:
                logger.debug("Parsing response JSON.")
                result = response.json()["data"]
            except (IndexError, KeyError, ValueError) as e:
                logger.warning(f"Invalid response structure from Deezer: {e}")
                return None

            music_info = self._parse_results(artist, song, result)
            if music_info:
                return music_info

        logger.warning(
            f"No matching results found for artist='{artist}' and song='{song}'"
        )
        return None

    def _get_upc_isrc(self, music_id: int, music_type: str) -> Optional[Dict]:
        """
        Retrieves UPC and ISRC information for a given music ID and type.

        Parameters
        ----------
        music_id : int
            The ID of the music.
        music_type : str
            The type of the music (track or album).

        Returns
        -------
        Optional[Dict]
            A dictionary containing UPC and ISRC information.
        """
        if music_type == "track":
            return self._get_track_info(music_id)
        elif music_type == "album":
            return self._get_album_info(music_id)
        else:
            raise InvalidValueException(f"Invalid music type: {music_type}")

    def _get_track_info(self, track_id: int) -> Optional[Dict]:
        """
        Retrieves track information for a given track ID.

        Parameters
        ----------
        music_id : int
            The ID of the track.

        Returns
        -------
        Optional[Dict]
            A dictionary containing track information.
        """
        query_url = f"{self.api_url}/track/{track_id}"
        try:
            logger.info(f"Fetching track info for track_id: {track_id}")
            logger.debug(f"Query URL: {query_url}")
            response = self.__session.get(query_url, timeout=30)
            logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Error fetching track info: {e}")
            return None

        try:
            logger.debug("Parsing Response JSON.")
            result = response.json()
        except ValueError as e:
            logger.warning(f"Invalid response received from Deezer: {e}")
            return None

        return {
            "isrc": result.get("isrc"),
            "release_date": result.get("release_date"),
            "tempo": result.get("bpm"),
        }

    def _get_album_info(self, album_id: int) -> Optional[Dict]:
        """
        Retrieves album information for a given album ID.

        Parameters
        ----------
        music_id : int
            The ID of the album.

        Returns
        -------
        Optional[Dict]
            A dictionary containing album information.
        """
        query_url = f"{self.api_url}/album/{album_id}"
        try:
            logger.info(f"Fetching album info for album_id: {album_id}")
            logger.debug(f"Query URL: {query_url}")
            response = self.__session.get(query_url, timeout=30)
            logger.info(f"Response status code: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Error fetching album info: {e}")
            return None

        try:
            logger.debug(f"Response JSON: {response.json()}")
            result = response.json()
        except ValueError as e:
            logger.warning(f"Invalid response received from Deezer: {e}")
            return None

        return {
            "genre": (
                result["genres"]["data"][0]["name"]
                if result["genres"]["data"]
                else None
            ),
            "release_date": result.get("release_date"),
            "upc": result.get("upc"),
        }

    def _parse_results(
        self, artist: str, song: str, results: List[Dict]
    ) -> Optional[MusicInfo]:
        """
        Parses the search results to find a matching song.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        results : List[Dict]
            The search results from the API.

        Returns
        -------
        Optional[MusicInfo]
            The music information if a match is found, otherwise None.
        """
        for result in results:
            if not (
                are_strings_similar(
                    result["title"],
                    song,
                    use_translation=self.normalize_non_english,
                    translation_session=self._translation_session,
                )
                and are_strings_similar(
                    result["artist"]["name"],
                    artist,
                    use_translation=self.normalize_non_english,
                    translation_session=self._translation_session,
                )
            ):
                continue

            return self._extract_music_info(result)

        return None

    def _extract_music_info(self, result: Dict) -> MusicInfo:
        """
        Extracts music information from a search result.

        Parameters
        ----------
        result : Dict
            A single search result from the API.

        Returns
        -------
        MusicInfo
            The extracted music information.
        """
        music_type = result["type"]
        music_info = MusicInfo(
            album_art=(
                result["album"]["cover_xl"]
                if music_type == "track"
                else result["cover_xl"]
            ),
            album_title=(
                result["album"]["title"] if music_type == "track" else result["title"]
            ),
            album_type=result.get("record_type", music_type.replace("track", "single")),
            artists=result["artist"]["name"],
            genre=None,
            id=result["id"],
            isrc=None,
            lyrics=None,
            release_date=None,
            tempo=None,
            title=result["title"],
            type=music_type,
            upc=None,
            url=result["link"],
        )

        if music_type == "track":
            track_info = self._get_upc_isrc(result["id"], music_type)
            music_info.isrc = track_info.get("isrc")
            music_info.release_date = track_info.get("release_date")
            music_info.tempo = track_info.get("tempo")
        else:
            album_info = self._get_upc_isrc(result["id"], music_type)
            music_info.upc = album_info.get("upc")
            music_info.release_date = album_info.get("release_date")
            music_info.genre = album_info.get("genre")

        if self.fetch_lyrics:
            with LrcLib() as lrc_lib:
                lyrics = lrc_lib.get_lyrics(
                    artist=music_info.artists, song=music_info.title
                )
            if lyrics:
                music_info.lyrics = lyrics.get("plainLyrics")

        return music_info


if __name__ == "__main__":
    import logging

    from yutipy.logger import enable_logging

    enable_logging(level=logging.DEBUG)
    deezer = Deezer()
    try:
        artist_name = input("Artist Name: ")
        song_name = input("Song Name: ")
        pprint(deezer.search(artist_name, song_name))
    finally:
        deezer.close_session()
