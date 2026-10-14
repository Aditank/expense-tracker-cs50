
import os
import tempfile

import pytest

_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["EXPENSE_DB"] = _db_path

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_homepage_redirects_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.location == "/login"


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/register")

    assert response.status_code == 200


def test_register_creates_user(client):
    response = client.post(
        "/register",
        data={"username": "testuser", "password": "testpassword123"},
    )

    assert response.status_code == 302
    assert response.location == "/login"


def test_login_with_invalid_credentials(client):
    response = client.post(
        "/login",
        data={"username": "missinguser", "password": "wrongpassword"},
    )

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Invalid credentials"


def teardown_module():
    if os.path.exists(_db_path):
        os.remove(_db_path)
