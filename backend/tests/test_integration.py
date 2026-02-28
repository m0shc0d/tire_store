# backend/tests/test_integration.py
def test_full_auth_flow(client, session):
    """Тест полного цикла аутентификации и работы с пользователем."""
    # 1. Регистрация нового пользователя
    register_data = {
        "email": "integration@example.com",
        "password": "IntegrationPass123!",
        "full_name": "Integration User"
    }

    register_response = client.post("/api/v1/users/signup", json=register_data)
    assert register_response.status_code == 200

    # 2. Вход в систему
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }

    login_response = client.post("/api/v1/auth/login/access-token", data=login_data)
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 3. Проверка токена
    client.headers.update({"Authorization": f"Bearer {token}"})
    test_token_response = client.post("/api/v1/auth/login/test-token")
    assert test_token_response.status_code == 200

    # 4. Обновление профиля
    update_data = {
        "full_name": "Updated Integration User",
        "email": "updated_integration@example.com"
    }

    update_response = client.patch("/api/v1/users/me", json=update_data)
    assert update_response.status_code == 200

    # 5. Обновление пароля
    password_data = {
        "current_password": register_data["password"],
        "new_password": "NewIntegrationPass456!"
    }

    password_response = client.patch("/api/v1/users/me/password", json=password_data)
    assert password_response.status_code == 200

    # 6. Проверка нового пароля
    new_login_data = {
        "username": update_data["email"],
        "password": password_data["new_password"]
    }

    new_login_response = client.post("/api/v1/auth/login/access-token", data=new_login_data)
    assert new_login_response.status_code == 200

    # 7. Удаление аккаунта
    delete_response = client.delete("/api/v1/users/me")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "User deleted successfully"
