from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update, desc
from fastapi_cache.decorator import cache

from .chemas import NewsItem, NewsItemForInsert, NewsItemForPut
from db import get_async_session
from news.models import News

router = APIRouter(
    prefix='/news',
    tags=['News']
)


@router.get("/", response_model=List[NewsItem])
@cache(expire=60)
async def get_news(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).order_by(desc(News.id)).limit(20))
    news = result.scalars().all()
    return [i.json() for i in news]


@router.get('/{news_id}', response_model=NewsItem)
async def news_details(news_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return news.json()


@router.post("/add_news")
async def add_news(news_item: NewsItemForInsert, session: AsyncSession = Depends(get_async_session)):
    statement = insert(News).values(**news_item.dict())
    try:
        await session.execute(statement)
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add news")
    return {"status": 200}


@router.put("/edit_news")
async def edit_news(news_item: NewsItemForPut, session: AsyncSession = Depends(get_async_session)):
    statement = update(News).where(News.id == news_item.id).values(**news_item.dict())
    try:
        await session.execute(statement)
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to edit news")
    return {"status": 200}


@router.delete("/delete_news")
async def delete_news(news_id: int, session: AsyncSession = Depends(get_async_session)):
    statement = delete(News).where(News.id == news_id)
    try:
        await session.execute(statement)
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete news")
    return {"status": 200}