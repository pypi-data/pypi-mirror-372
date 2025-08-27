__all__ = [
    "AuthenticationException",
    "InvalidResponseException",
    "InvalidValueException",
    "YutipyException",
]


# Base Exception
class YutipyException(Exception):
    """Base class for exceptions in the Yutipy package."""


# Generic Exceptions
class AuthenticationException(YutipyException):
    """Exception raised for authentication errors."""


class InvalidResponseException(YutipyException):
    """Exception raised for invalid responses from APIs."""


class InvalidValueException(YutipyException):
    """Exception raised for invalid values."""


# Service Exceptions
class DeezerException(YutipyException):
    """Exception raised for errors related to the Deezer API."""


class ItunesException(YutipyException):
    """Exception raised for errors related to the iTunes API."""


class KKBoxException(YutipyException):
    """Exception raised for errors related to the KKBOX Open API."""


class LastFmException(YutipyException):
    """Exception raised for errors related to the LastFm API."""


class MusicYTException(YutipyException):
    """Exception raised for errors related to the YouTube Music API."""


class SpotifyException(YutipyException):
    """Exception raised for errors related to the Spotify API."""


class SpotifyAuthException(AuthenticationException):
    """Exception raised for Spotify authorization code grant type / flow"""
