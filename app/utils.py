# app/utils.py
import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return the hashed password as a string
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Check if the hashed password matches the plain password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(username: str, expires_delta: timedelta):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    print(f"Token will expire at: {expire}")  # Debug: Print expiration time
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(username: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
