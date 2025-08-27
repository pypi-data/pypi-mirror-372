<p align="center">
<img src="https://raw.githubusercontent.com/CheapNightbot/yutipy/main/docs/_static/yutipy_header.png" alt="yutipy" />
</p>

<p align="center">
<a href="https://github.com/CheapNightbot/yutipy/actions/workflows/tests.yml">
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/cheapnightbot/yutipy/pytest-unit-testing.yml?style=for-the-badge&label=Pytest">
</a>
<a href="https://yutipy.readthedocs.io/en/latest/">
<img src="https://img.shields.io/readthedocs/yutipy?style=for-the-badge" alt="Documentation Status" />
</a>
<a href="https://pypi.org/project/yutipy/">
<img src="https://img.shields.io/pypi/v/yutipy?style=for-the-badge" alt="PyPI" />
</a>
<a href="https://github.com/CheapNightbot/yutipy/blob/master/LICENSE">
<img src="https://img.shields.io/github/license/CheapNightbot/yutipy?style=for-the-badge" alt="License" />
</a>
<a href="https://github.com/CheapNightbot/yutipy/stargazers">
<img src="https://img.shields.io/github/stars/CheapNightbot/yutipy?style=for-the-badge" alt="Stars" />
</a>
<a href="https://github.com/CheapNightbot/yutipy/issues">
<img src="https://img.shields.io/github/issues/CheapNightbot/yutipy?style=for-the-badge" alt="Issues" />
</a>
</p>

> **Looking for an easy-to-use API or GUI to search for music, instead of using the CLI or building your own integration?**
> Check out [yutify](https://yutify.cheapnightbot.me) — it’s powered by yutipy!

A _**simple**_ Python package to interact with various music platforms APIs.

## Table of Contents

- [Features](#features)
    - [Available Music Platforms](#available-music-platforms)
- [Installation](#installation)
- [Usage Example](#usage-example)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
    - [Search for Music](#search-for-music)
        - [Options](#options)
    - [Configuration Wizard](#configuration-wizard)
- [Contributing](#contributing)
- [License](#license)

## Features

- Simple & Easy integration with popular music APIs.
- Search for music by artist and song title across multiple platforms.
- It uses `RapidFuzz` to compare & return the best match so that you can be sure you got what you asked for without having to worry and doing all that work by yourself.
- Retrieve detailed music information, including album art, release dates, lyrics, ISRC, and UPC codes.
- Authorize and access user resources easily.

### Available Music Platforms

Right now, the following music platforms are available in yutipy for searching music. New platforms will be added in the future.
Feel free to request any music platform you would like me to add by opening an issue on [GitHub](https://github.com/CheapNightbot/yutipy/issues) or by emailing me.

- `Deezer`: https://www.deezer.com
- `iTunes`: https://music.apple.com
- `KKBOX`: https://www.kkbox.com
- `Lastfm`: https://last.fm
- `ListenBrainz`: https://listenbrainz.org
- `Spotify`: https://spotify.com
- `YouTube Music`: https://music.youtube.com

## Installation

You can install the package using pip. Make sure you have Python 3.9 or higher installed.

```bash
pip install -U yutipy
```

## Usage Example

Here's a quick example of how to use the `yutipy` package to search for a song on **Deezer**:

```python
from yutipy.deezer import Deezer

with Deezer() as deezer:
    result = deezer.search("Artist Name", "Song Title")
    print(result)
```

For more usage examples, see the [Usage Examples](https://yutipy.readthedocs.io/en/latest/usage_examples.html) page in docs.

## Command-Line Interface (CLI)

The `yutipy` package includes a CLI tool that allows you to search for music directly from the command line and configure API keys interactively.

### Search for Music

You can use the CLI tool to search for music across multiple platforms:

```bash
yutipy-cli "Rick Astley" "Never Gonna Give You Up" --limit 3 --normalize
```

#### Options:
- `artist` (required): The name of the artist.
- `song` (required): The title of the song.
- `--limit`: The number of results to retrieve (default: 5).
- `--normalize`: Normalize non-English characters for comparison.
- `--verbose`: Enable logging in the terminal.
- `--service`: Specify a single service to search (e.g., `deezer`, `spotify`, `itunes`).

### Configuration Wizard

To set up your API keys interactively, use the configuration wizard:

```bash
yutipy-config
```

The wizard will guide you through obtaining and setting up API keys for supported services like Spotify and KKBOX. If the required environment variables are already set, the wizard will skip those steps.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Optionally, create an issue to discuss the changes you plan to make.
3. Create a new branch linked to that issue.
4. Make your changes in the new branch.
5. Write tests if you add new functionality.
6. Ensure all tests pass before opening a pull request.
7. Open a pull request for review.

Thank you for your contributions!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
