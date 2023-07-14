import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from fastapi_users import FastAPIUsers

from auth.auth import auth_backend
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserRead, UserCreate

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import sys
import os

server_path = os.path.join(os.getcwd(), "")
sys.path.insert(0, server_path)
from main import app
from db import get_async_session, metadata
from tests.config import settings

URL_TEST_DATABASE = f"postgresql+asyncpg://{settings.POSTGRES_USER_TEST}:{settings.POSTGRES_PASSWORD_TEST}@" \
                    f"{settings.POSTGRES_HOST_TEST}:{settings.POSTGRES_PORT_TEST}/{settings.POSTGRES_DB_TEST}"

engine_test = create_async_engine(URL_TEST_DATABASE, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session

redis = aioredis.from_url("redis://localhost:6379/2")
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@pytest_asyncio.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)
async_client = AsyncClient(app=app, base_url='http://test')


@pytest_asyncio.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
