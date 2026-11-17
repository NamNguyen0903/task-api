
import hashlib
import hmac
import os


def hash_password(password: str, salt: bytes) -> bytes:
    """Create a PBKDF2-HMAC-SHA256 password hash."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )


def login(username: str, password: str) -> bool:
    """Validate user credentials securely."""
    if not isinstance(username, str) or not isinstance(password, str):
        return False

    if not username or not password:
        return False

    expected_username = os.getenv("APP_USERNAME")
    password_hash = os.getenv("APP_PASSWORD_HASH")
    password_salt = os.getenv("APP_PASSWORD_SALT")

    if not all([expected_username, password_hash, password_salt]):
        raise RuntimeError("Authentication is not configured")

    try:
        stored_hash = bytes.fromhex(password_hash)
        salt = bytes.fromhex(password_salt)
    except ValueError as exc:
        raise RuntimeError("Invalid authentication configuration") from exc

    candidate_hash = hash_password(password, salt)

    return (
        hmac.compare_digest(username, expected_username)
        & hmac.compare_digest(candidate_hash, stored_hash)
    )
