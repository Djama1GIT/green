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


class NewsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def categories(self):
        statement = select(Category)
        try:
            result = await self.session.execute(statement)
            return result.scalars().all()
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def follow(self, email: str):
        statement = select(Follower).where(Follower.email == email)
        try:
            result = await self.session.execute(statement)
            if result.scalars().all():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Follower already exists")
            if not re.fullmatch("^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid Email")
            uuid = uuid4()
            token = Follower.generate_token(uuid, email)
            await self.session.execute(insert(Follower).values(uuid=uuid, email=email, token=token))
            await self.session.commit()
            return {"status": 200}
        except Exception as exc:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to follow")

    async def unfollow(self, token: str):
        statement = select(Follower).where(Follower.token == token)
        try:
            result = await self.session.execute(statement)
            if not result.scalars().all():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")
            await self.session.execute(delete(Follower).where(Follower.token == token))
            await self.session.commit()
            return {"status": 200}
        except:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unfollow")

    async def news_details(self, news_id: int):
        result = await self.session.execute(select(News).where(News.id == news_id))
        news = result.scalars().first()
        if not news:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        return news.json()

    async def news(self, page: int, size: int, category: Optional[str]):
        size = min(size, 50)
        offset = (page - 1) * size
        statement = select(News)
        if category:
            statement = statement.where(News.category == category)
        statement = statement.order_by(desc(News.time)).offset(offset).limit(size)

        result = await self.session.execute(statement)
        news = result.scalars().all()
        total_count = await self.session.execute(select(func.count(News.id)))
        response = Response(content=json.dumps([i.json() for i in news]), media_type="application/json")
        response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
        response.headers["X-Total-Count"] = str(total_count.scalar())
        return response

    async def add_news(self, news_item: NewsItemForInsert):
        statement = insert(News).values(**{k: v for k, v in news_item.dict().items() if v is not None})
        try:
            await self.session.execute(statement)
            await self.session.commit()
            statement = select(Follower.email, Follower.token)
            result = await self.session.execute(statement)
            followers = result.all()
            for follower in followers:
                try:
                    send_newsletter_for_email.delay(
                        follower.email,
                        follower.token,
                        Urls.get("news_unfollow"),
                        news_item.dict()
                    )
                    import logging
                except Exception as exc:
                    print(exc)
                    print(f"Не удалось отправить рассылку фолловеру {follower.email}")
            return {"status": 200}
        except:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add news")

    async def update_news(self, news_item: NewsItemForPut):
        result = await self.session.execute(select(News).where(News.id == news_item.id))
        news = result.scalars().first()
        if not news:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        statement = update(News).where(News.id == news_item.id).values(**news_item.dict())
        try:
            await self.session.execute(statement)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to edit news")

    async def delete_news(self, news_id: int):
        statement = delete(News).where(News.id == news_id)
        try:
            await self.session.execute(statement)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete news")
