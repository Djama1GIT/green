import asyncio
import pytest
import pytest_asyncio

from conftest import client


@pytest.mark.asyncio
async def test_auth(ac):
    """

    :param ac:
    :return:
    """
    response = await ac.post("/auth/register", json={
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert response.status_code == 201
    data = {
        "username": "user@example.com",
        "password": "string",
    }
    encoded_data = "&".join([f"{key}={value}" for key, value in data.items()])
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = await ac.post("/auth/login", data=encoded_data, headers=headers)
    assert response.status_code == 204
    cookies = {k: ac.cookies.get(k) for k in ac.cookies}
    print(cookies)
    headers = {
        "Content-Type": "application/json"
    }
    response = await ac.post("/auth/logout", headers=headers, cookies=cookies)
    print(response)
    assert response.status_code == 204



