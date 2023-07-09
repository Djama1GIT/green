from typing import Tuple
from pydantic import BaseModel, Field


class Currency(BaseModel):
    dollar: Tuple[str, float]
    euro: Tuple[str, float]
    FYM: Tuple[str, float]


class Weather(BaseModel):
    city: str = Field(max_length=20)
    celsius: float
    weather: str = Field(max_length=20)
