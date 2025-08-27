import argparse
from dataclasses import asdict
from pprint import pprint

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("yutipy")
except PackageNotFoundError:
    __version__ = "unknown"

from yutipy.deezer import Deezer
from yutipy.itunes import Itunes
from yutipy.kkbox import KKBox
from yutipy.musicyt import MusicYT
from yutipy.spotify import Spotify
from yutipy.logger import disable_logging, enable_logging
from yutipy.yutipy_music import YutipyMusic


def main():
    disable_logging()

    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Search for music information across multiple platforms using yutipy."
    )
    parser.add_argument("artist", type=str, help="The name of the artist.")
    parser.add_argument("song", type=str, help="The title of the song.")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="The number of results to retrieve (default: 5).",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize non-English characters.",
        default=False,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable logging in terminal",
        default=False,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"yutipy v{__version__}",
        help="Show the version of the yutipy and exit.",
    )
    parser.add_argument(
        "--service",
        type=str,
        choices=["deezer", "itunes", "kkbox", "spotify", "ytmusic"],
        help="Specify a single service to search (e.g., deezer, itunes, kkbox, spotify, ytmusic).",
    )

    # Parse the arguments
    args = parser.parse_args()

    if args.verbose:
        enable_logging()

    # Use the specified service or default to YutipyMusic
    try:
        if args.service:
            service_map = {
                "deezer": Deezer,
                "itunes": Itunes,
                "kkbox": KKBox,
                "spotify": Spotify,
                "ytmusic": MusicYT,
            }
            service_class = service_map[args.service]
            with service_class() as service:
                result = service.search(
                    artist=args.artist,
                    song=args.song,
                    limit=args.limit,
                    normalize_non_english=args.normalize,
                )
        else:
            with YutipyMusic() as yutipy_music:
                result = yutipy_music.search(
                    artist=args.artist,
                    song=args.song,
                    limit=args.limit,
                    normalize_non_english=args.normalize,
                )

        if result:
            print("\nSEARCH RESULTS:\n")
            pprint(asdict(result))
        else:
            print("No results found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
