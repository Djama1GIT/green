from typing import Optional

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    id: int = Field(ge=0)
    title: str
    description: str
    content: Optional[str]
    views: int


class NewsItemForInsert(BaseModel):
    title: str
    description: str
    content: Optional[str]


class NewsItemForPut(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
