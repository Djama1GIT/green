from fastapi_users.authentication import CookieTransport, AuthenticationBackend
import redis.asyncio
from fastapi_users.authentication import RedisStrategy
from config import settings

cookie_transport = CookieTransport(cookie_max_age=3600)
redis = redis.asyncio.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)
