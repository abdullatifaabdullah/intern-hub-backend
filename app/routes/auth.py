from fastapi import APIRouter, Depends
from app.schemas.auth_schema import SignInRequest, SignUpRequest, TokenResponse, RefreshRequest, SignOutRequest
from app.schemas.user_schema import UserOut
from app.services.auth_service import sign_up, sign_in, refresh_access_token, sign_out, get_me
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", response_model=TokenResponse)
async def route_sign_up(payload: SignUpRequest, db: AsyncSession = Depends(get_db)):
    return await sign_up(db=db, payload=payload)


@router.post("/sign-in", response_model=TokenResponse)
async def route_sign_in(payload: SignInRequest, db: AsyncSession = Depends(get_db)):
    return await sign_in(db=db, payload=payload)


@router.post("/refresh", response_model=TokenResponse)
async def route_refresh(payload: RefreshRequest):
    return await refresh_access_token(payload=payload)


@router.post("/sign-out")
async def route_sign_out(payload: SignOutRequest):
    return await sign_out(payload=payload)


@router.get("/me", response_model=UserOut)
async def route_me(current=Depends(get_me)):
    return current

 