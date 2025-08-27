__all__ = ["YutipyMusic"]

from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
from typing import Optional

from yutipy.deezer import Deezer
from yutipy.exceptions import InvalidValueException, KKBoxException, SpotifyException
from yutipy.itunes import Itunes
from yutipy.kkbox import KKBox
from yutipy.logger import logger
from yutipy.lrclib import LrcLib
from yutipy.models import MusicInfo, MusicInfos
from yutipy.musicyt import MusicYT
from yutipy.spotify import Spotify
from yutipy.utils.helpers import is_valid_string


class YutipyMusic:
    """A class that can be used to retrieve music information from all music platforms available in ``yutipy``.

    This is useful when you want to get music information (especially streaming link) from all available platforms.
    Instead of calling each service separately, you can use this class to get the information from all services at once.
    """

    def __init__(
        self,
        custom_kkbox_class=None,
        custom_spotify_class=None,
    ) -> None:
        """
        Parameters
        ----------
        custom_kkbox_class : Optional[type], optional
            A custom class inherited from ``KKBox`` to override the default KKBox implementation.
            This class should implement ``load_access_token()`` and ``save_access_token()`` methods. Default is ``KKBox``.
        custom_spotify_class : Optional[type], optional
            A custom class inherited from ``Spotify`` to override the default Spotify implementation.
            This class should implement ``load_access_token()`` and ``save_access_token()`` methods. Default is ``Spotify``.
        """
        self.music_info = MusicInfos()
        self.normalize_non_english = True
        self.album_art_priority = ["deezer", "ytmusic", "itunes"]
        self.services = {
            "deezer": Deezer(fetch_lyrics=False),
            "itunes": Itunes(fetch_lyrics=False),
            "ytmusic": MusicYT(fetch_lyrics=False),
        }

        try:
            self.services["kkbox"] = (
                custom_kkbox_class(defer_load=True, fetch_lyrics=False)
                if custom_kkbox_class
                else KKBox(fetch_lyrics=False)
            )
        except KKBoxException as e:
            logger.warning(
                f"{self.__class__.__name__}: Skipping KKBox due to KKBoxException: {e}"
            )
        else:
            idx = self.album_art_priority.index("ytmusic")
            self.album_art_priority.insert(idx, "kkbox")

        try:
            self.services["spotify"] = (
                custom_spotify_class(defer_load=True, fetch_lyrics=False)
                if custom_spotify_class
                else Spotify(fetch_lyrics=False)
            )
        except SpotifyException as e:
            logger.warning(
                f"{self.__class__.__name__}: Skipping Spotify due to SpotifyException: {e}"
            )
        else:
            idx = self.album_art_priority.index("ytmusic")
            self.album_art_priority.insert(idx, "spotify")

    def __enter__(self) -> "YutipyMusic":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.close_sessions()

    def search(
        self,
        artist: str,
        song: str,
        limit: int = 5,
        normalize_non_english: bool = True,
    ) -> Optional[MusicInfos]:
        """
        Searches for a song by artist and title.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        limit: int, optional
            The number of items to retrieve from all APIs. ``limit >=1 and <= 50``. Default is ``5``.
        normalize_non_english : bool, optional
            Whether to normalize non-English characters for comparison. Default is ``True``.

        Returns
        -------
        Optional[MusicInfos_]
            The music information if found, otherwise None.
        """
        if not is_valid_string(artist) or not is_valid_string(song):
            raise InvalidValueException(
                "Artist and song names must be valid strings and can't be empty."
            )

        self.normalize_non_english = normalize_non_english

        logger.info(
            f"Searching all platforms for `artist='{artist}'` and `song='{song}'`"
        )

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    service.search,
                    artist=artist,
                    song=song,
                    limit=limit,
                    normalize_non_english=self.normalize_non_english,
                ): name
                for name, service in self.services.items()
            }

            for future in as_completed(futures):
                service_name = futures[future]
                try:
                    result = future.result()
                    self._combine_results(result, service_name)
                except Exception as e:
                    logger.warning(
                        f"Error occurred while searching with {service_name}: {e}"
                    )

        if len(self.music_info.url) == 0:
            logger.info(
                f"No matching results found across all platforms for artist='{artist}' and song='{song}'"
            )
            return None

        # Fetch lyrics only once using LrcLib if not already present
        if not self.music_info.lyrics:
            with LrcLib() as lrc_lib:
                lyrics_result = lrc_lib.get_lyrics(artist, song)
            if lyrics_result:
                self.music_info.lyrics = lyrics_result.get("plainLyrics")

        return self.music_info

    def _combine_results(self, result: Optional[MusicInfo], service_name: str) -> None:
        """
        Combines the results from different services.

        Parameters
        ----------
        result : Optional[MusicInfo]
            The music information from a service.
        service_name : str
            The name of the streaming service.
        """
        if not result:
            return

        attributes = [
            "album_title",
            "album_type",
            "artists",
            "genre",
            "isrc",
            "lyrics",
            "release_date",
            "tempo",
            "title",
            "type",
            "upc",
        ]

        # Always overwrite with Spotify, else Deezer, else KKBox
        highest_priority = None
        for candidate in ["spotify", "deezer", "kkbox"]:
            if candidate in self.services:
                highest_priority = candidate
                break

        if service_name == highest_priority:
            for attr in attributes:
                setattr(self.music_info, attr, getattr(result, attr))
        else:
            for attr in attributes:
                if getattr(result, attr) and (
                    not getattr(self.music_info, attr)
                    or (attr in ["genre", "album_type"] and service_name == "itunes")
                ):
                    setattr(self.music_info, attr, getattr(result, attr))

        if result.album_art:
            current_priority = self.album_art_priority.index(service_name)
            existing_priority = (
                self.album_art_priority.index(self.music_info.album_art_source)
                if self.music_info.album_art_source
                else len(self.album_art_priority)
            )
            if current_priority < existing_priority or service_name == highest_priority:
                self.music_info.album_art = result.album_art
                self.music_info.album_art_source = service_name

        self.music_info.id[service_name] = result.id
        self.music_info.url[service_name] = result.url

    def close_sessions(self) -> None:
        """Closes the sessions for all services."""
        for service in self.services.values():
            if hasattr(service, "close_session"):
                service.close_session()


if __name__ == "__main__":
    import logging
    from dataclasses import asdict

    from yutipy.logger import enable_logging

    enable_logging(level=logging.INFO)
    yutipy_music = YutipyMusic()

    artist_name = input("Artist Name: ")
    song_name = input("Song Name: ")

    pprint(asdict(yutipy_music.search(artist_name, song_name)))
    yutipy_music.close_sessions()
