from fastapi import APIRouter
from .chemas import Currency, Weather

router = APIRouter(
    tags=['Utils']
)


@router.get('/currency_rates', response_model=Currency)
async def currency():
    return Currency(
        dollar=('$', 80.0),
        euro=('€', 99.85),
        FYM=('¥', 12.0)
    )


@router.get('/weather', response_model=Weather)
async def weather():
    return Weather(
        city='Moscow',
        celsius=24.5,
        weather='Clear',
    )
