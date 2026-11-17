
import hashlib

import pytest

from login import login


@pytest.fixture
def credentials(monkeypatch):
    username = "admin"
    password = "StrongPassword123!"
    salt = b"test-salt-for-unit-tests"

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )

    monkeypatch.setenv("APP_USERNAME", username)
    monkeypatch.setenv("APP_PASSWORD_HASH", hashed.hex())
    monkeypatch.setenv("APP_PASSWORD_SALT", salt.hex())

    return username, password


def test_login_success(credentials):
    username, password = credentials

    assert login(username, password) == {
        "success": True,
        "message": "Login successful",
    }


@pytest.mark.parametrize(
    "username,password",
    [
        (None, "password"),
        ("admin", None),
        (123, "password"),
        ("admin", 123),
        ([], "password"),
        ({}, "password"),
    ],
)
def test_invalid_input_type(username, password):
    assert login(username, password) == {
        "success": False,
        "message": "Invalid input type",
    }


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "password"),
        ("admin", ""),
        ("", ""),
        ("   ", "password"),
        ("admin", "   "),
    ],
)
def test_required_fields(username, password):
    assert login(username, password) == {
        "success": False,
        "message": "Username and password are required",
    }


@pytest.mark.parametrize(
    "username,password",
    [
        ("unknown", "StrongPassword123!"),
        ("admin", "WrongPassword"),
        ("unknown", "WrongPassword"),
    ],
)
def test_invalid_credentials(credentials, username, password):
    assert login(username, password) == {
        "success": False,
        "message": "Invalid credentials",
    }


def test_missing_configuration(monkeypatch):
    monkeypatch.delenv("APP_USERNAME", raising=False)
    monkeypatch.delenv("APP_PASSWORD_HASH", raising=False)
    monkeypatch.delenv("APP_PASSWORD_SALT", raising=False)

    with pytest.raises(RuntimeError, match="not configured"):
        login("admin", "password")


def test_invalid_configuration(monkeypatch):
    monkeypatch.setenv("APP_USERNAME", "admin")
    monkeypatch.setenv("APP_PASSWORD_HASH", "invalid-hex")
    monkeypatch.setenv("APP_PASSWORD_SALT", "invalid-hex")

    with pytest.raises(RuntimeError, match="Invalid authentication"):
        login("admin", "password")
