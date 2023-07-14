import pytest
from conftest import client


# @pytest.mark.timeout(5)
# def test_currency_rates():
#     with client.websocket_connect("/currency_rates") as websocket:
#         message = websocket.receive_json()
#         assert "dollar" in message
#         assert "euro" in message
#         assert "FYM" in message
#         websocket.close()


@pytest.mark.asyncio
async def test_weather(ac):
    response = await ac.get("/weather")
    assert response.status_code == 200
