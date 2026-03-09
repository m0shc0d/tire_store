# ruff: noqa: F401
from sqlmodel import SQLModel

from app.auth.models import NewPassword, Token, TokenPayload
from app.user.models import (
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)


# Generic message
class Message(SQLModel):
    message: str
