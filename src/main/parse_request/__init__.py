import warnings

from src.main.exceptions import ValidationError
from dataclasses import fields as get_fields

from src.main.helpers.email_utils import is_valid_email, normalize_email
from src.main.models import UserInfo, Audio
from marshmallow import EXCLUDE
from typing import List


def request_body_is_json(request):
    if request.is_json is None:
        raise ValidationError("The request mimetype did not indicate JSON (application/json).")


def validate_request_data_against_model(request_data, model_cls, exclude=[]):
    fields = {field.name: field.type for field in get_fields(model_cls)}

    errors = []

    def missing_field(pfield_name):
        errors.append({"detail": "Request is missing field '{}'".format(pfield_name), "pointer": pfield_name})

    def wrong_field_type(pfield_name, expected_field_type, actual_field_value):
        errors.append({
            "detail": "'{}' is not a valid value for request field '{}', expected a {}.".format(
                actual_field_value, pfield_name, expected_field_type.__name__),
            "pointer": pfield_name})

    for field_name, field_type in fields.items():
        if field_name in exclude:
            continue

        if field_name not in request_data:
            missing_field(field_name)
            continue
        if isinstance(field_type, type(List)):
            if type(request_data[field_name]) != list:
                wrong_field_type(field_name, field_type, request_data[field_name])
            continue

        try:
            field_type(request_data[field_name])
        except ValueError:
            wrong_field_type(field_name, field_type, request_data[field_name])

    if len(errors) > 0:
        raise ValidationError(detailed_validation_errors=errors)


def validate_and_get_user_info_model(data):
    validate_request_data_against_model(data, UserInfo, exclude=["id"])
    if not is_valid_email(data["email"]):
        raise ValidationError(detailed_validation_errors=[{
            "detail": f"'{data['email']}' is not a valid email.",
            "pointer": "email"}])
    data["email"] = normalize_email(data["email"])
    return UserInfo.schema(unknown=EXCLUDE).load(data)


def validate_and_get_audio_model(data):
    validate_request_data_against_model(data, Audio, exclude=["id"])
    # we only perform domain-level business rule validation if the basic validation passes (does not throw)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        audio_model = Audio.schema(unknown=EXCLUDE).load(data)

    errors = []

    def wrong_type_in_list(pfield_name, expected_field_type, actual_field_value):
        errors.append({
            "detail": "'{}' is not a valid value for request field '{}', expected a list of {}s.".format(
                actual_field_value, pfield_name, expected_field_type.__name__),
            "pointer": pfield_name})

    try:
        audio_model.ticks = [float(tick) for tick in audio_model.ticks]
    except ValueError:
        wrong_type_in_list("ticks", float, audio_model.ticks)

    if len(audio_model.ticks) != 15 or min(audio_model.ticks) < -100 or max(audio_model.ticks) > -10:
        errors.append({
            "detail": f"'{audio_model.ticks}' is not a valid value for request field 'ticks', must be 15 values and range from -10.0 to -100.0"})

    if audio_model.selected_tick < 0 or audio_model.selected_tick > 14:
        errors.append({
            "detail": f"'{audio_model.ticks}' is not a valid value for request field 'selected_tick', must be between 0 and 14"})

    if len(errors) > 0:
        raise ValidationError(detailed_validation_errors=errors)

    # we enforce uniqueness constraints later in request handling, as it requires data access

    return audio_model
