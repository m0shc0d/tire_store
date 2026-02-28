import pytest
import os
import sys

# Устанавливаем ВСЕ обязательные переменные окружения
# ENVIRONMENT должен быть одним из: local, staging, production
os.environ.update({
    "ENVIRONMENT": "local",  # Изменено с 'test' на 'local'
    "DOMAIN": "localhost:8000",
    "PROJECT_NAME": "tire_store",
    "POSTGRES_SERVER": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
    "FIRST_SUPERUSER": "admin@test.com",
    "FIRST_SUPERUSER_PASSWORD": "admin123",
    "SECRET_KEY": "test_secret_key_change_in_production",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "FRONTEND_HOST": "http://localhost:5173",
    "BACKEND_CORS_ORIGINS": '["http://localhost:5173"]',
    "SMTP_HOST": "smtp.test.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "test@test.com",
    "SMTP_PASSWORD": "test_password",
    "EMAILS_FROM_EMAIL": "noreply@test.com",
    "EMAILS_FROM_NAME": "Tire Store Test",
    "EMAIL_TEST_USER": "test@example.com",
    "SENTRY_DSN": "",
})

# Теперь импортируем приложение
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from app.main import app
from app.user.models import User
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from datetime import timedelta

# Создаем движок для тестовой базы данных
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    # Мокаем зависимость для получения сессии
    from app.api.deps import get_db

    def get_db_override():
        yield session

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()

# Фикстуры для тестового пользователя
@pytest.fixture
def test_user(session):
    """Создает тестового пользователя."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def token(test_user):
    """Генерирует токен для тестового пользователя."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(str(test_user.id), expires_delta=access_token_expires)

@pytest.fixture
def authenticated_client(client, token):
    """Клиент с токеном авторизации."""
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

# Фикстуры для суперпользователя
@pytest.fixture
def superuser(session):
    """Создает тестового суперпользователя."""
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_superuser=True,
        full_name="Super Admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def superuser_token(superuser):
    """Генерирует токен для суперпользователя."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(str(superuser.id), expires_delta=access_token_expires)

@pytest.fixture
def superuser_client(client, superuser_token):
    """Клиент с токеном суперпользователя."""
    client.headers.update({"Authorization": f"Bearer {superuser_token}"})
    return client

@pytest.fixture
def mock_send_email_auth(mocker):
    """Мок для send_email в auth router (для test_auth.py)"""
    return mocker.patch('app.auth.router.send_email')

@pytest.fixture
def mock_send_email_utils(mocker):
    """Мок для send_email в utils router (для test_utils.py)"""
    return mocker.patch('app.api.utils.send_email')

@pytest.fixture
def mock_generate_token(mocker):
    """Мок для генерации токена в auth router"""
    mock = mocker.patch('app.auth.router.generate_password_reset_token')
    mock.return_value = "mocked_token_123"
    return mock

@pytest.fixture
def mock_verify_token(mocker):
    """Мок для проверки токена в auth router"""
    mock = mocker.patch('app.auth.router.verify_password_reset_token')
    mock.return_value = "test@example.com"
    return mock

@pytest.fixture
def mock_generate_token(mocker):
    """Мок для генерации токена сброса пароля в auth router"""
    mock = mocker.patch('app.auth.router.generate_password_reset_token')
    mock.return_value = "mocked_token_123"
    return mock

@pytest.fixture
def mock_verify_token(mocker):
    """Мок для проверки токена сброса пароля в auth router"""
    mock = mocker.patch('app.auth.router.verify_password_reset_token')
    mock.return_value = "test@example.com"
    return mock