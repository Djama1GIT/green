from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_async_session

from .repository import get_statistics, get_statistics_by_id, create_editor

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.get('/statistics/', name="admin_statistics")
async def statistics(session: AsyncSession = Depends(get_async_session)):
    return await get_statistics(session)


@router.get('/statistics/{news_id}', name="admin_statistics_by_id")
async def statistics(news_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_statistics_by_id(news_id, session)


@router.post('/reg_editor/', name="reg_editor")
async def reg_editor(email: str, session: AsyncSession = Depends(get_async_session)):
    return await create_editor(email, session)
