# backend/tests/test_models.py
import uuid

from app.auth.models import Token
from app.models import Message
from app.user.models import (
    User,
    UserCreate,
    UserRegister,
)


def test_user_model_creation():
    """Тест создания модели пользователя."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        full_name="Test User"
    )

    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.full_name == "Test User"
    assert isinstance(user.id, uuid.UUID)

def test_user_create_schema():
    """Тест схемы создания пользователя."""
    user_data = UserCreate(
        email="new@example.com",
        password="StrongPass123!",
        full_name="New User",
        is_active=True,
        is_superuser=False
    )

    assert user_data.email == "new@example.com"
    assert user_data.password == "StrongPass123!"
    assert user_data.full_name == "New User"
    assert user_data.is_active is True
    assert user_data.is_superuser is False

def test_user_register_schema():
    """Тест схемы регистрации пользователя."""
    register_data = UserRegister(
        email="register@example.com",
        password="RegisterPass123!",
        full_name="Register User"
    )

    assert register_data.email == "register@example.com"
    assert register_data.password == "RegisterPass123!"
    assert register_data.full_name == "Register User"

def test_token_model():
    """Тест модели токена."""
    token = Token(
        access_token="test_token_123",
        token_type="bearer"
    )

    assert token.access_token == "test_token_123"
    assert token.token_type == "bearer"

def test_message_model():
    """Тест модели сообщения."""
    message = Message(message="Test message")
    assert message.message == "Test message"
