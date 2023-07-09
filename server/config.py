from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    POSTGRES_DB: str = 'green'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = '93757'
    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: str = 5432
    QUESTIONS_URL: str = ''

    AUTH_MANAGER_SECRET: str = 'pLLefnee45weI7W78RUQI4QRW8wfriF95HIRW414UwqiuF34'


settings = Settings()

DATABASE_URL = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}' \
               f'@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
