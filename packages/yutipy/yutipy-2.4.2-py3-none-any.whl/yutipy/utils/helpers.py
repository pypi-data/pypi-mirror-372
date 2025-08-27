import re

import pykakasi
import requests
from rapidfuzz import fuzz
from rapidfuzz.utils import default_process

kakasi = pykakasi.kakasi()

TRANSLATION_CACHE = {}


def similarity(str1: str, str2: str, threshold: int = 100):
    similarity_score = fuzz.WRatio(str1, str2, processor=default_process)
    return similarity_score >= threshold


def translate_text(
    text: str,
    sl: str = None,
    dl: str = "en",
    session: requests.Session = None,
) -> dict:
    """
    Translate text from one language to another.

    Args:
        text (str): The text to be translated.
        sl (str, optional): The source language code (e.g., 'en' for English, 'es' for Spanish). If not provided, the API will attempt to detect the source language.
        dl (str, optional): The destination language code (default is 'en' for English).
        session (requests.Session, optional): A `requests.Session` object to use for making the API request. If not provided, a new session will be created and closed within the function.
            Providing your own session can improve performance by reusing the same session for multiple requests. Don't forget to close the session afterwards.

     Returns:
        dict: A dictionary containing the following keys:
            - 'source-text': The original text.
            - 'source-language': The detected or provided source language code.
            - 'destination-text': The translated text.
            - 'destination-language': The destination language code.
    """
    default_session = False
    if session is None:
        default_session = True
        session = requests.Session()

    if sl:
        url = f"https://ftapi.pythonanywhere.com/translate?sl={sl}&dl={dl}&text={text}"
    else:
        url = f"https://ftapi.pythonanywhere.com/translate?dl={dl}&text={text}"

    response = session.get(url)
    response_json = response.json()
    result = {
        "source-text": response_json["source-text"],
        "source-language": response_json["source-language"],
        "destination-text": response_json["destination-text"],
        "destination-language": response_json["destination-language"],
    }

    if default_session:
        session.close()

    return result


def are_strings_similar(
    str1: str,
    str2: str,
    threshold: int = 95,
    use_translation: bool = True,
    translation_session: requests.Session = None,
) -> bool:
    """
    Determine if two strings are similar based on a given threshold.

    Args:
        str1 (str): First string to compare.
        str2 (str): Second string to compare.
        threshold (int, optional): Similarity threshold. Defaults to 95.
        use_translation (bool, optional): Use translations to compare strings. Defaults to ``True``
        translation_session (requests.Session, optional): A `requests.Session` object to use for making the API request. If not provided, a new session will be created and closed within the function.
            Providing your own session can improve performance by reusing the same session for multiple requests. Don't forget to close the session afterwards.

    Returns:
        bool: True if the strings are similar, otherwise False.
    """

    """
    note for myself so that it make sense later ~ _(:з)∠)_
    0. Check cached strings for comparision
        a. if found and same, return True.
    1. normalize original strings.
        a. if both same, return True.
    2. translate original string.
        a. if both same, return True.
    3. translate normalized string.
        a. if both same, return True.
    4. return False.
    """

    # ### Step 0 ####
    cached_str1 = TRANSLATION_CACHE.get(str1, str1)
    cached_str2 = TRANSLATION_CACHE.get(str2, str2)
    similar = similarity(cached_str1, cached_str2, threshold=threshold)
    if similar:
        return True
    # ###############

    # ### Step 1 ####
    # Transliterate / Normalize Strings
    normalized_str1 = (
        TRANSLATION_CACHE.get(str1)
        or "".join(item["hepburn"] for item in kakasi.convert(str1))
        or str1
    )
    normalized_str2 = (
        TRANSLATION_CACHE.get(str2)
        or "".join(item["hepburn"] for item in kakasi.convert(str2))
        or str2
    )
    similar = similarity(normalized_str1, normalized_str2, threshold=threshold)
    if similar:
        TRANSLATION_CACHE[str1] = normalized_str1
        TRANSLATION_CACHE[str2] = normalized_str2
        return True
    # ###############

    if use_translation:
        # ### Step 2 ####
        original_translated_str1 = (
            TRANSLATION_CACHE.get(str1)
            or translate_text(str1, session=translation_session)["destination-text"]
            if translation_session
            else translate_text(str1)["destination-text"]
        )
        original_translated_str2 = (
            TRANSLATION_CACHE.get(str2)
            or translate_text(str2, session=translation_session)["destination-text"]
            if translation_session
            else translate_text(str2)["destination-text"]
        )
        similar = similarity(
            original_translated_str1, original_translated_str2, threshold=threshold
        )
        if similar:
            TRANSLATION_CACHE[str1] = original_translated_str1
            TRANSLATION_CACHE[str2] = original_translated_str2
            return True
        # ###############

        normalized_translated_str1 = (
            TRANSLATION_CACHE.get(str1)
            or translate_text(str1, session=translation_session)["destination-text"]
            if translation_session
            else translation_session(str1)["destination-text"]
        )
        normalized_translated_str2 = (
            TRANSLATION_CACHE.get(str2)
            or translate_text(str2, session=translation_session)["destination-text"]
            if translation_session
            else translate_text(str2)["destination-text"]
        )
        similar = similarity(
            normalized_translated_str1, normalized_translated_str2, threshold=threshold
        )
        if similar:
            TRANSLATION_CACHE[str1] = normalized_translated_str1
            TRANSLATION_CACHE[str2] = normalized_translated_str2
            return True

    return False


def separate_artists(artists: str, custom_separator: str = None) -> list[str]:
    """
    Separate artist names of a song or album into a list.

    Args:
        artists (str): Artists string (e.g., artistA & artistB, artistA ft. ArtistB).
        custom_separator (str, optional): A specific separator to use. Defaults to None.

    Returns:
        list[str]: List of individual artists.
    """
    if custom_separator:
        pattern = re.escape(custom_separator)
    else:
        pattern = r"\s(?:ft\.?|feat\.?|with|and|[;/&])\s"

    return [
        artist.strip()
        for artist in re.split(pattern, artists, flags=re.IGNORECASE)
        if artist.strip()
    ]


def is_valid_string(string: str) -> bool:
    """Validate if a string is non-empty, alphanumeric, or contains non-whitespace characters."""
    return bool(string and (string.isalnum() or not string.isspace()))


def guess_album_type(total_tracks: int):
    """Just guessing the album type (i.e. single, ep or album) by total track counts."""
    if total_tracks == 1:
        return "single"
    if 3 <= total_tracks <= 5:
        return "ep"
    if total_tracks >= 7:
        return "album"
    return "unknown"
