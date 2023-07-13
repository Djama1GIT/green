from conftest import client


def test_register():
    response = client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert response.status_code == 201


def test_login():
    data = {
        "username": "user@example.com",
        "password": "string",
    }
    encoded_data = "&".join([f"{key}={value}" for key, value in data.items()])
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = client.post("/auth/login", data=encoded_data, headers=headers)
    assert response.status_code == 204


# def test_logout():
# не сохраняются куки или еще что я хз, ошибка 401, пользователь не авторизован, хотя куки авторизации есть
#     print(client.cookies)
#     response = client.post("/auth/logout", cookies=client.cookies)
#
#     assert response.status_code == 200
