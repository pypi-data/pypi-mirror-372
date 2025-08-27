==============
Usage Examples
==============

Here's a quick example of how to use the **yutipy** package to search for a song:

.. important::
    - All examples here use the ``with`` context manager to initialize an instance of the respective class,
      as those classes internally use ``requests.Session()`` for making requests to APIs.
      This approach ensures that the session is automatically closed once you exit the context. Although using ``with`` is not mandatory,
      if you instantiate an object without it, you are responsible for closing the session after use by calling the ``close_session()`` method on that object.

    - Following examples suggest to create ``.env`` file for storing, for example api keys. However, when hosting or deplyoing your application on production,
      it is suggested and you may store them in environment variable(s) provided by your hosting provider.


CLI Tool
--------

You can use the CLI tool to search for music directly from the command line:

.. code-block:: bash

    yutipy-cli "Rick Astley" "Never Gonna Give You Up" --limit 3 --normalize

Deezer
------

.. code-block:: python

    from yutipy.deezer import Deezer

    with Deezer() as deezer:
        result = deezer.search("Artist Name", "Song Title")
        print(result)

iTunes
------

.. code-block:: python

    from yutipy.itunes import Itunes

    with Itunes() as itunes:
        result = itunes.search("Artist Name", "Song Title")
        print(result)

KKBOX
-----

To use the KKBOX Open API, you need to set the ``KKBOX_CLIENT_ID`` and ``KKBOX_CLIENT_SECRET`` for KKBOX.
You can do this by creating a ``.env`` file in the root directory of your project with the following content:

.. admonition:: .env

    .. code-block:: bash

        KKBOX_CLIENT_ID=<your_kkbox_client_id>
        KKBOX_CLIENT_SECRET=<your_kkbox_client_secret>

Alternatively, you can manually provide these values when creating an object of the ``KKBox`` class:

.. code-block:: python

    from yutipy.kkbox import KKBox

    kkbox = KKBox(client_id="your_kkbox_client_id", client_secret="your_kkbox_client_secret")

.. code-block:: python

    from yutipy.kkbox import KKBox

    with KKBox() as kkbox:
        result = kkbox.search("Artist Name", "Song Title")
        print(result)

Lastfm
------

To use and retreive information from Lastfm, you need Lastfm API Key and need to set ``LASTFM_API_KEY``.
You can do this by creating a ``.env`` file int the root directory of your project with the following content:

.. admonition:: .env

    .. code-block:: bash

        LASTFM_API_KEY=<your_lastfm_api_key>

Alternatively, you can manually provide these values when creating an object of the ``LastFm`` class:

.. code-block:: python

    from yutipy.lastfm import LastFm

    lastfm = LastFm(api_key="your_lastfm_api_key")

.. code-block:: python

    from yutipy.lastfm import LastFm

    with LastFm() as lastfm:
        result = lastfm.get_currently_playing(username="username")
        print(result)

ListenBrainz
------------

.. code-block:: python

    from dataclasses import asdict
    from yutipy.listenbrainz import ListenBrainz

    with ListenBrainz() as listenbrainz:
        result = listenbrainz.get_currently_playing(username="username")
        if result:
            print(asdict(result))

Spotify
-------

Client Credentials Grant Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the Spotify API with Client Credentials flow, you need to set the ``SPOTIFY_CLIENT_ID`` and ``SPOTIFY_CLIENT_SECRET`` for Spotify.
You can do this by creating a ``.env`` file in the root directory of your project with the following content:

.. admonition:: .env

    .. code-block:: bash

        SPOTIFY_CLIENT_ID=<your_spotify_client_id>
        SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>

Alternatively, you can manually provide these values when creating an object of the ``Spotify`` class:

.. code-block:: python

    from yutipy.spotify import Spotify

    spotify = Spotify(client_id="your_spotify_client_id", client_secret="your_spotify_client_secret")

.. code-block:: python

    from yutipy.spotify import Spotify

    with Spotify() as spotify:
        result = spotify.search("Artist Name", "Song Title")
        print(result)

OR, if you have the ":abbr:`ISRC (International Standard Recording Code)`" or ":abbr:`UPC (Universal Product Code)`" of the song, you can use the `search_advanced` method:

.. code-block:: python

    from yutipy.spotify import Spotify

    with Spotify() as spotify:
        # ISRC for "single" tracks & UPC for "album" tracks. Only one of them is required.
        result = spotify.search_advanced("Artist Name", "Song Title", isrc="USAT29900609", upc="00602517078194")
        print(result)

Authorization Code Flow
~~~~~~~~~~~~~~~~~~~~~~~

To use the Spotify API with the Authorization Code Flow, you need to set the ``SPOTIFY_CLIENT_ID``, ``SPOTIFY_CLIENT_SECRET``, and ``SPOTIFY_REDIRECT_URI``.
You can do this by creating a ``.env`` file in the root directory of your project with the following content:

.. admonition:: .env

    .. code-block:: bash

        SPOTIFY_CLIENT_ID=<your_spotify_client_id>
        SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>
        SPOTIFY_REDIRECT_URI=<your_redirect_uri>

Alternatively, you can manually provide these values when creating an object of the ``SpotifyAuth`` class.

Here’s an example of how to use the ``SpotifyAuth`` class in a web application:

.. code-block:: python

    from flask import Flask, request, session, redirect, url_for
    from yutipy.spotify import SpotifyAuth, SpotifyAuthException

    app = Flask(__name__)
    app.secret_key = "your_secret_key"  # Replace with a secure secret key

    # Initialize SpotifyAuth with your credentials
    SPOTIFY_CLIENT_ID = "your_spotify_client_id"
    SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
    SPOTIFY_REDIRECT_URI = "http://localhost:5000/callback"

    spotify_auth = SpotifyAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scopes=["user-read-email", "user-read-private"],
    )

    @app.route("/")
    def home():
        """Home route to start the authorization process."""
        state = spotify_auth.generate_state()
        session["state"] = state  # Save the state in the session for validation
        auth_url = spotify_auth.get_authorization_url(state=state)
        return redirect(auth_url)

    @app.route("/callback")
    def callback():
        """Callback route to handle Spotify's response after user authorization."""
        code = request.args.get("code")
        state = request.args.get("state")
        expected_state = session.get("state")

        if not code or not state:
            return "Authorization failed: Missing code or state.", 400

        try:
            spotify_auth.callback_handler(code, state, expected_state)
            user_profile = spotify_auth.get_user_profile()
            if user_profile:
                return f"Successfully authenticated! Welcome, {user_profile['display_name']}."
            else:
                return "Authentication successful, but failed to fetch user profile."
        except SpotifyAuthException as e:
            return f"Authorization failed: {e}", 400

    @app.route("/logout")
    def logout():
        """Logout route to close the session."""
        spotify_auth.close_session()
        session.clear()
        return "Logged out successfully."

    if __name__ == "__main__":
        app.run(debug=True)

.. note::

    - Avoid hard-coding your credentials in the code. Instead, define them in a ``.env`` file, which will be automatically read by the library.
    - Ensure that the redirect URI matches the one configured in your Spotify Developer Dashboard.
    - This example uses Flask, but it can be adapted to other web frameworks as needed.


YouTube Music
-------------

.. code-block:: python

    from yutipy.musicyt import MusicYT

    with MusicYT() as music_yt:
        result = music_yt.search("Artist Name", "Song Title")
        print(result)

Yutipy Music
------------

.. code-block:: python

    from yutipy.yutify_music import YutipyMusic

    with YutipyMusic() as yutipy_music:
        result = yutify_music.search("Artist Name", "Song Title")
        print(result)
