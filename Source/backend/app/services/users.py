from __future__ import annotations

from fastapi import HTTPException, status

from ..auth import hash_password
from ..schemas import UserCreate
from ..storage import MemoryStorage


class UserService:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def list(self):
        return self.storage.list_users()

    def get(self, user_id: int):
        user = self.storage.get_public_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return user

    def create(self, payload: UserCreate):
        data = payload.model_dump(exclude={"password"})
        data["password_hash"] = hash_password(payload.password)
        return self.storage.create_user(data)
