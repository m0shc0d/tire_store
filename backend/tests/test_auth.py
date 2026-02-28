# backend/tests/test_auth.py
import json

def test_login_access_token_success(client, test_user):
    """Тест успешного получения токена доступа."""
    login_data = {
        "username": test_user.email,
        "password": "testpassword"
    }

    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_access_token_wrong_password(client, test_user):
    """Тест входа с неправильным паролем."""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }

    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_access_token_inactive_user(client, session):
    """Тест входа неактивного пользователя."""
    from app.user.models import User
    from app.core.security import get_password_hash

    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=False,
        is_superuser=False,
        full_name="Inactive User",
    )
    session.add(inactive_user)
    session.commit()

    login_data = {
        "username": inactive_user.email,
        "password": "testpassword"
    }

    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"

def test_test_token_endpoint(authenticated_client, test_user):
    """Тест проверки токена."""
    response = authenticated_client.post("/api/v1/auth/login/test-token")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name

def test_password_recovery_success(client, test_user, mock_send_email_auth):
    response = client.post(f"/api/v1/auth/password-recovery/{test_user.email}")
    assert response.status_code == 200
    assert response.json()["message"] == "Password recovery email sent"
    assert mock_send_email_auth.called

def test_password_recovery_nonexistent_email(client):
    """Тест запроса восстановления для несуществующего email."""
    response = client.post("/api/v1/auth/password-recovery/nonexistent@example.com")
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]

def test_reset_password_success(client, test_user, mock_generate_token, mock_verify_token):
    """Тест успешного сброса пароля."""
    # Сначала запрашиваем восстановление
    client.post(f"/api/v1/auth/password-recovery/{test_user.email}")

    # Затем сбрасываем пароль
    reset_data = {
        "token": "mocked_token",
        "new_password": "newpassword123"
    }

    response = client.post("/api/v1/auth/reset-password/", json=reset_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

def test_reset_password_invalid_token(client):
    """Тест сброса пароля с невалидным токеном."""
    reset_data = {
        "token": "invalid_token",
        "new_password": "newpassword123"
    }

    response = client.post("/api/v1/auth/reset-password/", json=reset_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"

def test_password_recovery_html_content(superuser_client, test_user):
    """Тест получения HTML контента для восстановления пароля."""
    response = superuser_client.post(
        f"/api/v1/auth/password-recovery-html-content/{test_user.email}"
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
