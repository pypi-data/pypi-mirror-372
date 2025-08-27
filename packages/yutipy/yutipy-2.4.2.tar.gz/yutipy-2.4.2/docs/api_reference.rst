=============
API Reference
=============

Main Classes
=============

Deezer
------

.. autoclass:: yutipy.deezer.Deezer
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed

iTunes
------

.. autoclass:: yutipy.itunes.Itunes
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed

KKBox
-----

.. autoclass:: yutipy.kkbox.KKBox
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed, SERVICE_NAME, ACCESS_TOKEN_URL

Lastfm
------

.. autoclass:: yutipy.lastfm.LastFm
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed

ListenBrainz
------------

.. autoclass:: yutipy.listenbrainz.ListenBrainz
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed

LRCLIB
------

.. autoclass:: yutipy.lrclib.LrcLib
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed

Spotify
-------

.. autoclass:: yutipy.spotify.Spotify
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed, SERVICE_NAME, ACCESS_TOKEN_URL

.. autoclass:: yutipy.spotify.SpotifyAuth
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: is_session_closed, SERVICE_NAME, ACCESS_TOKEN_URL, USER_AUTH_URL

YouTube Music
-------------

.. autoclass:: yutipy.musicyt.MusicYT
    :members:
    :inherited-members:
    :noindex:

Yutipy Music
------------

.. autoclass:: yutipy.yutipy_music.YutipyMusic
    :members:
    :inherited-members:
    :noindex:

Data Classes
=============

MusicInfo
---------

.. autoclass:: yutipy.models.MusicInfo
    :members:
    :noindex:
    :exclude-members: album_art, album_title, album_type, artists, genre, id, isrc, lyrics, release_date, tempo, title, type, upc, url

MusicInfos
----------

.. autoclass:: yutipy.models.MusicInfos
    :members:
    :noindex:
    :exclude-members: album_art, album_art_source, album_title, album_type, artists, genre, id, isrc, lyrics, release_date, tempo, title, type, upc, url

UserPlaying
-----------

.. autoclass:: yutipy.models.UserPlaying
    :members:
    :noindex:
    :exclude-members: album_art, album_art_source, album_title, album_type, artists, genre, id, isrc, lyrics, release_date, tempo, title, type, upc, url, timestamp, is_playing

Exceptions
=============

Base Exception
--------------

.. autoclass:: yutipy.exceptions.YutipyException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

Generic Exceptions
------------------

.. autoclass:: yutipy.exceptions.AuthenticationException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.InvalidResponseException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.InvalidValueException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

Service Exceptions
------------------

.. autoclass:: yutipy.exceptions.DeezerException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.ItunesException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.KKBoxException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.LastFmException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.MusicYTException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.SpotifyException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback

.. autoclass:: yutipy.exceptions.SpotifyAuthException
    :members:
    :inherited-members:
    :noindex:
    :exclude-members: add_note, args, with_traceback
