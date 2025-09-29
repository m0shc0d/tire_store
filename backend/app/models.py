from sqlmodel import SQLModel
from app.user.models import (
        UserBase,
        UserCreate,
        UserRegister,
        UserUpdate,
        UserUpdateMe,
        UpdatePassword,
        User,
        UserPublic,
        UsersPublic
        )
from app.auth.models import (
        Token,
        TokenPayload,
        NewPassword
        )


# Generic message
class Message(SQLModel):
    message: str
