from typing import Optional

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    id: int = Field(ge=0)
    title: str = Field(min_length=10)
    description: str = Field(min_length=10)
    content: Optional[str]
    views: int
    time: str
    category: str


class NewsItemForInsert(BaseModel):
    id: Optional[int]
    title: str = Field(min_length=10)
    description: str = Field(min_length=10)
    content: Optional[str]
    category: str


class NewsItemForPut(BaseModel):
    id: int
    title: str = Field(min_length=10)
    description: str = Field(min_length=10)
    content: Optional[str]
    time: str
    category: str
