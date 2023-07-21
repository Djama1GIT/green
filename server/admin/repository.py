from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import PasswordHelper
from news.models import News
from auth.models import User

from .chemas import UserRegister
from tasks.tasks import send_welcome_message


async def get_statistics(session: AsyncSession):
    try:
        result = await session.execute(select(News.id, News.views))
        news = result.all()
        return [{"id": i[0], "views": i[1]} for i in news]
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get statistics")


async def get_statistics_by_id(news_id: int, session: AsyncSession):
    try:
        result = await session.execute(select(News.views).where(News.id == news_id))
        news = result.scalars().first()
        if news is None:
            raise Exception("404")
        return {"id": news_id, "views": news}
    except Exception as exc:
        if exc.args[0] == "404":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get statistics")


async def create_editor(email: str, session: AsyncSession):
    password_helper = PasswordHelper()
    password = password_helper.generate()
    statement = insert(User).values(UserRegister(
        email=email,
        hashed_password=password_helper.hash(password),
        is_active=True,
        is_superuser=False,
        is_verified=False
    ).dict())
    try:
        await session.execute(statement)
        await session.commit()
        send_welcome_message.delay(email, password)
        return {"status": 200}
    except:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register editor")