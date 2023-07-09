from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .chemas import NewsItem
from db import get_async_session
from news.models import News

router = APIRouter(
    prefix='/news',
    tags=['News']
)


@router.get("/", response_model=Dict[str, List[NewsItem]])
async def root(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News))
    news = result.scalars().all()
    return {'news': [i.json() for i in news]}


@router.get('/{news_id}', response_model=Dict[str, NewsItem])
async def news_detail(news_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    return {'news': news.json()}
