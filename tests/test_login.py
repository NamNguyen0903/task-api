
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
    assert login(username, password) is True


def test_login_wrong_password(credentials):
    username, _ = credentials
    assert login(username, "WrongPassword") is False


def test_login_wrong_username(credentials):
    _, password = credentials
    assert login("unknown", password) is False


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "password"),
        ("admin", ""),
        ("", ""),
        (None, "password"),
        ("admin", None),
        (123, "password"),
    ],
)
def test_login_invalid_inputs(credentials, username, password):
    assert login(username, password) is False


def test_login_missing_configuration(monkeypatch):
    monkeypatch.delenv("APP_USERNAME", raising=False)
    monkeypatch.delenv("APP_PASSWORD_HASH", raising=False)
    monkeypatch.delenv("APP_PASSWORD_SALT", raising=False)

    with pytest.raises(RuntimeError, match="not configured"):
        login("admin", "password")


def test_login_invalid_hash_configuration(monkeypatch):
    monkeypatch.setenv("APP_USERNAME", "admin")
    monkeypatch.setenv("APP_PASSWORD_HASH", "not-hex")
    monkeypatch.setenv("APP_PASSWORD_SALT", "not-hex")

    with pytest.raises(RuntimeError, match="Invalid authentication"):
        login("admin", "password")
