__all__ = ["Spotify", "SpotifyException", "SpotifyAuthException"]

import os
import webbrowser
from pprint import pprint
from typing import Optional, Union

import requests
from dotenv import load_dotenv

from yutipy.base_clients import BaseAuthClient, BaseClient
from yutipy.exceptions import (
    InvalidValueException,
    SpotifyAuthException,
    SpotifyException,
)
from yutipy.logger import logger
from yutipy.lrclib import LrcLib
from yutipy.models import MusicInfo, UserPlaying
from yutipy.utils.helpers import (
    are_strings_similar,
    guess_album_type,
    is_valid_string,
    separate_artists,
)

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


class Spotify(BaseClient):
    """
    A class to interact with the Spotify API. It uses "Client Credentials" grant type (or flow).

    This class reads the ``SPOTIFY_CLIENT_ID`` and ``SPOTIFY_CLIENT_SECRET`` from environment variables or the ``.env`` file by default.
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
            The Client ID for the Spotify API. Defaults to ``SPOTIFY_CLIENT_ID`` from environment variable or the ``.env`` file.
        client_secret : str, optional
            The Client secret for the Spotify API. Defaults to ``SPOTIFY_CLIENT_SECRET`` from environment variable or the ``.env`` file.
        defer_load : bool, optional
            Whether to defer loading the access token during initialization, by default ``False``
        fetch_lyrics : bool, optional
            Whether to fetch lyrics (using `LRCLIB <https://lrclib.net>`__) if the music platform does not provide lyrics (default is True).
        """
        self.client_id = client_id or SPOTIFY_CLIENT_ID
        self.client_secret = client_secret or SPOTIFY_CLIENT_SECRET
        self.fetch_lyrics = fetch_lyrics

        if not self.client_id:
            raise SpotifyException(
                "Client ID was not found. Set it in environment variable or directly pass it when creating object."
            )

        if not self.client_secret:
            raise SpotifyException(
                "Client Secret was not found. Set it in environment variable or directly pass it when creating object."
            )

        super().__init__(
            service_name="Spotify",
            access_token_url="https://accounts.spotify.com/api/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            defer_load=defer_load,
        )

        self.__api_url = "https://api.spotify.com/v1"

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

        self._normalize_non_english = normalize_non_english

        music_info = None
        artist_ids = None
        queries = [
            f"?q=artist:{artist} track:{song}&type=track&limit={limit}",
            f"?q=artist:{artist} album:{song}&type=album&limit={limit}",
        ]

        for query in queries:
            if music_info:
                return music_info

            self._refresh_access_token()

            query_url = f"{self.__api_url}/search{query}"

            logger.info(
                f"Searching Spotify for `artist='{artist}'` and `song='{song}'`"
            )
            logger.debug(f"Query URL: {query_url}")

            try:
                response = self._session.get(
                    query_url, headers=self._authorization_header(), timeout=30
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"Failed to search for music: {e}")
                return None

            artist_ids = artist_ids if artist_ids else self._get_artists_ids(artist)
            music_info = self._find_music_info(
                artist, song, response.json(), artist_ids
            )

        return music_info

    def search_advanced(
        self,
        artist: str,
        song: str,
        isrc: str = None,
        upc: str = None,
        limit: int = 1,
        normalize_non_english: bool = True,
    ) -> Optional[MusicInfo]:
        """
        Searches for a song by artist, title, ISRC, or UPC.

        Parameters
        ----------
        artist : str
            The name of the artist.
        song : str
            The title of the song.
        isrc : str, optional
            The ISRC of the track.
        upc : str, optional
            The UPC of the album.
        limit: int, optional
            The number of items to retrieve from API. ``limit >=1 and <= 50``. Default is ``1``.
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

        if isrc:
            query = f"?q={artist} {song} isrc:{isrc}&type=track&limit={limit}"
        elif upc:
            query = f"?q={artist} {song} upc:{upc}&type=album&limit={limit}"
        else:
            raise InvalidValueException("ISRC or UPC must be provided.")

        query_url = f"{self.__api_url}/search{query}"
        try:
            response = self._session.get(
                query_url, headers=self._authorization_header(), timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise logger.warning(f"Failed to search music with ISRC/UPC: {e}")
            return None

        artist_ids = self._get_artists_ids(artist)
        return self._find_music_info(artist, song, response.json(), artist_ids)

    def _get_artists_ids(self, artist: str) -> Union[list, None]:
        """
        Retrieves the IDs of the artists.

        Parameters
        ----------
        artist : str
            The name of the artist.

        Returns
        -------
        Union[list, None]
            A list of artist IDs or None if not found.
        """
        artist_ids = []
        for name in separate_artists(artist):
            query_url = f"{self.__api_url}/search?q={name}&type=artist&limit=5"
            try:
                response = self._session.get(
                    query_url, headers=self._authorization_header(), timeout=30
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"Network error during Spotify get artist ids: {e}")
                return None

            if response.status_code != 200:
                return None

            artist_ids.extend(
                artist["id"] for artist in response.json()["artists"]["items"]
            )
        return artist_ids

    def _find_music_info(
        self, artist: str, song: str, response_json: dict, artist_ids: list
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
        artist_ids : list
            A list of artist IDs.

        Returns
        -------
        Optional[MusicInfo]
            The music information if found, otherwise None.
        """
        try:
            for track in response_json["tracks"]["items"]:
                music_info = self._find_track(song, artist, track, artist_ids)
                if music_info:
                    return music_info
        except KeyError:
            pass

        try:
            for album in response_json["albums"]["items"]:
                music_info = self._find_album(song, artist, album, artist_ids)
                if music_info:
                    return music_info
        except KeyError:
            pass

        logger.warning(
            f"No matching results found for artist='{artist}' and song='{song}'"
        )
        return None

    def _find_track(
        self, song: str, artist: str, track: dict, artist_ids: list
    ) -> Optional[MusicInfo]:
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
        artist_ids : list
            A list of artist IDs.

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

        artists_name = [x["name"] for x in track["artists"]]
        matching_artists = [
            x["name"]
            for x in track["artists"]
            if are_strings_similar(
                x["name"],
                artist,
                use_translation=self._normalize_non_english,
                translation_session=self._translation_session,
            )
            or x["id"] in artist_ids
        ]

        if matching_artists:
            music_info = MusicInfo(
                album_art=track["album"]["images"][0]["url"],
                album_title=track["album"]["name"],
                album_type=track["album"]["album_type"],
                artists=", ".join(artists_name),
                genre=None,
                id=track["id"],
                isrc=track.get("external_ids").get("isrc"),
                lyrics=None,
                release_date=track["album"]["release_date"],
                tempo=None,
                title=track["name"],
                type="track",
                upc=None,
                url=track["external_urls"]["spotify"],
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

    def _find_album(
        self, song: str, artist: str, album: dict, artist_ids: list
    ) -> Optional[MusicInfo]:
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
        artist_ids : list
            A list of artist IDs.

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

        artists_name = [x["name"] for x in album["artists"]]
        matching_artists = [
            x["name"]
            for x in album["artists"]
            if are_strings_similar(
                x["name"],
                artist,
                use_translation=self._normalize_non_english,
                translation_session=self._translation_session,
            )
            or x["id"] in artist_ids
        ]

        if matching_artists:
            guess = guess_album_type(album.get("total_tracks", 1))
            guessed_right = are_strings_similar(
                album.get("album_type", "x"), guess, use_translation=False
            )

            return MusicInfo(
                album_art=album["images"][0]["url"],
                album_title=album["name"],
                album_type=album.get("album_type") if guessed_right else guess,
                artists=", ".join(artists_name),
                genre=None,
                id=album["id"],
                isrc=None,
                lyrics=None,
                release_date=album["release_date"],
                tempo=None,
                title=album["name"],
                type=album.get("type"),
                upc=None,
                url=album["external_urls"]["spotify"],
            )

        return None


class SpotifyAuth(BaseAuthClient):
    """
    A class to interact with the Spotify API. It uses "Authorization Code" grant type (or flow).

    This class reads the ``SPOTIFY_CLIENT_ID``, ``SPOTIFY_CLIENT_SECRET`` and ``SPOTIFY_REDIRECT_URI``
    from environment variables or the ``.env`` file by default.
    Alternatively, you can manually provide these values when creating an object.
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: list[str] = None,
        defer_load: bool = False,
        fetch_lyrics: bool = True,
    ):
        """
        Parameters
        ----------
        client_id : str, optional
            The Client ID for the Spotify API. Defaults to ``SPOTIFY_CLIENT_ID`` from environment variable or the ``.env`` file.
        client_secret : str, optional
            The Client secret for the Spotify API. Defaults to ``SPOTIFY_CLIENT_SECRET`` from environment variable or the ``.env`` file.
        redirect_uri : str, optional
            The Redirect URI for the Spotify API. Defaults to ``SPOTIFY_REDIRECT_URI`` from environment variable or the ``.env`` file.
        scopes : list[str], optional
            A list of scopes for the Spotify API. For example: `['user-read-email', 'user-read-private']`.
        defer_load : bool, optional
            Whether to defer loading the access token during initialization. Default is ``False``.
        fetch_lyrics : bool, optional
            Whether to fetch lyrics using `LRCLIB <https://lrclib.net>`__ if the music platform does not provide lyrics (default is True).
        """
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")
        self.scopes = scopes
        self.fetch_lyrics = fetch_lyrics

        if not self.client_id:
            raise SpotifyAuthException(
                "Client ID was not found. Set it in environment variable or directly pass it when creating object."
            )

        if not self.client_secret:
            raise SpotifyAuthException(
                "Client Secret was not found. Set it in environment variable or directly pass it when creating object."
            )

        if not self.redirect_uri:
            raise SpotifyAuthException(
                "No redirect URI was provided! Set it in environment variable or directly pass it when creating object."
            )

        if not scopes:
            logger.warning(
                "No scopes were provided. Authorization will only grant access to publicly available information."
            )
        else:
            self.scopes = " ".join(scopes)

        super().__init__(
            service_name="Spotify",
            access_token_url="https://accounts.spotify.com/api/token",
            user_auth_url="https://accounts.spotify.com/authorize",
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes,
            defer_load=defer_load,
        )

        self.__api_url = "https://api.spotify.com/v1/me"

    def get_user_profile(self) -> Optional[dict]:
        """
        Fetches the user's display name and profile images.

        Notes
        -----
        - ``user-read-email`` and ``user-read-private`` scopes are required to access user profile information.

        Returns
        -------
        dict
            A dictionary containing the user's display name and profile images.
        """
        self._refresh_access_token()
        query_url = self.__api_url
        header = self._authorization_header()

        try:
            response = self._session.get(query_url, headers=header, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch user profile: {e}")
            return None

        if response.status_code != 200:
            logger.warning(f"Unexpected response: {response.json()}")
            return None

        result = response.json()
        return {
            "display_name": result.get("display_name"),
            "images": result.get("images", []),
            "url": result.get("external_urls", {}).get("spotify"),
        }

    def get_currently_playing(self) -> Optional[UserPlaying]:
        """
        Fetches information about the currently playing track for the authenticated user.

        This method interacts with the Spotify API to retrieve details about the track
        the user is currently listening to. It includes information such as the track's
        title, album, artists, release date, and more.

        Returns
        -------
        Optional[UserPlaying_]
            An instance of the ``UserPlaying`` model containing details about the currently
            playing track if available, or ``None`` if no track is currently playing or an
            error occurs.

        Notes
        -----
        - The user must have granted the necessary permissions (e.g., `user-read-currently-playing` scope) for this method to work.
        - If the API response does not contain the expected data, the method will return `None`.

        """
        query_url = f"{self.__api_url}/player/currently-playing"
        self._refresh_access_token()
        header = self._authorization_header()

        try:
            response = self._session.get(query_url, headers=header, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Error while getting Spotify user activity: {e}")
            return None

        if response.status_code == 204:
            logger.info("Requested user is currently not listening to any music.")
            return None

        response_json = response.json()
        result = response_json.get("item")
        if result:
            guess = guess_album_type(result.get("album", {}).get("total_tracks", 1))
            guessed_right = are_strings_similar(
                result.get("album", {}).get("album_type", "x"),
                guess,
                use_translation=False,
            )
            # Spotify returns timestamp in milliseconds, so convert milliseconds to seconds:
            timestamp = response_json.get("timestamp") / 1000.0
            user_playing = UserPlaying(
                album_art=result.get("album", {}).get("images", [])[0].get("url"),
                album_title=result.get("album", {}).get("name"),
                album_type=(
                    result.get("album", {}).get("album_type")
                    if guessed_right
                    else guess
                ),
                artists=", ".join([x["name"] for x in result.get("artists", [])]),
                genre=None,
                id=result.get("id"),
                isrc=result.get("external_ids", {}).get("isrc"),
                is_playing=response_json.get("is_playing"),
                lyrics=None,
                release_date=result.get("album", {}).get("release_date"),
                tempo=None,
                timestamp=timestamp,
                title=result.get("name"),
                type=result.get("type"),
                upc=result.get("external_ids", {}).get("upc"),
                url=result.get("external_urls", {}).get("spotify"),
            )

            if self.fetch_lyrics:
                with LrcLib() as lrc_lib:
                    lyrics = lrc_lib.get_lyrics(
                        artist=user_playing.artists, song=user_playing.title
                    )
                if lyrics:
                    user_playing.lyrics = lyrics.get("plainLyrics")
            return user_playing
        return None


if __name__ == "__main__":
    import logging
    from dataclasses import asdict

    from yutipy.logger import enable_logging

    enable_logging(level=logging.DEBUG)

    print("\nChoose Spotify Grant Type/Flow:")
    print("1. Client Credentials (Spotify)")
    print("2. Authorization Code (SpotifyAuth)")
    choice = input("\nEnter your choice (1 or 2): ")

    if choice == "1":
        spotify = Spotify()

        try:
            artist_name = input("Artist Name: ")
            song_name = input("Song Name: ")
            result = spotify.search(artist_name, song_name)
            pprint(asdict(result))
        finally:
            spotify.close_session()

    elif choice == "2":
        redirect_uri = input("Enter Redirect URI: ")
        scopes = ["user-read-email", "user-read-private"]

        spotify_auth = SpotifyAuth(scopes=scopes)

        try:
            state = spotify_auth.generate_state()
            auth_url = spotify_auth.get_authorization_url(state=state)
            print(f"Opening the following URL in your browser: {auth_url}")
            webbrowser.open(auth_url)

            code = input("Enter the authorization code: ")
            spotify_auth.callback_handler(code, state, state)

            user_profile = spotify_auth.get_user_profile()
            if user_profile:
                print(f"Successfully authenticated \"{user_profile['display_name']}\".")
            else:
                print("Authentication successful, but failed to fetch user profile.")
        finally:
            spotify_auth.close_session()

    else:
        print("Invalid choice. Exiting.")
