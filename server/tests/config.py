from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    POSTGRES_DB_TEST: str = os.getenv("POSTGRES_DB_TEST")
    POSTGRES_USER_TEST: str = os.getenv("POSTGRES_USER_TEST")
    POSTGRES_PASSWORD_TEST: str = os.getenv("POSTGRES_PASSWORD_TEST")
    POSTGRES_HOST_TEST: str = os.getenv("POSTGRES_HOST_TEST")
    POSTGRES_PORT_TEST: int = os.getenv("POSTGRES_PORT_TEST")


settings = Settings()
