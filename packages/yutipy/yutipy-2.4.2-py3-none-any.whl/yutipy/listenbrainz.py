__all__ = ["ListenBrainz"]

from typing import Optional
from time import time

import requests

from yutipy.logger import logger
from yutipy.models import UserPlaying
from yutipy.utils.helpers import are_strings_similar


class ListenBrainz:
    """A class to interact with the ListenBrainz API for fetching user music data."""

    def __init__(self):
        self._is_session_closed = False
        self.__api_url = "https://api.listenbrainz.org"
        self.__session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close_session()

    def close_session(self):
        """Closes the current session(s)."""
        if not self._is_session_closed:
            self.__session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        """Checks if the session is closed."""
        return self._is_session_closed

    def find_user(self, username: str) -> Optional[str]:
        """
        Whether profile with the provided username exists on the ListenBrainz.

        It searches ListenBrainz for the provided username and fuzzy matches
        the provided username with the username(s) returned from ListenBrainz API.

        Parameters
        ----------
        username : str
            The username to search.

        Returns
        -------
        Optional[str]
            The username returned by ListenBrainz API if user found,
            or ``None`` if the user with provided username does not exist.
        """
        endpoint = "/1/search/users/"
        url = self.__api_url + endpoint

        try:
            response = self.__session.get(
                url=url, params={"search_term": username}, timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to search for the user: {e}")
            return

        response_json = response.json()
        users = response_json.get("users")

        if not users:
            return

        for user in users:
            user_name = user.get("user_name")
            if are_strings_similar(
                username, user_name, threshold=100, use_translation=False
            ):
                return user_name

    def get_currently_playing(self, username: str) -> Optional[UserPlaying]:
        """
        Fetches information about the currently playing track for a user.

        Parameters
        ----------
        username : str
            The ListenBrainz username to fetch data for.

        Returns
        -------
        Optional[UserPlaying_]
            An instance of the ``UserPlaying`` model containing details about the currently
            playing track if available, or ``None`` if the request fails or no data is available.
        """
        endpoint = f"/1/user/{username}/playing-now"
        url = self.__api_url + endpoint

        try:
            response = self.__session.get(url=url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to retrieve listening activity: {e}")
            return

        response_json = response.json()
        if not response_json:
            logger.info(
                f"It seems no activity found for `{username}`. Might be user does not exist or not no data available."
            )
            return

        result = response_json.get("payload", {})
        is_playing = result.get("playing_now", False)
        user_id = result.get("user_id", "")

        if username.lower() != user_id.lower():
            return

        if result and is_playing:
            track_metadata = result.get("listens", [{}])[0].get("track_metadata", {})
            return UserPlaying(
                artists=track_metadata.get("artist_name"),
                id=None,
                timestamp=time(),
                title=track_metadata.get("track_name"),
                url=track_metadata.get("additional_info", {}).get("origin_url"),
                is_playing=is_playing,
            )
        return None


if __name__ == "__main__":
    with ListenBrainz() as listenbrainz:
        username = input("Enter ListenBrainz Username: ").strip()
        result = listenbrainz.find_user(username)

        if result:
            print(f"User found with username: {result}")
        else:
            print(f"No user with username '{username}' found!")
