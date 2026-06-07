from __future__ import annotations

from fastapi import HTTPException, status

from ..schemas import ResultPayload
from ..storage import MemoryStorage


class ResultService:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def list(self):
        return self.storage.list_results()

    def get(self, result_id: int, user: dict):
        result = self.storage.get_result(result_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Результат не найден")
        if user["role"] == "student" and int(result["user_id"]) != int(user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return result

    def create(self, payload: ResultPayload):
        return self.storage.create_result(payload.model_dump())

    def update(self, result_id: int, payload: ResultPayload):
        return self.storage.update_result(result_id, payload.model_dump())

    def delete(self, result_id: int):
        self.storage.delete_result(result_id)
        return {"deleted": True}
