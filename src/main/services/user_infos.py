from src.main import ValidationError
from src.main.data_sources.db import get_db
from src.main.data_sources.buckets.images import get_image_bucket
from src.main.exceptions import NoSuchInstanceError


def create_user_info(user_info_model):
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO user_info (name, email, address) VALUES (?, ?, ?)",
            (user_info_model.name, user_info_model.email, user_info_model.address),
        )
        db.commit()

        # would use RETURNING * on above query to fetch from same cursor,
        # but this is not supported in std lib sqlite3 coming with Python3 version that is stable for GCP client libraries :/
        # hence we do a second query
        user_info = get_user_info(cursor.lastrowid)

        return user_info
    except db.IntegrityError as e:
        raise ValidationError(f"Email '{user_info_model.email}' is already registered.")


def get_user_info(user_id):
    db = get_db()
    user_info = db.execute(
        "SELECT * FROM user_info WHERE id = ?", (user_id,)
    ).fetchone()

    if user_info is None:
        raise NoSuchInstanceError(f"No user info exists with id '{user_id}'.")

    return user_info


def get_user_infos(search):
    db = get_db()

    conjunction_condition_terms = [f"{k} = '{v}'" for k, v in search.items()]
    where_clause = "WHERE " + " AND ".join(conjunction_condition_terms)
    return db.execute(f"SELECT * FROM user_info{' ' + where_clause if len(conjunction_condition_terms) > 0 else ''}").fetchall()


def update_user_info(user_id, user_info_model):
    db = get_db()
    try:
        cursor = db.execute(
            "UPDATE user_info SET name = ?, address = ?, email = ? WHERE id = ?",
            (user_info_model.name, user_info_model.address, user_info_model.email, user_id)
        )
        db.commit()

        if cursor.rowcount == 0:
            raise NoSuchInstanceError(f"No user info exists with id '{user_id}'.")

        return get_user_info(user_id)
    except db.IntegrityError:
        raise ValidationError(f"Email '{user_info_model.email}' is already registered.")


def delete_user_info(user_id):
    db = get_db()
    db.execute("DELETE FROM user_info WHERE id = ?", (user_id,))
    db.commit()

    image_bucket = get_image_bucket()

    image_bucket.delete_blobs(build_image_blob_name(user_id), on_error=lambda *args: None)  # suppress if does not exist


def build_image_blob_name(user_id):
    return f"user_{str(user_id)}-image"  # filename omitted, as it won't be known at retrieval time, and does not matter


def upload_user_image(user_id, image_file):
    get_user_info(user_id)  # assert that the basic user info has been created first

    image_bucket = get_image_bucket()

    image_blob_name = build_image_blob_name(user_id)

    # replace existing image, if any
    image_bucket.delete_blobs((image_blob_name,), on_error=lambda *args: None)  # suppress if does not exist

    image_blob = image_bucket.blob(image_blob_name)

    image_blob.upload_from_string(image_file.read(), image_file.mimetype)

    db = get_db()
    db.execute(
        "UPDATE user_info SET image_hosted_link = ? WHERE id = ?",
        (image_blob.media_link, user_id)
    )
    db.commit()

    return get_user_info(user_id)
