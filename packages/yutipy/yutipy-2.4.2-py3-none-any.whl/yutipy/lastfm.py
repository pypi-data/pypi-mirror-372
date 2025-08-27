__all__ = ["LastFm", "LastFmException"]

import os
from pprint import pprint
from time import time
from typing import Optional

import requests
from dotenv import load_dotenv

from yutipy.exceptions import LastFmException
from yutipy.logger import logger
from yutipy.models import UserPlaying
from yutipy.utils.helpers import separate_artists

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")


class LastFm:
    """
    A class to interact with the Last.fm API for fetching user music data.

    This class reads the ``LASTFM_API_KEY`` from environment variables or the ``.env`` file by default.
    Alternatively, you can manually provide this values when creating an object.
    """

    def __init__(self, api_key: str = None):
        """
        Parameters
        ----------
        lastfm_api_key : str, optional
            The Lastfm API Key (<https://www.last.fm/api>). Defaults to ``LASTFM_API_KEY`` from environment variable or the ``.env`` file.

        Raises:
            LastFmException: If the API key is not provided or found in the environment.
        """
        self.api_key = api_key or LASTFM_API_KEY

        if not self.api_key:
            raise LastFmException(
                "Lastfm API key was not found. Set it in environment variable or directly pass it when creating object."
            )

        self._is_session_closed = False

        self.__api_url = "https://ws.audioscrobbler.com/2.0"
        self.__session = requests.Session()

    def __enter__(self):
        """Enters the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exits the runtime context related to this object."""
        self.close_session()

    def close_session(self) -> None:
        """Closes the current session(s)."""
        if not self._is_session_closed:
            self.__session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        """Checks if the session is closed."""
        return self._is_session_closed

    def get_user_profile(self, username: str):
        """
        Fetches the user profile information for the provided username.

        Parameters
        ----------
        username : str
            The Last.fm username to fetch profile information for.

        Returns
        -------
        dict
            A dictionary containing the user's profile information or error is username does not exist.
        """
        query = (
            f"?method=user.getinfo&user={username}&api_key={self.api_key}&format=json"
        )
        query_url = self.__api_url + query

        try:
            response = self.__session.get(query_url, timeout=30)
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch user profile: {e}")
            return None

        response_json = response.json()
        result = response_json.get("user")
        error = response_json.get("message")
        if result:
            images = [
                {"size": image.get("size"), "url": image.get("#text")}
                for image in result.get("image", [])
            ]
            return {
                "name": result.get("realname"),
                "username": result.get("name"),
                "type": result.get("type"),
                "url": result.get("url"),
                "images": images,
            }
        elif error:
            return {"error": error}
        else:
            return None

    def get_currently_playing(self, username: str) -> Optional[UserPlaying]:
        """
        Fetches information about the currently playing track for a user.

        Parameters
        ----------
        username : str
            The Last.fm username to fetch data for.

        Returns
        -------
        Optional[UserPlaying_]
            An instance of the ``UserPlaying`` model containing details about the currently
            playing track if available, or ``None`` if the request fails or no data is available.
        """
        query = f"?method=user.getrecenttracks&user={username}&limit=1&api_key={self.api_key}&format=json"
        query_url = self.__api_url + query

        try:
            response = self.__session.get(query_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch user profile: {e}")
            return None

        response_json = response.json()
        result = response_json.get("recenttracks", {}).get("track", [])[0]
        is_playing = result.get("@attr", {}).get("nowplaying", False)
        is_playing = (
            True if isinstance(is_playing, str) and is_playing == "true" else False
        )
        if result and is_playing:
            album_art = [
                img.get("#text")
                for img in result.get("image", [])
                if img.get("size") == "extralarge"
            ]
            return UserPlaying(
                album_art="".join(album_art),
                album_title=result.get("album", {}).get("#text"),
                artists=", ".join(
                    separate_artists(result.get("artist", {}).get("#text"))
                ),
                id=result.get("mbid") if result.get("mbid") else None,
                timestamp=result.get("date", {}).get("uts") or time(),
                title=result.get("name"),
                url=result.get("url"),
                is_playing=is_playing,
            )
        return None


if __name__ == "__main__":
    with LastFm() as lastfm:
        username = input("Enter Lasfm Username: ").strip()
        result = lastfm.get_user_profile(username=username)

        if result:
            pprint(result)
        else:
            print("No result was found. Make sure the username is correct!")
