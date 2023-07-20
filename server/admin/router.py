from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import PasswordHelper
from db import get_async_session
from news.models import News
from auth.models import User

from .chemas import UserRegister
from tasks.tasks import send_welcome_message

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.get('/statistics/', name="admin_statistics")
async def statistics(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(News.id, News.views))
        news = result.all()
        return [{"id": i[0], "views": i[1]} for i in news]
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get statistics")


@router.get('/statistics/{news_id}', name="admin_statistics_by_id")
async def statistics(news_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(News.views).where(News.id == news_id))
        news = result.scalars().first()
        if not news:
            raise Exception("404")
        return {"id": news_id, "views": news}
    except Exception as exc:
        if exc.args[0] == "404":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get statistics")


@router.post('/reg_editor/', name="reg_editor")
async def reg_editor(email: str, session: AsyncSession = Depends(get_async_session)):
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
