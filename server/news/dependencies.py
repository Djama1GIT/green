from fastapi import HTTPException, Depends

from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from utils.utils import fastapi_users
from .repository import NewsRepository


def check_permissions(permission: str):
    def _check_permissions(user: User = Depends(fastapi_users.current_user())):
        if not user.is_superuser and (permission not in user.permissions or not user.permissions[permission]):
            raise HTTPException(status_code=403, detail="User does not have required permissions")
        return True

    return _check_permissions


def get_news_repository(get_async_session):
    def _get_news_repository(session: AsyncSession = Depends(get_async_session)) -> NewsRepository:
        return NewsRepository(session)

    return _get_news_repository
