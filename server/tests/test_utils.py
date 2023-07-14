import pytest


@pytest.mark.asyncio
async def test_currency(ac):
    response = await ac.get("/currency_rates")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_weather(ac):
    response = await ac.get("/weather")
    assert response.status_code == 200
