import pytest
from src.main import create_app


pytestmark = [pytest.mark.infra]


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
