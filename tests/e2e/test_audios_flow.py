import pytest

from tests.helpers.requests_assertion import assert_ok, assert_bad_request, assert_not_found, assert_resources_count, \
    assert_no_resources, assert_data_matches_resource_ignore_id, assert_data_has_id, assert_data_matches_resource

pytestmark = [pytest.mark.uses_server]



def get_audio(s, session_id):
    return s.get(f"/audios/{session_id}")


def get_audios(s):
    return s.get("/audios")


def post_audio(s, audio):
    return s.post("/audios", json=audio)


def update_audio(s, session_id, audio):
    return s.put(f"/audios/{session_id}", json=audio)


def delete_audio(s, session_id):
    return s.delete(f"/audios/{session_id}")


def test_audios_endpoint(http_session):
    """The test scenario implementation."""

    s = http_session

    # No audios yet

    res = get_audios(s)
    assert_no_resources(assert_ok(res))  # if this fails, you need to delete all resources from server beforehand

    # Fail to create audios with invalid data

    valid_audio = {"ticks": [-96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3448, "step_count": 1}

    too_few_ticks_invalid_audio = dict(valid_audio).update({"ticks": [-96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31]})

    res = post_audio(s, too_few_ticks_invalid_audio)
    assert_bad_request(res)

    step_count_too_large_invalid_audio = dict(valid_audio).update({"step_count": 11})
    res = post_audio(s, step_count_too_large_invalid_audio)
    assert_bad_request(res)

    res = get_audios(s)
    assert_no_resources(assert_ok(res))

    # Succeed to create an audio with valid data

    first_valid_audio = dict(valid_audio)
    first_session_id = first_valid_audio["session_id"]

    res = post_audio(s, first_valid_audio)

    assert_data_matches_resource(assert_ok(res), first_valid_audio)

    # Succeed to get the first audio

    res = get_audio(s, first_session_id)
    assert_data_matches_resource(assert_ok(res), first_valid_audio)

    res = get_audios(s)
    assert_resources_count(assert_ok(res), 1)

    # Fail to get an audio by a session_id that does not exist

    res = get_audio(s, first_session_id + 100)
    assert_not_found(res)

    # Succeed to create a second account with valid user info

    second_valid_audio = {
        "ticks": [-99, -98, -97, -96, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03,
                  -53.6, -49.17, -44.74, -40.31], "selected_tick": 7, "session_id": 1000, "step_count": 7}

    res = post_audio(s, second_valid_audio)
    print(res)
    print(res.text)
    print(res.content)
    second_session_id = second_valid_audio["session_id"]
    assert_data_matches_resource(assert_ok(res), second_valid_audio)

    # Succeed to get the second audio

    res = get_audio(s, second_session_id)
    assert_data_matches_resource(assert_ok(res), second_valid_audio)

    # Succeed to get both audios

    res = get_audios(s)
    assert_resources_count(assert_ok(res), 2)

    # Fail to create an audio with duplicate session

    duplicate_session_id_invalid_audio = dict(first_valid_audio).update({"ticks": [-96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], "step_count": 7})

    res = post_audio(s, duplicate_session_id_invalid_audio)
    assert_bad_request(res)

    # Succeed to get still two audios

    res = get_audios(s)
    assert_resources_count(assert_ok(res), 2)

    # Succeed to get prior audio

    res = get_audio(s, first_session_id)
    assert_data_matches_resource(assert_ok(res), first_valid_audio)

    # Fail to update an audio by session_id that does not match data session_id

    first_valid_audio_with_different_session_id = dict(first_valid_audio).update({"session_id": 1000})

    res = update_audio(s, first_session_id, first_valid_audio_with_different_session_id)
    assert_bad_request(res)

    # Succeed to get the first audio old data

    res = get_audio(s, first_session_id)
    assert_data_matches_resource(assert_ok(res), first_valid_audio)

    # Succeed to get still two audios

    res = get_audios(s)
    assert_resources_count(assert_ok(res), 2)

    # Succeed to delete first audio

    res = delete_audio(s, first_session_id)
    assert_ok(res)

    # Fail to get deleted audio

    res = get_audio(s, first_session_id)
    assert_not_found(res)

    # Succeed to get remaining audio

    res = get_audios(s)
    assert_resources_count(assert_ok(res), 1)

    res = get_audio(s, second_session_id)
    assert_data_matches_resource_ignore_id(assert_ok(res), second_valid_audio)
