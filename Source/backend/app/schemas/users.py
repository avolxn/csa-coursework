from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator

Role = Literal["admin", "teacher", "student"]


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    age: int | None = None
    role: Role = "student"

    @field_validator("name", "email", "password")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не должно быть пустым")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Некорректный email")
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")
        return value

    @field_validator("age")
    @classmethod
    def validate_age(cls, value: int | None) -> int | None:
        if value is not None and not 6 <= value <= 100:
            raise ValueError("Возраст должен быть в диапазоне от 6 до 100")
        return value
