import os
import tempfile
from requests_toolbelt import sessions
import pytest

from src.main import create_app
from src.main.data_sources.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "test_data", "seed.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def pytest_addoption(parser):
    parser.addoption("--server_url", action="store")  # , default="http://localhost:5000")


@pytest.fixture(scope="session")
def http_session(pytestconfig):
    server_url = pytestconfig.getoption("server_url")
    if server_url is None:
        pytest.fail("Tests ran require a server endpoint to be run against.")

    print("Configuring tests to run against server url: " + server_url)
    return sessions.BaseUrlSession(
        base_url=server_url)
