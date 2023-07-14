from typing import Tuple
from pydantic import BaseModel, Field


class Currency(BaseModel):
    dollar: Tuple[str, float, int]
    euro: Tuple[str, float, int]
    FYM: Tuple[str, float, int]


class Weather(BaseModel):
    city: str = Field(max_length=20)
    celsius: float
    weather: str = Field(max_length=20)
