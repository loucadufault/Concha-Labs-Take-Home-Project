import requests

"""The assertion functions are defined to support chaining, so they return the given res (as is).
For example: assert_no_resources(assert_ok(res))
"""


def assert_ok(res):
    assert res.status_code == requests.codes.ok or str(res.status_code)[0] == "2"  # 2xx
    return res


def assert_bad_request(res):
    assert res.status_code == 400
    return res


def assert_not_found(res):
    assert res.status_code == 404
    return res


def assert_resources_count(res, count):
    assert len(res.json()) == count
    return res


def assert_no_resources(res):
    return assert_resources_count(res, 0)


def assert_data_matches_resource(res, resource):
    assert res.json() == resource
    return res


def assert_data_matches_resource_ignore_id(res, resource):
    res_json = dict(res.json())
    resource_copy = dict(resource)
    if "id" in res_json:
        del res_json["id"]
    if "id" in resource_copy:
        del resource_copy["id"]
    assert res_json == resource_copy
    return res


def assert_data_has_id(res, pid=None):
    res_json = res.json()
    assert "id" in res_json
    if pid is not None:
        assert res_json["id"] == pid
    return res
