import json
from typing import List

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update, desc, func
from fastapi_cache.decorator import cache
from fastapi_users import FastAPIUsers

from .chemas import NewsItem, NewsItemForInsert, NewsItemForPut
from db import get_async_session
from news.models import News
from auth.models import User
from auth.auth import auth_backend
from auth.manager import get_user_manager
from tasks.tasks import send_newsletter_for_email

router = APIRouter(
    prefix='/news',
    tags=['News']
)
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


@router.get("/", response_model=List[NewsItem])
@cache(expire=60)
async def get_news(page: int = 1, size: int = 10, session: AsyncSession = Depends(get_async_session)):
    offset = (page - 1) * size
    result = await session.execute(select(News).order_by(desc(News.id)).offset(offset).limit(size))
    news = result.scalars().all()
    total_count = await session.execute(select(func.count(News.id)))
    response = Response(content=json.dumps([i.json() for i in news]), media_type="application/json")
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    response.headers["X-Total-Count"] = str(total_count.scalar())
    return response


@router.get('/{news_id}', response_model=NewsItem)
async def news_details(news_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return news.json()


@router.post("/add_news", dependencies=[Depends(fastapi_users.current_user(active=True))])
async def add_news(news_item: NewsItemForInsert,
                   session: AsyncSession = Depends(get_async_session)):
    news_item = news_item.dict()
    news_item = ({"id": news_item["id"]} if news_item["id"] else {}) | \
                 {
                     "title": news_item["title"],
                     "description": news_item["description"],
                     "content": news_item["content"],
                 }
    statement = insert(News).values(**news_item)
    try:
        await session.execute(statement)
        await session.commit()
        statement = select(User.email)
        result = await session.execute(statement)
        users = result.all()
        for user in users:
            try:
                send_newsletter_for_email.delay(user.email, news_item)
            except Exception as exc:
                print(exc)
                print(f"Не удалось отправить рассылку пользователю {user.email}")
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add news")


@router.put("/edit_news", dependencies=[Depends(fastapi_users.current_user(active=True))])
async def edit_news(news_item: NewsItemForPut, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).where(News.id == news_item.id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"News not found ({news_item.id})")
    statement = update(News).where(News.id == news_item.id).values(**news_item.dict())
    try:
        await session.execute(statement)
        await session.commit()
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to edit news")


@router.delete("/delete_news", dependencies=[Depends(fastapi_users.current_user(active=True))])
async def delete_news(news_id: int, session: AsyncSession = Depends(get_async_session)):
    statement = delete(News).where(News.id == news_id)
    try:
        await session.execute(statement)
        await session.commit()
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete news")
