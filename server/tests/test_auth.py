import pytest

from conftest import async_client as ac


@pytest.mark.parametrize("email, password, code",
                         [
                             ("user@example.com", "string", 201),
                             ("user@example.com", "string", 400),
                             ("user@example.com", "c", 400),
                             ("user@example", "string", 422),
                             ("23432", "4234", 422),
                         ])
@pytest.mark.asyncio
async def test_register(email, password, code):
    response = await ac.post("/auth/register", json={
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert response.status_code == code


@pytest.mark.parametrize("email, password, code",
                         [
                             ("user@example.com", "strinwdg", 400),
                             ("user@example.com", "c", 400),
                             ("user@example", "string", 400),
                             ("23432", "4234", 400),
                             ("user@example.com", "string", 200 | 204),
                         ])
@pytest.mark.asyncio
async def test_login(email, password, code):
    data = {
        "username": email,
        "password": password,
    }
    encoded_data = "&".join([f"{key}={value}" for key, value in data.items()])
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = await ac.post("/auth/login", data=encoded_data, headers=headers)
    assert response.status_code == code


@pytest.mark.asyncio
async def test_logout():
    cookies_test_cases = [({k: ac.cookies.get(k) for k in ac.cookies}, 204),  # <-- parametrize doesn't work with this
                          ({k: "348" for k in ac.cookies}, 401),
                          ({}, 401)]
    for cookies, code in cookies_test_cases:
        headers = {
            "Content-Type": "application/json"
        }
        response = await ac.post("/auth/logout", headers=headers, cookies=cookies)
        assert response.status_code == code
