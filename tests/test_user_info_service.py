import pytest as pytest

from src.main.data_sources.db import get_db
from src.main.exceptions import ValidationError
from src.main.models import UserInfo
from src.main.services import user_infos as user_info_service


def get_valid_user_info_model():
    return UserInfo.from_dict({
        "name": "Foo bar",
        "email": "foo.bar@gmail.com",
        "address": "1000 Palm Springs"
    })


def test_create_user_info_valid(app):
    test_data = get_valid_user_info_model()
    with app.app_context():
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        user_info = user_info_service.create_user_info(test_data)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        new_user_info_row = db.execute("SELECT * FROM user_info WHERE id = ?", (user_info["id"],)).fetchone()

    assert user_info["name"] == test_data.name
    assert user_info["email"] == test_data.email
    assert user_info["address"] == test_data.address
    assert user_info["image_hosted_link"] is None

    assert new_user_info_row["name"] == test_data.name
    assert new_user_info_row["email"] == test_data.email
    assert new_user_info_row["address"] == test_data.address

    assert initial_row_count + 1 == final_row_count


def test_create_user_info_duplicate_email(app):
    test_data = get_valid_user_info_model()
    test_data.email = "test.user@dummy.com"
    with app.app_context():
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        with pytest.raises(ValidationError):
            user_info_service.create_user_info(test_data)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]

    assert initial_row_count == final_row_count


def test_get_user_info_existing(app):
    user_id = 1
    with app.app_context():
        user_info = user_info_service.get_user_info(user_id)

    assert user_info["id"] == user_id
    assert user_info["name"] == "Test User"
    assert user_info["email"] == "test.user@dummy.com"
    assert user_info["address"] == "1234 Main Road"


def test_get_user_infos(app):
    with app.app_context():
        user_infos = user_info_service.get_user_infos({})

    assert len(user_infos) == 2


def test_get_user_infos_search_by_existing_name(app):
    search_name = "Test User"
    with app.app_context():
        user_infos = user_info_service.get_user_infos({"name": search_name})

    assert len(user_infos) == 1
    assert user_infos[0]["name"] == search_name


def test_get_user_infos_search_by_nonexisting_name(app):
    search_name = "DNE"
    with app.app_context():
        user_infos = user_info_service.get_user_infos({"name": search_name})

    assert len(user_infos) == 0


def test_update_user_info_valid(app):
    user_id = 1
    test_data = get_valid_user_info_model()
    with app.app_context():
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        user_info = user_info_service.update_user_info(user_id, test_data)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        updated_user_info_row = db.execute("SELECT * FROM user_info WHERE id = ?", (user_id,)).fetchone()

    assert user_info["id"] == user_id
    assert user_info["name"] == test_data.name
    assert user_info["email"] == test_data.email
    assert user_info["address"] == test_data.address

    assert updated_user_info_row["name"] == test_data.name
    assert updated_user_info_row["email"] == test_data.email
    assert updated_user_info_row["address"] == test_data.address

    assert initial_row_count == final_row_count


def test_update_user_info_only_name_valid(app):
    user_id = 1
    test_data = get_valid_user_info_model()
    test_data.email = "test.user@dummy.com"
    test_data.address = "1234 Main Road"
    with app.app_context():
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        user_info = user_info_service.update_user_info(user_id, test_data)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        updated_user_info_row = db.execute("SELECT * FROM user_info WHERE id = ?", (user_id,)).fetchone()

    assert user_info["id"] == user_id
    assert user_info["name"] == test_data.name
    assert user_info["email"] == test_data.email
    assert user_info["address"] == test_data.address

    assert updated_user_info_row["name"] == test_data.name
    assert updated_user_info_row["email"] == test_data.email
    assert updated_user_info_row["address"] == test_data.address

    assert initial_row_count == final_row_count


def test_update_user_info_duplicate_email(app):
    user_id = 1
    test_data = get_valid_user_info_model()
    test_data.email = "second.user@dummy.com"
    with app.app_context():
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        with pytest.raises(ValidationError):
            user_info_service.update_user_info(user_id, test_data)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]

    assert initial_row_count == final_row_count


def test_delete_user_info_existing(app, monkeypatch):
    user_id = 1

    class Recorder(object):
        called = False

    class FakeBucket:
        @staticmethod
        def delete_blobs(*args, **kwargs):
            Recorder.called = True

    with app.app_context():
        monkeypatch.setattr('src.main.services.user_infos.get_image_bucket', lambda: FakeBucket())
        db = get_db()
        initial_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        user_info_service.delete_user_info(user_id)
        final_row_count = db.execute("SELECT COUNT() FROM user_info").fetchone()["COUNT()"]
        deleted_user_info_row = db.execute("SELECT * FROM user_info WHERE id = ?", (user_id,)).fetchone()

    assert initial_row_count - 1 == final_row_count
    assert deleted_user_info_row is None
    assert Recorder.called  # deleted user info image from bucket
