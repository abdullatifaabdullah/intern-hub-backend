from __future__ import annotations

from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, get_current_user
from app.models.user import User
from app.schemas.auth_schema import SignInRequest, TokenResponse, RefreshRequest, SignOutRequest


async def sign_in(db: AsyncSession, payload: SignInRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    claims = {"sub": str(user.id), "role": user.role}
    access = create_access_token(claims)
    refresh = None if settings.STATELESS_STRICT else create_refresh_token(claims)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRES_MIN)


async def refresh_access_token(payload: RefreshRequest) -> TokenResponse:
    if settings.STATELESS_STRICT:
        raise HTTPException(status_code=400, detail="Refresh disabled in stateless strict mode")
    try:
        decoded = jwt.decode(payload.refresh_token, settings.JWT_SECRET, algorithms=["HS256"])
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    claims = {k: decoded[k] for k in ("sub", "role")}
    access = create_access_token(claims)
    refresh = create_refresh_token(claims)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRES_MIN)


async def sign_out(payload: SignOutRequest):
    # Stateless: nothing to do. If token store is implemented, revoke here.
    return {"ok": True}


async def get_me(current=Depends(get_current_user)):
    return current


