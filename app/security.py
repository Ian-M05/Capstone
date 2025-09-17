import os
import hmac
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from app.config import settings

PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "100000"))
SALT_BYTES = 16


def _generate_salt_hex() -> str:
    return secrets.token_hex(SALT_BYTES)


def hash_password(plain_password: str) -> str:
    salt_hex = _generate_salt_hex()
    derived_key = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS
    )
    return f"{salt_hex}${derived_key.hex()}"


def verify_password(plain_password: str, stored_value: str) -> bool:
    try:
        salt_hex, stored_hex = stored_value.split("$", 1)
    except ValueError:
        return False
    computed = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(computed.hex(), stored_hex)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
