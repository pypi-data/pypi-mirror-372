===
FAQ
===

Why use ``yutipy`` when there are better libraries for individual music platforms?
----------------------------------------------------------------------------------

You are correct that there are other libraries with more features tailored to specific music platforms. However,
these libraries often come with complexities and additional steps that may not be necessary for all users.
In contrast, **yutipy** is designed to be simple and focuses primarily on search functionality [#]_.

While there are several music platforms available for searching music, and potentially more in the future,
**yutipy** aims to provide a straightforward experience. The key difference is that other libraries return
results from music platforms' APIs as-is, whereas **yutipy** utilizes the ``RapidFuzz`` [#]_ library to compare each
result returned by the APIs with your search query. This ensures that you receive the best match for your search
without having to perform the comparison manually.

Why is it necessary to use the ``close_session()`` method? What happens if we don't call it?
--------------------------------------------------------------------------------------------

Internally, **yutipy** uses ``requests.Session()`` [#]_ to make requests to the respective music platforms' APIs for performance improvements.
Using ``requests.get()`` [#]_ for each request can be relatively slow, as it opens a new connection each time. In contrast, ``requests.Session()``
allows for reusing the same session, which is beneficial when making multiple requests to the same API.

If you initiate an object using the ``with`` keyword, calling ``close_session()`` is not required. While inside the ``with`` block,
the same session is used for making requests, and ``close_session()`` is automatically called when you exit the block.

If you forget to call ``close_session()`` after you no longer need to make requests, the session will remain open,
potentially consuming resources. However, the session will eventually close when your application ends.

Why doesn't the ``MusicYT`` class support initialization with the ``with`` keyword?
-----------------------------------------------------------------------------------

**yutipy** does not make direct requests to the "YouTube Music" APIs; instead, it relies on the ``ytmusicapi`` [#]_ library for searching and
retrieving music information. Additionally, **yutipy** does not inherit from any classes in the ``ytmusicapi`` library,
so you should not expect to have access to all functionalities available in that library.

Why am I receiving a ``SpotifyException`` when trying to use the ``Spotify`` class?
-----------------------------------------------------------------------------------

Unfortunately, the Spotify API endpoints require authentication. You will need a ``Client ID`` and ``Client Secret``
obtained from the Spotify for Developers website. To do this, follow these steps:

1. Go to your dashboard at https://developer.spotify.com/dashboard.
2. Create a new app and fill in the "Redirect URIs" field with:
    - .. code-block:: text

        localhost/callback
3. Select "Web API" for "Which API/SDKs are you planning to use?", check the "I understand..." box, and click "Save".
4. Click on "Settings" (located in the top right corner).
5. Copy the ``Client ID`` and save it somewhere secure.
    .. _step_5:
6. Click on "View client secret" to obtain your ``Client Secret`` and save it somewhere secure as well.
    .. _step_6:
7. Create a ``.env`` file in the root directory of your project.
8. Paste the following into the ``.env`` file:
    - .. admonition:: .env

        .. code-block:: bash

            SPOTIFY_CLIENT_ID=<spotify_client_id>
            SPOTIFY_CLIENT_SECRET=<spotify_client_secret>
    - Ensure you replace ``<spotify_client_id>`` and ``<spotify_client_secret>`` with the values you copied in steps :ref:`5 <step_5>` and :ref:`6 <step_6>` respectively.

After completing these steps, you should be able to use the ``Spotify`` class and its methods as expected.

Why am I receiving a ``KKBoxException`` when trying to use the ``KKBox`` class?
-------------------------------------------------------------------------------

Unfortunately, it's the same case as with Spotify. You will need a ``Client ID`` and ``Client Secret``
obtained from the KKBOX for Developers website. Please visit https://developer.kkbox.com/ for more information.

How do I use the CLI tool to search for music?
----------------------------------------------

You can use the CLI tool to search for music directly from the command line. For example:

.. code-block:: bash

    yutipy-cli "Rick Astley" "Never Gonna Give You Up" --limit 3 --normalize

For more details, see the :doc:`usage_examples`.

How do I set up API keys for the library?
-----------------------------------------

You can use the configuration wizard to set up API keys interactively:

.. code-block:: bash

    yutipy-config

The wizard will guide you through obtaining and setting up API keys for supported services like Spotify and KKBOX.

----

.. [#] There may be additional features in the future.
.. [#] https://pypi.org/project/RapidFuzz/
.. [#] https://requests.readthedocs.io/en/latest/api/#request-sessions
.. [#] https://requests.readthedocs.io/en/latest/api/#requests.get
.. [#] https://pypi.org/project/ytmusicapi/
