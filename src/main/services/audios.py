import json
import re

from src.main.exceptions import ValidationError
from src.main.data_sources.buckets.audios import get_audio_bucket
from src.main.exceptions import NoSuchInstanceError


def build_audio_blob_name(session_id):
    return f"session_{str(session_id)}-audio.json"


def extract_session_id(blob_name):
    match = re.search(r"^session_(\d+)-audio.json$", blob_name)
    try:
        if match:
            return int(match.group(1))
    except Exception:
        pass

    raise ValueError("Blob name does not conform to expected format.")


def create_audio(audio_model):
    audio_bucket = get_audio_bucket()

    existing_blobs = audio_bucket.list_blobs()
    existing_session_ids = [extract_session_id(blob.name) for blob in existing_blobs]

    if audio_model.session_id in existing_session_ids:
        raise ValidationError(f"Audio file with session_id {audio_model.session_id} already exists.")

    audio_bucket \
        .blob(build_audio_blob_name(audio_model.session_id)) \
        .upload_from_string(audio_model.to_json(), content_type="application/json")

    return audio_model.to_dict()


def get_audio(session_id):
    audio_bucket = get_audio_bucket()

    audio_blob = audio_bucket.get_blob(build_audio_blob_name(session_id))
    if audio_blob is None:
        raise NoSuchInstanceError(f"No audio file exists with session_id '{session_id}'.")

    return json.loads(audio_blob.download_as_text())


def get_audios():
    audio_bucket = get_audio_bucket()
    audio_blobs_iterator = audio_bucket.list_blobs()

    # this is potentially very slow since sdk does not seem to allow for batch downloading of bucket blobs
    # at the minimum it should be paginated
    # it is kept for completeness
    return [json.loads(audio_blob.download_as_text()) for audio_blob in audio_blobs_iterator]


def update_audio(_, audio_model):
    # there are no "versioning" or "lifecycle" policies defined on the blob's bucket,
    # so upload will overwrite any existing contents anyway
    audio_bucket = get_audio_bucket()

    audio_bucket \
        .blob(build_audio_blob_name(audio_model.session_id)) \
        .upload_from_string(audio_model.to_json(), content_type="application/json")

    return audio_model.to_dict()


def delete_audio(session_id):
    audio_bucket = get_audio_bucket()
    audio_bucket.delete_blobs((build_audio_blob_name(session_id),), on_error=lambda *args: None)  # suppress if does not exist
