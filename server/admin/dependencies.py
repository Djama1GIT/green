from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import AdminRepository


def get_admin_repository(get_async_session):
    def _get_admin_repository(session: AsyncSession = Depends(get_async_session)) -> AdminRepository:
        return AdminRepository(session)

    return _get_admin_repository
