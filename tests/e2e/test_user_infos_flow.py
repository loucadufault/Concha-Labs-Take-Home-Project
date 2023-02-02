import pytest

from tests.helpers.requests_assertion import assert_ok, assert_bad_request, assert_not_found, assert_resources_count, \
    assert_no_resources, assert_data_matches_resource_ignore_id, assert_data_has_id

pytestmark = [pytest.mark.uses_server]


def with_null_image_hosted_link(user_info):
    d = dict(user_info)
    d["image_hosted_link"] = None
    return d


def get_user_info(s, user_id):
    return s.get(f"/accounts/{user_id}")


def get_user_infos(s, search={}):
    return s.get("/accounts", params=search)


def post_user_info(s, user_info):
    return s.post("/accounts", json=user_info)


def update_user_info(s, user_id, user_info):
    return s.put(f"/accounts/{user_id}", json=user_info)


def delete_user_info(s, user_id):
    return s.delete(f"/accounts/{user_id}")


def test_accounts_endpoint(http_session):
    """The test scenario implementation."""

    s = http_session

    # No accounts yet

    res = get_user_infos(s)
    assert_no_resources(assert_ok(res))  # if this fails, you need to delete all resources from server beforehand

    # Fail to create an account with invalid user info

    invalid_user_info = {
        "name": "Foo Bar",
        "email": "foo.bar@dummy.com",  # no address
    }

    res = post_user_info(s, invalid_user_info)
    assert_bad_request(res)

    res = get_user_infos(s)
    assert_no_resources(assert_ok(res))

    res = get_user_infos(s, {"name": "Foo Bar"})
    assert_no_resources(assert_ok(res))

    # Succeed to create a first account with valid user info

    first_valid_user_info = {
        "name": "Foo Bar",
        "email": "foo.bar@dummy.com",
        "address": "1234 Main Road"
    }

    res = post_user_info(s, first_valid_user_info)

    first_user_id = res.json()["id"]
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            first_user_id),
        with_null_image_hosted_link(first_valid_user_info))

    # Succeed to get and search for the first account user info

    res = get_user_info(s, first_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            first_user_id),
        with_null_image_hosted_link(first_valid_user_info))

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 1)

    res = get_user_infos(s, {"name": first_valid_user_info["name"]})
    assert_resources_count(assert_ok(res), 1)

    res = get_user_infos(s, {"email": first_valid_user_info["email"]})
    assert_resources_count(assert_ok(res), 1)

    res = get_user_infos(s, {"address": first_valid_user_info["address"]})
    assert_resources_count(assert_ok(res), 1)

    # Fail to search for an account by a name that does not exist

    res = get_user_infos(s, {"name": "DNE"})
    assert_no_resources(assert_ok(res))

    # Succeed to create a second account with valid user info

    second_valid_user_info = {
        "name": "Test User2",
        "email": "test.user2@dummy.com",
        "address": "978 Grand Blvd"
    }

    res = post_user_info(s, second_valid_user_info)
    second_user_id = res.json()["id"]
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            second_user_id),
        with_null_image_hosted_link(second_valid_user_info))

    # Succeed to get the second account user info

    res = get_user_info(s, second_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            second_user_id),
        with_null_image_hosted_link(second_valid_user_info))

    # Succeed to get both accounts

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 2)

    # Succeed to create a third account with same name as first account

    doppelganger_valid_user_info = {
        "name": "Foo Bar",
        "email": "doppelganger@dummy.com",
        "address": "1235 Main Road"
    }

    res = post_user_info(s, doppelganger_valid_user_info)
    doppelganger_user_id = res.json()["id"]
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            doppelganger_user_id),
        with_null_image_hosted_link(doppelganger_valid_user_info))

    # Succeed to get the third account user info

    res = get_user_info(s, doppelganger_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            doppelganger_user_id),
        with_null_image_hosted_link(doppelganger_valid_user_info))

    # Succeed to get all three accounts

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 3)

    # Succeed to search for both accounts by name

    res = get_user_infos(s, {"name": "Foo Bar"})
    assert_resources_count(assert_ok(res), 2)

    # Succeed to search for first account by email

    res = get_user_infos(s, {"email": first_valid_user_info["email"]})
    assert_resources_count(assert_ok(res), 1)

    # Fail to create an account with duplicate email

    duplicate_email_invalid_user_info = {
        "name": "Foo Bar",
        "email": "doppelganger@dummy.com",
        "address": "1235 Main Road"
    }

    res = post_user_info(s, duplicate_email_invalid_user_info)
    assert_bad_request(res)

    # Succeed to get still three accounts

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 3)

    # Fail to update an account with duplicate email

    duplicate_email_invalid_user_info = {
        "name": "New Name",
        "email": second_valid_user_info["email"],
        "address": "1235 New Addr"
    }

    res = update_user_info(s, first_user_id, duplicate_email_invalid_user_info)
    assert_bad_request(res)

    # Succeed to get the first account old user info

    res = get_user_info(s, first_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            first_user_id),
        with_null_image_hosted_link(first_valid_user_info))

    # Succeed to get still three accounts

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 3)

    # Succeed to delete first user account

    res = delete_user_info(s, first_user_id)
    assert_ok(res)

    # Fail to get or search for deleted first user account

    res = get_user_info(s, first_user_id)
    assert_not_found(res)

    res = get_user_infos(s, {"name": first_valid_user_info["name"]})
    assert_resources_count(assert_ok(res), 1)

    res = get_user_infos(s, {"email": first_valid_user_info["email"]})
    assert_no_resources(assert_ok(res))

    res = get_user_infos(s, {"address": first_valid_user_info["address"]})
    assert_no_resources(assert_ok(res))

    # Succeed to get both remaining accounts

    res = get_user_infos(s)
    assert_resources_count(assert_ok(res), 2)

    res = get_user_info(s, second_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            second_user_id),
        with_null_image_hosted_link(second_valid_user_info))

    res = get_user_info(s, doppelganger_user_id)
    assert_data_matches_resource_ignore_id(
        assert_data_has_id(
            assert_ok(res),
            doppelganger_user_id),
        with_null_image_hosted_link(doppelganger_valid_user_info))
