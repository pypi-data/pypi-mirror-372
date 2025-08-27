__all__ = ["BaseClient", "BaseAuthClient"]

import base64
import secrets
from time import time
from urllib.parse import urlencode

import requests

from yutipy.exceptions import AuthenticationException, InvalidValueException
from yutipy.logger import logger


class BaseClient:
    """Base class for Client Credentials grant type/flow."""

    SERVICE_NAME: str
    ACCESS_TOKEN_URL: str

    def __init__(
        self,
        service_name: str,
        access_token_url: str,
        client_id: str = None,
        client_secret: str = None,
        defer_load: bool = False,
    ) -> None:
        """Initializes client (using Client Credentials grant type/flow) and sets up the session.

        Parameters
        ----------
        service_name : str
            The service name class belongs to. For example, "Spotify".
        access_token_url : str
            The url endpoint to request access token.
        """

        self.SERVICE_NAME = service_name
        self.ACCESS_TOKEN_URL = access_token_url

        self._client_id = client_id
        self._client_secret = client_secret

        self._defer_load = defer_load
        self._is_session_closed = False
        self._normalize_non_english = True

        self._access_token = None
        self._token_expires_in = None
        self._token_requested_at = None
        self._session = requests.Session()
        self._translation_session = requests.Session()

        if not defer_load:
            # Attempt to load access token during initialization if not deferred
            self.load_token_after_init()
        else:
            logger.warning(
                "`defer_load` is set to `True`. Make sure to call `load_token_after_init()`."
            )

    def __enter__(self):
        """Enters the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Exits the runtime context related to this object."""
        self.close_session()

    def close_session(self) -> None:
        """Closes the current session(s)."""
        if not self.is_session_closed:
            self._session.close()
            self._translation_session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        """Checks if the session is closed."""
        return self._is_session_closed

    def load_token_after_init(self) -> None:
        """
        Explicitly load the access token after initialization.
        This is useful when ``defer_load`` is set to ``True`` during initialization.
        """
        token_info = None
        try:
            token_info = self.load_access_token()
            if token_info and not isinstance(token_info, dict):
                raise InvalidValueException(
                    "`load_access_token()` should return a dict."
                )
        except NotImplementedError:
            logger.warning(
                "`load_access_token` is not implemented. Falling back to in-memory storage and requesting new access token."
            )
        finally:
            if not token_info or not token_info.get("access_token"):
                token_info = self._get_access_token()
            self._access_token = token_info.get("access_token")
            self._token_expires_in = token_info.get("expires_in")
            self._token_requested_at = token_info.get("requested_at")

            try:
                self.save_access_token(token_info)
            except NotImplementedError:
                logger.warning(
                    "`save_access_token` is not implemented, falling back to in-memory storage. Access token will not be saved."
                )

    def _authorization_header(self) -> dict:
        """
        Generates the authorization header for API requests.

        Returns
        -------
        dict
            A dictionary containing the Bearer token for authentication.
        """
        return {"Authorization": f"Bearer {self._access_token}"}

    def _get_access_token(self) -> dict:
        """
        Gets the API access token information.

        Returns
        -------
        dict
            The API access token, with additional information such as expires in, etc.
        """
        auth_string = f"{self._client_id}:{self._client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        url = self.ACCESS_TOKEN_URL
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        try:
            logger.info(
                f"Authenticating with {self.SERVICE_NAME} API using Client Credentials grant type."
            )
            response = self._session.post(
                url=url, headers=headers, data=data, timeout=30
            )
            logger.debug(f"Authentication response status code: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            raise AuthenticationException(
                f"Something went wrong authenticating with {self.SERVICE_NAME}: {e}"
            )

        response_json = response.json()
        response_json["requested_at"] = time()
        return response_json

    def _refresh_access_token(self) -> None:
        """Refreshes the token if it has expired."""
        try:
            if time() - self._token_requested_at >= self._token_expires_in:
                token_info = self._get_access_token()

                try:
                    self.save_access_token(token_info)
                except NotImplementedError as e:
                    logger.warning(e)

                self._access_token = token_info.get("access_token")
                self._token_expires_in = token_info.get("expires_in")
                self._token_requested_at = token_info.get("requested_at")
            else:
                logger.debug("The access token is still valid, no need to refresh.")
        except TypeError:
            logger.debug(
                f"token requested at: {self._token_requested_at} | token expires in: {self._token_expires_in}"
            )
            logger.info(
                "Something went wrong while trying to refresh the access token. Set logging level to `DEBUG` to see the issue."
            )

    def save_access_token(self, token_info: dict) -> None:
        """
        Saves the access token and related information.

        This method must be overridden in a subclass to persist the access token and other
        related information (e.g., expiration time). If not implemented,
        the access token will not be saved, and it will be requested each time the
        application restarts.

        Parameters
        ----------
        token_info : dict
            A dictionary containing the access token and related information, such as
            refresh token, expiration time, etc.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in a subclass.
        """
        raise NotImplementedError(
            "The `save_access_token` method must be overridden in a subclass to save the access token and related information. "
            "If not implemented, access token information will not be persisted, and users will need to re-authenticate after application restarts."
        )

    def load_access_token(self) -> dict:
        """
        Loads the access token and related information.

        This method must be overridden in a subclass to retrieve the access token and other
        related information (e.g., expiration time) from persistent storage.
        If not implemented, the access token will not be loaded, and it will be requested
        each time the application restarts.

        Returns
        -------
        dict | None
            A dictionary containing the access token and related information, such as
            refresh token, expiration time, etc., or None if no token is found.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in a subclass.
        """
        raise NotImplementedError(
            "The `load_access_token` method must be overridden in a subclass to load access token and related information. "
            "If not implemented, access token information will not be loaded, and users will need to re-authenticate after application restarts."
        )


