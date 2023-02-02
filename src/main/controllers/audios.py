from flask import (
    Blueprint, request, jsonify, make_response
)
import json
from src.main import ValidationError
from src.main.helpers.filename_validation_utils import is_allowed_file
from src.main.helpers.header_utils import set_resource_uri_header
from src.main.parse_request import request_body_is_json, \
    validate_and_get_audio_model
from src.main.services import audios as audios_service

bp = Blueprint("audios", __name__, url_prefix="/audios")


def get_if_allowed_file(prequest):
    # check if the post request has the file part
    if "audio" not in prequest.files:
        return None

    file = prequest.files["audio"]

    if file is None:
        return None

    if file.filename == '':
        raise ValidationError("Uploaded audio data file does not have a filename.")

    if not is_allowed_file(file.filename, ["json"]):
        raise ValidationError("Uploaded audio data filename must have a '.json' extension.")

    return file


def get_data_from_request():
    file = get_if_allowed_file(request)
    if file is None:
        request_body_is_json(request)

        if request.mimetype != "application/json":
            raise ValidationError("Request did not contain a form-data file 'audio', and request body is not JSON.")

        data = request.json
    else:
        # Opening JSON file
        # with open(file, encoding="utf-8") as json_file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError as e:
            raise ValidationError("Malformed JSON file: " + e.msg)

    return data


def make_response_with_resource_header(audio_model_with_id, status):
    response = make_response(jsonify(audio_model_with_id), status)
    set_resource_uri_header(request, response, bp.url_prefix + "/" + str(audio_model_with_id["session_id"]))
    return response


@bp.post("/")
def insert_audio():
    data = get_data_from_request()

    audio_model = validate_and_get_audio_model(data)

    audio_model_with_id = audios_service.create_audio(audio_model)

    return make_response_with_resource_header(audio_model_with_id, 201)


@bp.get("/<session_id>")
def get_audio(session_id):
    return make_response_with_resource_header(audios_service.get_audio(session_id), 200)


@bp.get("/")
def list_audios():
    result = make_response(jsonify(audios_service.get_audios()), 200)
    return result


@bp.put("/<session_id>")
def update_audio(session_id):
    data = get_data_from_request()

    audio_model = validate_and_get_audio_model(data)

    audios_service.get_audio(session_id)  # ensure it exists already

    if audio_model.session_id != session_id:
        raise ValidationError("Cannot modify an existing audio file's session_id.")

    audio_model_with_id = audios_service.update_audio(session_id, audio_model)

    return make_response_with_resource_header(audio_model_with_id, 200)


@bp.delete("/<session_id>")
def delete_audio(session_id):
    audios_service.delete_audio(session_id)

    return "", 200
