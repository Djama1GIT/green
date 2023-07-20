import asyncio
import random
from copy import copy

from fastapi import APIRouter, WebSocket

from .chemas import Currency, Weather

router = APIRouter(
    tags=['Utils']
)


@router.websocket('/currency_rates', name="currency")
async def currency(websocket: WebSocket):
    """
    Hypothetically, there may be a request to an external API here
    :return
    """
    try:
        await websocket.accept()
        prev = Currency(
                dollar=('$', 80.0 + random.random(), 0),
                euro=('€', 99.85 + random.random(), 0),
                FYM=('¥', 12.0 + random.random(), 0)
            )
        while True:
            now = Currency(
                dollar=('$', (d := (80.0 + random.random())), (1 if d > prev.dollar[1] else (0 if d == prev.dollar[1] else -1))),
                euro=('€', (e := (99.0 + random.random())), 1 if e > prev.euro[1] else (0 if e == prev.euro[1] else -1)),
                FYM=('¥', (f := (12.0 + random.random())), 1 if f > prev.FYM[1] else (0 if f == prev.FYM[1] else -1)),
            )
            await websocket.send_json(now.dict())
            await asyncio.sleep(2)
            prev = copy(now)
    except:
        pass


@router.get('/weather', response_model=Weather, name="weather")
async def weather():
    """
    Hypothetically, there may be a request to an external API here
    :return:
    """
    return Weather(
        city='Moscow',
        celsius=24.5,
        weather='Clear',
    )
