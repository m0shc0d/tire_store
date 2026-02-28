# backend/tests/test_utils.py
def test_health_check(client):
    """Тест проверки работоспособности API."""
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    assert response.json() is True

def test_test_email_as_superuser(superuser_client, mock_send_email_utils):
    """Тест отправки тестового email суперпользователем."""
    email_to = "test@example.com"
    response = superuser_client.post(f"/api/v1/utils/test-email/?email_to={email_to}")
    # Проверьте реальный статус код в вашем роутере
    # Если роутер возвращает 201, то и в тесте должен быть 201
    assert response.status_code == 201  # ИЛИ 201, если так задано в роутере
    assert response.json()["message"] == "Test email sent"
    assert mock_send_email_utils.called

def test_test_email_as_regular_user(authenticated_client):
    """Тест отправки тестового email обычным пользователем."""
    response = authenticated_client.post("/api/v1/utils/test-email/?email_to=test@example.com")
    assert response.status_code == 403  # Forbidden
