"""There is nothing really to test. We would need to completely mock all functionality of the GCP lib
 relied on by this service, and even then we would only really be able to check that methods are indeed called.

 There are very few code paths in the service, and all of them depend on behaviour of the GCP Storage service."""
import pytest as pytest

from src.main.services.audios import build_audio_blob_name, extract_session_id


@pytest.mark.parametrize("test_input,expected", [(3448, "session_3448-audio.json"), (1, "session_1-audio.json")])
def test_build_audio_blob_name(test_input, expected):
    assert build_audio_blob_name(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [("session_3448-audio.json", 3448), ("session_1-audio.json", 1)])
def test_extract_session_id(test_input, expected):
    assert extract_session_id(test_input) == expected


def test_extract_session_id_from_invalid_blob_name():
    with pytest.raises(ValueError):
        print(extract_session_id("not_a_valid_format_123.json"))
