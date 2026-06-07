from __future__ import annotations

from fastapi import HTTPException, status

from ..schemas import TestPayload
from ..storage import MemoryStorage


class TestService:
    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def list(self):
        return self.storage.list_tests()

    def get(self, test_id: int):
        test = self.storage.get_test(test_id)
        if test is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
        return test

    def create(self, payload: TestPayload):
        return self.storage.create_test(payload.model_dump())

    def update(self, test_id: int, payload: TestPayload):
        return self.storage.update_test(test_id, payload.model_dump())

    def delete(self, test_id: int):
        self.storage.delete_test(test_id)
        return {"deleted": True}
