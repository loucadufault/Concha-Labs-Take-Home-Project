import pytest as pytest

from src.main.exceptions import ValidationError
from src.main.helpers.email_utils import normalize_email
from src.main.models import UserInfo, Audio
from src.main.parse_request import validate_and_get_user_info_model, validate_and_get_audio_model
from tests.helpers.list_utils import is_lists_equal


def test_valid_user_info():
    test_data = {
        "name": "Foo bar",
        "email": "foo.bar@gmail.com",
        "address": "1234 Main Road"
    }
    user_model = validate_and_get_user_info_model(test_data)

    assert isinstance(user_model, UserInfo)
    assert user_model.name == test_data["name"]
    assert user_model.email == test_data["email"]
    assert user_model.address == test_data["address"]


def test_normalizes_user_info_email():
    test_data = {
        "name": "Foo bar",
        "email": "foo.bar@GMAIL.cOm",
        "address": "1234 Main Road"
    }
    user_model = validate_and_get_user_info_model(test_data)
    print(user_model)
    assert user_model.email == normalize_email(test_data["email"])


def test_invalid_user_info_email():
    test_data = {
        "name": "Foo bar",
        "email": "no.domain",
        "address": "1234 Main Road"
    }

    with pytest.raises(ValidationError):
        validate_and_get_user_info_model(test_data)


def test_user_info_missing_field():
    test_data = {
        "email": "foo.bar@gmail.com",
        "address": "1234 Main Road"
    }

    with pytest.raises(ValidationError):
        validate_and_get_user_info_model(test_data)


def test_user_info_wrong_field_type():
    test_data = {
        "email": "foo.bar@gmail.com",
        "address": "1234 Main Road"
    }

    with pytest.raises(ValidationError):
        validate_and_get_user_info_model(test_data)



def test_valid_audio():
    test_data = {"ticks": [-96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}
    audio_model = validate_and_get_audio_model(test_data)

    assert isinstance(audio_model, Audio)
    assert is_lists_equal(audio_model.ticks, test_data["ticks"])
    assert audio_model.selected_tick == test_data["selected_tick"]
    assert audio_model.session_id == test_data["session_id"]
    assert audio_model.step_count == test_data["step_count"]


def test_invalid_audio_ticks_count_too_few():
    test_data = {
        "ticks": [-96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)


def test_invalid_audio_ticks_count_too_many():
    test_data = {
        "ticks": [-50, -96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)


def test_invalid_audio_ticks_value_too_small():
    test_data = {
        "ticks": [-200, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)


def test_invalid_audio_ticks_value_too_large():
    test_data = {
        "ticks": [-9, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)


def test_invalid_audio_step_count_too_small():
    test_data = {
        "ticks": [-96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": -10}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)


def test_invalid_audio_selected_tick_too_large():
    test_data = {
        "ticks": [-96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 16, "session_id": 3448, "step_count": 1}

    with pytest.raises(ValidationError):
        validate_and_get_audio_model(test_data)
