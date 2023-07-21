from uuid import uuid4
import re
import json

from typing import Optional

from sqlalchemy import delete, select, update, insert, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response, status

from .models import Category, News, Follower
from .chemas import NewsItemForPut, NewsItemForInsert

from tasks.tasks import send_newsletter_for_email
from urls import Urls


async def categories_repository(session: AsyncSession):
    statement = select(Category)
    try:
        result = await session.execute(statement)
        return result.scalars().all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def follow_repository(email: str, session: AsyncSession):
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


async def unfollow_repository(token: str, session: AsyncSession):
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


async def news_details_repository(news_id: int, session: AsyncSession):
    result = await session.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return news.json()


async def news_repository(page: int, size: int, category: Optional[str], session: AsyncSession):
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


async def add_news_repository(news_item: NewsItemForInsert, session: AsyncSession):
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
                                                Urls.get("news_unfollow"),
                                                news_item.dict())
                import logging
            except Exception as exc:
                print(exc)
                print(f"Не удалось отправить рассылку фолловеру {follower.email}")
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add news")


async def update_news_repository(news_item: NewsItemForPut, session: AsyncSession):
    result = await session.execute(select(News).where(News.id == news_item.id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    statement = update(News).where(News.id == news_item.id).values(**news_item.dict())
    try:
        await session.execute(statement)
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to edit news")


async def delete_news_repository(news_id: int, session: AsyncSession):
    statement = delete(News).where(News.id == news_id)
    try:
        await session.execute(statement)
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete news")
