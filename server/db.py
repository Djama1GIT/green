from sqlalchemy.ext.asyncio import create_async_engine
from config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

engine = create_async_engine(DATABASE_URL)

Base = declarative_base()
metadata = Base.metadata
