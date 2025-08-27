import pytest
from yutipy.utils import are_strings_similar, separate_artists


def test_are_strings_similar():
    assert are_strings_similar("Hello World", "Hello World", use_translation=False) is True
    assert are_strings_similar("Hello W", "Hello", use_translation=False) is True


def test_are_strings_similar_translation(monkeypatch):
    # Mock responses for translate_text
    mock_responses = {
        "ポーター": {
            "source-text": "ポーター",
            "source-language": "ja",
            "destination-text": "Porter",
            "destination-language": "en",
        },
        "Porter": {
            "source-text": "Porter",
            "source-language": "en",
            "destination-text": "Porter",
            "destination-language": "en",
        },
    }

    def mock_translate_text(text, *args, **kwargs):
        return mock_responses[text]

    # Use monkeypatch to replace translate_text with the mock function
    monkeypatch.setattr("yutipy.utils.helpers.translate_text", mock_translate_text)

    # Run the test with the mocked translate_text
    assert are_strings_similar("ポーター", "Porter") is True


def test_separate_artists():
    assert separate_artists("Artist A & Artist B") == ["Artist A", "Artist B"]
    assert separate_artists("Artist A ft. Artist B") == ["Artist A", "Artist B"]
    assert separate_artists("Artist A") == ["Artist A"]
    assert separate_artists("Artist A and Artist B") == ["Artist A", "Artist B"]
    assert separate_artists("Artist A / Artist B") == ["Artist A", "Artist B"]
    assert separate_artists("Artist A, Artist B", custom_separator=",") == [
        "Artist A",
        "Artist B",
    ]
