from typing import List
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from .chemas import NewsItem, NewsItemForInsert, NewsItemForPut
from db import get_async_session

from .repository import NewsRepository
from .dependencies import check_permissions, get_news_repository
from utils.dependencies import Paginator

router = APIRouter(
    prefix='/news',
    tags=['News']
)


@router.get("/categories", name="news_categories")
async def categories(news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.categories()


@router.get("/follow", name="news_follow")
async def follow(email: str,
                 news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.follow(email)


@router.get("/unfollow", name="news_unfollow")
async def unfollow(token: str,
                   news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.unfollow(token)


@router.get('/{news_id}', response_model=NewsItem, name="news_by_id")
async def news_details(news_id: int,
                       news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.news_details(news_id)


@router.get("/", response_model=List[NewsItem], name="news_list")
@cache(expire=60)
async def news(paginator: Paginator = Depends(),
               news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.news(**paginator.dict())


@router.post("/add_news", name="add_news", dependencies=[Depends(check_permissions("add_news"))])
async def add_news(news_item: NewsItemForInsert,
                   news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    return await news_repo.add_news(news_item)


@router.put("/edit_news", name="edit_news", dependencies=[Depends(check_permissions("edit_news"))])
async def update_news(news_item: NewsItemForPut,
                      news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    await news_repo.update_news(news_item)
    return {"status": 200}


@router.delete("/delete_news", name="delete_news", dependencies=[Depends(check_permissions("delete_news"))])
async def delete_news(news_id: int,
                      news_repo: NewsRepository = Depends(get_news_repository(get_async_session))):
    await news_repo.delete_news(news_id)
    return {"status": 200}
