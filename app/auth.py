"""Password hashing + session login check.

I used PBKDF2 from the standard library so Docker does not need extra
native crypto packages. The session cookie itself is handled by
Starlette's SessionMiddleware in main.py.
"""

import hashlib
import hmac
import os

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

PBKDF2_ROUNDS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
    except (ValueError, TypeError):
        return False
    expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    return hmac.compare_digest(expected.hex(), digest_hex)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Used on POST/PUT/DELETE. GET routes stay public."""
    username = request.session.get("user")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required. POST /login first so Swagger can send the session cookie.",
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid. Please log in again.",
        )
    return user