class BaseAuthClient:
    """Base class for Authorization Code grant type/flow."""

    SERVICE_NAME: str
    ACCESS_TOKEN_URL: str
    USER_AUTH_URL: str

    def __init__(
        self,
        service_name: str,
        access_token_url: str,
        user_auth_url: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: str = None,
        defer_load: bool = False,
    ):
        """
        Initializes client (using Authorization Code grant type/flow) and sets up the session.

        Parameters
        ----------
        service_name : str
            The service name class belongs to. For example, "Spotify".
        access_token_url : str
            The url endpoint to request access token.
        user_auth_url : str
            The url endpoint for user authentication.
        """

        self.SERVICE_NAME = service_name
        self.ACCESS_TOKEN_URL = access_token_url
        self.USER_AUTH_URL = user_auth_url

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._scopes = scopes

        self._defer_load = defer_load
        self._is_session_closed = False

        self._access_token = None
        self._refresh_token = None
        self._token_expires_in = None
        self._token_requested_at = None
        self._session = requests.Session()

        if not defer_load:
            # Attempt to load access token during initialization if not deferred
            self.load_token_after_init()
        else:
            logger.warning(
                "`defer_load` is set to `True`. Make sure to call `load_token_after_init()`."
            )

    def __enter__(self):
        """Enters the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exits the runtime context related to this object."""
        self.close_session()

    def close_session(self) -> None:
        """Closes the current session(s)."""
        if not self.is_session_closed:
            self._session.close()
            self._is_session_closed = True

    @property
    def is_session_closed(self) -> bool:
        """Checks if the session is closed."""
        return self._is_session_closed

    def load_token_after_init(self):
        """
        Explicitly load the access token after initialization.
        This is useful when ``defer_load`` is set to ``True`` during initialization.
        """
        token_info = None
        try:
            token_info = self.load_access_token()
            if token_info and not isinstance(token_info, dict):
                raise InvalidValueException(
                    "`load_access_token()` should return a dict."
                )
        except NotImplementedError:
            logger.warning(
                "`load_access_token` is not implemented. Falling back to in-memory storage."
            )
        finally:
            if token_info and token_info.get("access_token"):
                self._access_token = token_info.get("access_token")
                self._refresh_token = token_info.get("refresh_token")
                self._token_expires_in = token_info.get("expires_in")
                self._token_requested_at = token_info.get("requested_at")
            else:
                logger.warning(
                    "No access token found during initialization. You must authenticate to obtain a new token."
                )

    def _authorization_header(self) -> dict:
        """
        Generates the authorization header for Spotify API requests.

        Returns
        -------
        dict
            A dictionary containing the Bearer token for authentication.
        """
        return {"Authorization": f"Bearer {self._access_token}"}

    def _get_access_token(
        self,
        authorization_code: str = None,
        refresh_token: str = None,
    ) -> dict:
        """
        Gets the API access token information.

        If ``authorization_code`` provided, it will try to get a new access token. Otherwise, if ``refresh_token`` is provided,
        it will refresh the access token using it and return new access token information.

        Returns
        -------
        dict
            The API access token, with additional information such as expires in, refresh token, etc.
        """
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        url = self.ACCESS_TOKEN_URL
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if authorization_code:
            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri,
            }

        if refresh_token:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }

        if not data:
            raise AuthenticationException(
                "Either `authorization_code` or `refresh_token` must be provided to get access token."
            )

        try:
            logger.info(
                f"Authenticating with {self.SERVICE_NAME} API using Authorization Code grant type."
            )
            response = self._session.post(
                url=url, headers=headers, data=data, timeout=30
            )
            logger.debug(f"Authentication response status code: {response.status_code}")
            response.raise_for_status()
        except requests.RequestException as e:
            raise AuthenticationException(
                f"Something went wrong authenticating with {self.SERVICE_NAME}: {e}"
            )

        response_json = response.json()
        if "refresh_token" not in response_json:
            response_json["refresh_token"] = refresh_token
        response_json["requested_at"] = time()
        return response_json

    def _refresh_access_token(self):
        """Refreshes the token if it has expired."""
        if not self._access_token or not self._refresh_token:
            logger.warning(
                "No access token or refresh token found. You must authenticate to obtain a new token."
            )
            return

        try:
            if time() - self._token_requested_at >= self._token_expires_in:
                token_info = self._get_access_token(refresh_token=self._refresh_token)

                try:
                    self.save_access_token(token_info)
                except NotImplementedError as e:
                    logger.warning(e)

                self._access_token = token_info.get("access_token")
                self._refresh_token = token_info.get("refresh_token")
                self._token_expires_in = token_info.get("expires_in")
                self._token_requested_at = token_info.get("requested_at")

            else:
                logger.debug("The access token is still valid, no need to refresh.")
        except TypeError:
            logger.debug(
                f"token requested at: {self._token_requested_at} | token expires in: {self._token_expires_in}"
            )
            logger.warning(
                "Something went wrong while trying to refresh the access token. Set logging level to `DEBUG` to see the issue."
            )

    @staticmethod
    def generate_state() -> str:
        """
        Generates a random state string for use in OAuth 2.0 authorization.

        This method creates a cryptographically secure, URL-safe string that can be used
        to prevent cross-site request forgery (CSRF) attacks during the authorization process.

        Returns
        -------
        str
            A random URL-safe string to be used as the state parameter in OAuth 2.0.
        """
        return secrets.token_urlsafe()

    def get_authorization_url(
        self, state: str = None, show_dialog: bool = False
    ) -> str:
        """
        Constructs the Spotify authorization URL for user authentication.

        This method generates a URL that can be used to redirect users to Spotify's
        authorization page for user authentication.

        Parameters
        ----------
        state : str, optional
            A random string to maintain state between the request and callback.
            If not provided, no state parameter is included.

            You may use :meth:`SpotifyAuth.generate_state` method to generate one.
        show_dialog : bool, optional
            Whether or not to force the user to approve the app again if they’ve already done so.
            If ``False`` (default), a user who has already approved the application may be automatically
            redirected to the URI specified by redirect_uri. If ``True``, the user will not be automatically
            redirected and will have to approve the app again.

        Returns
        -------
        str
            The full authorization URL to redirect users for Spotify authentication.
        """
        payload = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }

        if self._scopes:
            payload["scope"] = self._scopes

        if show_dialog:
            payload["show_dialog"] = show_dialog

        if state:
            payload["state"] = state

        return f"{self.USER_AUTH_URL}?{urlencode(payload)}"

    def save_access_token(self, token_info: dict) -> None:
        """
        Saves the access token and related information.

        This method must be overridden in a subclass to persist the access token and other
        related information (e.g., refresh token, expiration time). If not implemented,
        the access token will not be saved, and users will need to re-authenticate after
        application restarts.

        Parameters
        ----------
        token_info : dict
            A dictionary containing the access token and related information, such as
            refresh token, expiration time, etc.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in a subclass.
        """
        raise NotImplementedError(
            "The `save_access_token` method must be overridden in a subclass to save the access token and related information. "
            "If not implemented, access token information will not be persisted, and users will need to re-authenticate after application restarts."
        )

    def load_access_token(self) -> dict:
        """
        Loads the access token and related information.

        This method must be overridden in a subclass to retrieve the access token and other
        related information (e.g., refresh token, expiration time) from persistent storage.
        If not implemented, the access token will not be loaded, and users will need to
        re-authenticate after application restarts.

        Returns
        -------
        dict | None
            A dictionary containing the access token and related information, such as
            refresh token, expiration time, etc., or None if no token is found.

        Raises
        ------
        NotImplementedError
            If the method is not overridden in a subclass.
        """
        raise NotImplementedError(
            "The `load_access_token` method must be overridden in a subclass to load access token and related information. "
            "If not implemented, access token information will not be loaded, and users will need to re-authenticate after application restarts."
        )

    def callback_handler(self, code, state, expected_state):
        """
        Handles the callback phase of the OAuth 2.0 authorization process.

        This method processes the authorization code and state returned by Spotify after the user
        has granted permission. It validates the state to prevent CSRF attacks, exchanges the
        authorization code for an access token, and saves the token for future use.

        Parameters
        ----------
        code : str
            The authorization code returned by Spotify after user authorization.
        state : str
            The state parameter returned by Spotify to ensure the request's integrity.
        expected_state : str
            The original state parameter sent during the authorization request, used to validate the response.

        Raises
        ------
        SpotifyAuthException
            If the returned state does not match the expected state.

        Notes
        -----
        - This method can be used in a web application (e.g., Flask) in the `/callback` route to handle
          successful authorization.
        - Ensure that the ``save_access_token`` and ``load_access_token`` methods are implemented in a subclass
          if token persistence is required.
        """
        if state != expected_state:
            raise AuthenticationException("state does not match!")

        token_info = self._get_access_token(authorization_code=code)

        self._access_token = token_info.get("access_token")
        self._refresh_token = token_info.get("refresh_token")
        self._token_expires_in = token_info.get("expires_in")
        self._token_requested_at = token_info.get("requested_at")

        try:
            self.save_access_token(token_info)
        except NotImplementedError as e:
            logger.warning(e)
