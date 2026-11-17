
import hashlib
import hmac
import os


def hash_password(password: str, salt: bytes) -> bytes:
    """Hash password using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )


def login(username: str, password: str) -> dict:
    """Validate input and authenticate user."""

    # 1. Validate input types
    if not isinstance(username, str) or not isinstance(password, str):
        return {
            "success": False,
            "message": "Invalid input type",
        }

    # 2. Validate required fields
    if not username.strip() or not password.strip():
        return {
            "success": False,
            "message": "Username and password are required",
        }

    # 3. Load credentials from environment
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

    # 4. Verify credentials
    candidate_hash = hash_password(password, salt)

    username_valid = hmac.compare_digest(username, expected_username)
    password_valid = hmac.compare_digest(candidate_hash, stored_hash)

    if not (username_valid and password_valid):
        return {
            "success": False,
            "message": "Invalid credentials",
        }

    # 5. Authentication successful
    return {
        "success": True,
        "message": "Login successful",
    }
