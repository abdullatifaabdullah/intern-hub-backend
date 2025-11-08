from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# Use bcrypt directly to avoid passlib's bug detection issue
# Passlib's CryptContext has a bug during initialization that causes errors
import bcrypt


class BcryptContext:
    """Simple bcrypt wrapper to replace passlib CryptContext"""
    def hash(self, password: str) -> str:
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify(self, password: str, hashed: str) -> bool:
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

pwd_context = BcryptContext()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/sign-in")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(claims: dict, expires_minutes: int | None = None) -> str:
    to_encode = claims.copy()
    expire = _now_utc() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRES_MIN)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(claims: dict, expires_minutes: int | None = None) -> str:
    to_encode = claims.copy()
    expire = _now_utc() + timedelta(minutes=expires_minutes or settings.REFRESH_TOKEN_EXPIRES_MIN)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


class TokenData(BaseModel):
    sub: str
    role: str


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        sub: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if sub is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    result = await db.execute(select(User).where(User.id == int(sub)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


async def require_student(user: Annotated[User, Depends(get_current_user)]):
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student required")
    return user


