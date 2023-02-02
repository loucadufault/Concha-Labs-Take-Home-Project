from flask import (
    Blueprint, request, jsonify, make_response
)
from src.main import ValidationError
from src.main.helpers.email_utils import normalize_email
from src.main.helpers.filename_validation_utils import is_allowed_file
from src.main.helpers.header_utils import set_resource_uri_header

from src.main.helpers.dict_utils import filter_dict
from src.main.parse_request import request_body_is_json, \
    validate_and_get_user_info_model
from src.main.services import user_infos as user_info_service

bp = Blueprint("accounts", __name__, url_prefix="/accounts")


def make_response_with_resource_header(user_info_model_with_id, status):
    response = make_response(jsonify(user_info_model_with_id), status)
    set_resource_uri_header(request, response, bp.url_prefix + "/" + str(user_info_model_with_id["id"]))
    return response


@bp.post("/")
def insert_user_info():
    request_body_is_json(request)

    user_info_model = validate_and_get_user_info_model(request.json)

    user_info_model_with_id = user_info_service.create_user_info(user_info_model)

    return make_response_with_resource_header(user_info_model_with_id, 201)


@bp.get("/<user_id>")
def get_user_info(user_id):
    return make_response_with_resource_header(user_info_service.get_user_info(user_id), 200)


@bp.get("/")
def list_user_infos():
    search = filter_dict(dict(request.args), ["name", "email", "address"])
    if "email" in search:
        search["email"] = normalize_email(search["email"])
    return make_response(jsonify(user_info_service.get_user_infos(search)), 200)


@bp.put("/<user_id>")
def update_user_info(user_id):
    request_body_is_json(request)

    user_info_model = validate_and_get_user_info_model(request.json)

    user_info_model_with_id = user_info_service.update_user_info(user_id, user_info_model)

    return make_response_with_resource_header(user_info_model_with_id, 200)


@bp.delete("/<user_id>")
def delete_user_info(user_id):
    user_info_service.delete_user_info(user_id)

    return "", 200


def get_if_allowed_file(prequest):
    # check if the post request has the file part
    if "image" not in prequest.files:
        return None

    file = prequest.files["image"]

    if file is None:
        return None

    if file.filename == '':
        raise ValidationError("Uploaded image file does not have a filename.")

    if not is_allowed_file(file.filename, ["jpeg", "png"]):
        raise ValidationError("Uploaded image filename must have a '.jpeg' or '.png' extension.")

    if file.mimetype not in ["image/jpeg", "image/png"]:
        raise ValidationError("Uploaded image file mimetype must be 'image/jpeg' or 'image/png'.")

    return file


@bp.post("/<user_id>/upload-image")
def upload_user_image(user_id):
    image_file = get_if_allowed_file(request)

    if image_file is None:
        raise ValidationError("Request must contain a form-data file 'image'.")

    user_info_model_with_id = user_info_service.upload_user_image(user_id, image_file)

    result = make_response_with_resource_header(user_info_model_with_id, 200)
    print(result)
    return result
