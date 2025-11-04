from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserOut
from app.services.users_service import get_current_user_info
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def route_users_me(current=Depends(get_current_user)):
    return await get_current_user_info(current)

 