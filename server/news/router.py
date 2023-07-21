from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache
from fastapi_users import FastAPIUsers

from .chemas import NewsItem, NewsItemForInsert, NewsItemForPut
from db import get_async_session
from auth.models import User
from auth.auth import auth_backend
from auth.manager import get_user_manager

from .repository import categories_repository, news_repository, news_details_repository, \
    follow_repository, unfollow_repository, update_news_repository, add_news_repository, delete_news_repository

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
    return await categories_repository(session)


@router.get("/follow", name="news_follow")
async def follow(email: str, session: AsyncSession = Depends(get_async_session)):
    return await follow_repository(email, session)


@router.get("/unfollow", name="news_unfollow")
async def unfollow(token: str, session: AsyncSession = Depends(get_async_session)):
    return await unfollow_repository(token, session)


@router.get('/{news_id}', response_model=NewsItem, name="news_by_id")
async def news_details(news_id: int, session: AsyncSession = Depends(get_async_session)):
    return await news_details_repository(news_id, session)


@router.get("/", response_model=List[NewsItem], name="news_list")
@cache(expire=60)
async def news(page: int = 1,
               size: int = 10,
               category: Optional[str] = None,
               session: AsyncSession = Depends(get_async_session)):
    return await news_repository(page, size, category, session)


@router.post("/add_news", name="add_news")
async def add_news(news_item: NewsItemForInsert,
                   session: AsyncSession = Depends(get_async_session),
                   user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("add_news" not in user.permissions or not user.permissions["add_news"]):
        raise HTTPException(status_code=403, detail=f"User does not have required permissions")
    return await add_news_repository(news_item, session)


@router.put("/edit_news", name="edit_news")
async def update_news(news_item: NewsItemForPut,
                      session: AsyncSession = Depends(get_async_session),
                      user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("edit_news" not in user.permissions or not user.permissions["edit_news"]):
        raise HTTPException(status_code=403, detail="User does not have required permissions")
    await update_news_repository(news_item, session)
    return {"status": 200}


@router.delete("/delete_news", name="delete_news")
async def delete_news(news_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      user=Depends(fastapi_users.current_user())):
    if not user.is_superuser and ("delete_news" not in user.permissions or not user.permissions["delete_news"]):
        raise HTTPException(status_code=403, detail="User does not have required permissions")
    await delete_news_repository(news_id, session)
    return {"status": 200}
