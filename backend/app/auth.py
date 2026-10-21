import hashlib, hmac, os, time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .models import User

SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me")
bearer = HTTPBearer(auto_error=False)


def hash_password(pw: str) -> str:
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100_000)
    return f"{salt.hex()}${h.hex()}"


def verify_password(pw: str, stored: str) -> bool:
    salt_hex, h_hex = stored.split("$")
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), 100_000)
    return hmac.compare_digest(h.hex(), h_hex)


def create_token(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 7 * 86400}, SECRET, algorithm="HS256")


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Guest -> None. Token hợp lệ -> User."""
    if not creds:
        return None
    try:
        uid = int(jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])["sub"])
    except Exception:
        return None
    return db.get(User, uid)


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if not user:
        raise HTTPException(401, "Cần đăng nhập")
    return user
