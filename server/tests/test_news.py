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


@pytest.mark.parametrize("news_id, title, description, content, code", [
    (1001, "stringweqwfqwef", "stringwfwefwef", "string", 200),
    (1002, "striwefqwfwqfng", "strwefwfeqwfing", "", 200),
    (1003, "striwqefqwfqwefng", "", "string", 422),
    (1004, "string", "", "string", 422),
    (1005, "", "striwqfqwfwfng", "string", 422),
])
@pytest.mark.asyncio
async def test_add(ac, news_id, title, description, content, code):
    response = await login(ac)
    assert response.status_code == 204
    cookies = {k: ac.cookies.get(k) for k in ac.cookies}
    response = await ac.post("/news/add_news", json={
        "id": news_id,
        "title": title,
        "description": description,
        "content": content
    }, cookies=cookies)
    print(response.text)
    assert response.status_code == code


@pytest.mark.parametrize("news_id, title, description, content, code", [
    (1001, "stringwwefeqwwffqwef", "stringwfwefweweffwef", "string", 200),
    (30, "stringweqwfwefqwef", "stringwfwqefwefwef", "string", 404),
    (1001, "stringweqwfqwef", "stringw", "string", 422),
    (1001, "stringweqwfqwef", 2342, "string", 422),
    (1001, "2", "stringwfwefwefwef", "", 422),
    (1001, None, "stringw", "string", 422),
    (1001, 234234, "wefwefwfeewf", "string", 422),
])
@pytest.mark.asyncio
async def test_edit(ac, news_id, title, description, content, code):
    response = await login(ac)
    assert response.status_code == 204
    await ac.post("/news/add_news", json={
        "id": 1001,
        "title": "stringwwefeqwfqwef",
        "description": "stringwfwefwefwef",
        "content": "string"
    })
    cookies = {k: ac.cookies.get(k) for k in ac.cookies}
    response = await ac.put("/news/edit_news", json={
        "id": news_id,
        "title": title,
        "description": description,
        "content": content
    }, cookies=cookies)
    print(response.text)
    assert response.status_code == code


@pytest.mark.parametrize("news_id, code", [
    (1002, 200),
    (1003, 200),
    (1004, 200),
    (2006, 200),
    (100, 200),
    (None, 422),
    ("wefg", 422),
])
@pytest.mark.asyncio
async def test_delete(ac, news_id, code):
    response = await login(ac)
    assert response.status_code == 204
    cookies = {k: ac.cookies.get(k) for k in ac.cookies}
    response = await ac.delete("/news/delete_news", params=f"news_id={news_id}", cookies=cookies)
    print(response.text)
    assert response.status_code == code
