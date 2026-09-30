from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль минимум 8 символов")
        if not re.search(r"[A-ZА-Я]", v):
            raise ValueError("Нужна хотя бы одна заглавная буква")
        if not re.search(r"[a-zа-я]", v):
            raise ValueError("Нужна хотя бы одна строчная буква")
        if not re.search(r"\d", v):
            raise ValueError("Нужна хотя бы одна цифра")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str