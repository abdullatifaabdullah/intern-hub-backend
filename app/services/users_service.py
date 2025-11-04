from __future__ import annotations

from app.models.user import User


async def get_current_user_info(user: User) -> User:
    return user


