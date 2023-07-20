import json
import re

from uuid import uuid4

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update, desc, func
from fastapi_cache.decorator import cache
from fastapi_users import FastAPIUsers

from .chemas import NewsItem, NewsItemForInsert, NewsItemForPut
from db import get_async_session
from news.models import Category, News, Follower
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


@router.get("/categories", name="news_categories")
async def categories(session: AsyncSession = Depends(get_async_session)):
    statement = select(Category)
    try:
        result = await session.execute(statement)
        return result.scalars().all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/follow", name="news_follow")
async def follow(email: str, session: AsyncSession = Depends(get_async_session)):
    statement = select(Follower).where(Follower.email == email)
    try:
        result = await session.execute(statement)
        if result.scalars().all():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Follower already exists")
        if not re.fullmatch("^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid Email")
        uuid = uuid4()
        token = Follower.generate_token(uuid, email)
        await session.execute(insert(Follower).values(uuid=uuid, email=email, token=token))
        await session.commit()
        return {"status": 200}
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to follow")


@router.get("/unfollow", name="news_unfollow")
async def unfollow(token: str, session: AsyncSession = Depends(get_async_session)):
    statement = select(Follower).where(Follower.token == token)
    try:
        result = await session.execute(statement)
        if not result.scalars().all():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")
        await session.execute(delete(Follower).where(Follower.token == token))
        await session.commit()
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unfollow")


@router.get('/{news_id}', response_model=NewsItem, name="news_by_id")
async def news_details(news_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return news.json()


@router.get("/", response_model=List[NewsItem], name="news_list")
@cache(expire=60)
async def get_news(page: int = 1,
                   size: int = 10,
                   category: Optional[str] = None,
                   session: AsyncSession = Depends(get_async_session)):
    size = min(size, 50)
    offset = (page - 1) * size
    statement = select(News)
    if category:
        statement = statement.where(News.category == category)
    statement = statement.order_by(desc(News.time)).offset(offset).limit(size)

    result = await session.execute(statement)
    news = result.scalars().all()
    total_count = await session.execute(select(func.count(News.id)))
    response = Response(content=json.dumps([i.json() for i in news]), media_type="application/json")
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    response.headers["X-Total-Count"] = str(total_count.scalar())
    return response


@router.post("/add_news", name="add_news")
async def add_news(request: Request,
                   news_item: NewsItemForInsert,
                   session: AsyncSession = Depends(get_async_session),
                   user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("add_news" not in user.permissions or not user.permissions["add_news"]):
        raise HTTPException(status_code=403,
                            detail=f"User does not have required permissions")
    statement = insert(News).values(**{k: v for k, v in news_item.dict().items() if v is not None})
    try:
        await session.execute(statement)
        await session.commit()
        statement = select(Follower.email, Follower.token)
        result = await session.execute(statement)
        followers = result.all()
        for follower in followers:
            try:
                send_newsletter_for_email.delay(follower.email,
                                                follower.token,
                                                str(request.url_for("news_unfollow")),
                                                news_item.dict())
                import logging
            except Exception as exc:
                print(exc)
                print(f"Не удалось отправить рассылку фолловеру {follower.email}")
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add news")


@router.put("/edit_news", name="edit_news")
async def edit_news(news_item: NewsItemForPut, session: AsyncSession = Depends(get_async_session),
                    user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("edit_news" not in user.permissions or not user.permissions["edit_news"]):
        raise HTTPException(status_code=403, detail="User does not have required permissions")
    result = await session.execute(select(News).where(News.id == news_item.id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"News not found")
    statement = update(News).where(News.id == news_item.id).values(**news_item.dict())
    try:
        await session.execute(statement)
        await session.commit()
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to edit news")


@router.delete("/delete_news", name="delete_news")
async def delete_news(news_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("delete_news" not in user.permissions or not user.permissions["delete_news"]):
        raise HTTPException(status_code=403, detail="User does not have required permissions")
    statement = delete(News).where(News.id == news_id)
    try:
        await session.execute(statement)
        await session.commit()
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete news")
