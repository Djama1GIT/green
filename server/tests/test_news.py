import pytest


async def login(ac):
    data = {
        "username": "user@example.com",
        "password": "string",
    }
    encoded_data = "&".join([f"{key}={value}" for key, value in data.items()])
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    return await ac.post("/auth/login", data=encoded_data, headers=headers)


@pytest.mark.asyncio
async def test_add(ac):
    response = await login(ac)
    assert response.status_code == 204
    cookies = {k: ac.cookies.get(k) for k in ac.cookies}
    response = await ac.post("/news/add_news", json={
        "title": "string",
        "description": "string",
        "content": "string"
    }, cookies=cookies)
    assert response.status_code == 200
