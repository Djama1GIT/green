from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from news.models import News

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.get('/statistics/')
async def statistics(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(News.id, News.views))
        news = result.all()
        return [{"id": i[0], "views": i[1]} for i in news]
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get statistics")


@router.get('/statistics/{news_id}')
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
