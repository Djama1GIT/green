from typing import List
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    id: int = Field(ge=0)
    title: str
    description: str
    content: str
    views: int



