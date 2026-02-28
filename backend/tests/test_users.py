# backend/tests/test_users.py
import uuid
import json

def test_read_users_as_superuser(superuser_client, test_user, session):
    """Тест получения списка пользователей суперпользователем."""
    # Создаем еще одного пользователя
    from app.user.models import User
    from app.core.security import get_password_hash

    user2 = User(
        email="user2@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
        is_superuser=False,
        full_name="User Two",
    )
    session.add(user2)
    session.commit()

    response = superuser_client.get("/api/v1/users/?skip=0&limit=100")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["count"] >= 2
    assert any(user["email"] == test_user.email for user in data["data"])

def test_read_users_as_regular_user(authenticated_client):
    """Тест попытки получения списка пользователей обычным пользователем."""
    response = authenticated_client.get("/api/v1/users/")
    assert response.status_code == 403  # Forbidden

def test_create_user_as_superuser(superuser_client):
    """Тест создания пользователя суперпользователем."""
    user_data = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "full_name": "New User",
        "is_active": True,
        "is_superuser": False
    }

    response = superuser_client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert data["is_active"] == user_data["is_active"]
    assert data["is_superuser"] == user_data["is_superuser"]

def test_create_user_duplicate_email(superuser_client, test_user):
    """Тест создания пользователя с существующим email."""
    user_data = {
        "email": test_user.email,  # Дублирующий email
        "password": "password",
        "full_name": "Duplicate User"
    }

    response = superuser_client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_update_user_me_success(authenticated_client, test_user, session):
    """Тест успешного обновления своего профиля."""
    update_data = {
        "full_name": "Updated Full Name",
        "email": "updated@example.com"
    }

    response = authenticated_client.patch("/api/v1/users/me", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

    # Проверяем обновление в БД
    session.refresh(test_user)
    assert test_user.full_name == update_data["full_name"]
    assert test_user.email == update_data["email"]

def test_update_user_me_duplicate_email(authenticated_client, test_user, session):
    """Тест обновления своего email на уже существующий."""
    # Создаем второго пользователя
    from app.user.models import User
    from app.core.security import get_password_hash

    user2 = User(
        email="existing@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
        is_superuser=False,
        full_name="Existing User",
    )
    session.add(user2)
    session.commit()

    # Пытаемся обновить email на существующий
    update_data = {"email": "existing@example.com"}
    response = authenticated_client.patch("/api/v1/users/me", json=update_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_update_password_me_success(authenticated_client, test_user):
    """Тест успешного обновления своего пароля."""
    password_data = {
        "current_password": "testpassword",
        "new_password": "NewStrongPass123!"
    }

    response = authenticated_client.patch("/api/v1/users/me/password", json=password_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Проверяем, что можно войти с новым паролем
    login_data = {
        "username": test_user.email,
        "password": "NewStrongPass123!"
    }
    login_response = authenticated_client.post(
        "/api/v1/auth/login/access-token",
        data=login_data
    )
    assert login_response.status_code == 200

def test_update_password_wrong_current(authenticated_client):
    """Тест обновления пароля с неправильным текущим паролем."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "NewStrongPass123!"
    }

    response = authenticated_client.patch("/api/v1/users/me/password", json=password_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"

def test_update_password_same_password(authenticated_client):
    """Тест обновления пароля на тот же самый."""
    password_data = {
        "current_password": "testpassword",
        "new_password": "testpassword"  # Тот же пароль
    }

    response = authenticated_client.patch("/api/v1/users/me/password", json=password_data)
    assert response.status_code == 400
    assert "cannot be the same" in response.json()["detail"]

def test_read_user_me(authenticated_client, test_user):
    """Тест получения информации о текущем пользователе."""
    response = authenticated_client.get("/api/v1/users/me")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "id" in data

def test_delete_user_me_success(authenticated_client, test_user, session):
    """Тест успешного удаления своего аккаунта."""
    response = authenticated_client.delete("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Проверяем, что пользователь удален из БД
    from app.user.crud import get_user_by_email
    db_user = get_user_by_email(session=session, email=test_user.email)
    assert db_user is None

def test_delete_user_me_superuser(superuser_client):
    """Тест попытки удаления своего аккаунта суперпользователем."""
    response = superuser_client.delete("/api/v1/users/me")
    assert response.status_code == 403
    assert "not allowed to delete themselves" in response.json()["detail"]

def test_register_user_success(client, session):
    """Тест успешной регистрации нового пользователя."""
    user_data = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "full_name": "New User"
    }

    response = client.post("/api/v1/users/signup", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]

    # Проверяем создание в БД
    from app.user.crud import get_user_by_email
    db_user = get_user_by_email(session=session, email=user_data["email"])
    assert db_user is not None
    assert db_user.email == user_data["email"]

def test_register_user_duplicate_email(client, test_user):
    """Тест регистрации с существующим email."""
    user_data = {
        "email": test_user.email,
        "password": "StrongPass123!",
        "full_name": "Duplicate User"
    }

    response = client.post("/api/v1/users/signup", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_read_user_by_id_as_self(authenticated_client, test_user):
    """Тест получения пользователя по ID (самим собой)."""
    response = authenticated_client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email

def test_read_user_by_id_as_superuser(superuser_client, test_user):
    """Тест получения пользователя по ID (суперпользователем)."""
    response = superuser_client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_user.id)

def test_read_user_by_id_as_other_user(authenticated_client, session):
    """Тест получения другого пользователя по ID (обычным пользователем)."""
    from app.user.models import User
    from app.core.security import get_password_hash

    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
        is_superuser=False,
        full_name="Other User",
    )
    session.add(other_user)
    session.commit()

    response = authenticated_client.get(f"/api/v1/users/{other_user.id}")
    assert response.status_code == 403  # Forbidden

def test_update_user_as_superuser(superuser_client, test_user, session):
    """Тест обновления пользователя суперпользователем."""
    update_data = {
        "full_name": "Updated by Admin",
        "email": "updated_by_admin@example.com"
    }

    response = superuser_client.patch(
        f"/api/v1/users/{test_user.id}",
        json=update_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

    # Проверяем обновление в БД
    session.refresh(test_user)
    assert test_user.full_name == update_data["full_name"]
    assert test_user.email == update_data["email"]

def test_delete_user_as_superuser(superuser_client, session):
    """Тест удаления пользователя суперпользователем."""
    from app.user.models import User
    from app.core.security import get_password_hash

    user_to_delete = User(
        email="todelete@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
        is_superuser=False,
        full_name="To Delete",
    )
    session.add(user_to_delete)
    session.commit()

    response = superuser_client.delete(f"/api/v1/users/{user_to_delete.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Проверяем удаление из БД
    db_user = session.get(User, user_to_delete.id)
    assert db_user is None
