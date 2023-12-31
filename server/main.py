from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from pydantic import ValidationError

from auth.auth import auth_backend
# from auth.schemas import UserRead, UserCreate

from news.router import router as news_router
from admin.router import router as admin_router
from utils.router import router as utils_router

from redis import asyncio as aioredis
from config import settings
from utils.utils import fastapi_users


app = FastAPI(
    title=settings.NAME,
    version='0.33',
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
# app.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["auth"],
#     dependencies=[Depends(fastapi_users.current_user(active=True, superuser=True))]
# )


app.include_router(news_router)
app.include_router(admin_router,
                   dependencies=[Depends(fastapi_users.current_user(active=True, superuser=True))])
app.include_router(utils_router)


@app.exception_handler(ValidationError)
async def validation_exception_error(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors()})
    )


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
