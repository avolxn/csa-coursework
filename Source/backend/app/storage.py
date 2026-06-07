from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from .auth import hash_password


def default_data() -> dict[str, list[dict[str, Any]]]:
    return {
        "users": [
            {
                "id": 1,
                "name": "Администратор",
                "email": "admin@example.com",
                "password_hash": hash_password("password"),
                "age": 22,
                "role": "admin",
            },
            {
                "id": 2,
                "name": "Мария Орлова",
                "email": "maria.teacher@example.com",
                "password_hash": hash_password("password"),
                "age": 29,
                "role": "teacher",
            },
            {
                "id": 3,
                "name": "Анна Смирнова",
                "email": "anna@example.com",
                "password_hash": hash_password("password"),
                "age": 19,
                "role": "student",
            },
            {
                "id": 4,
                "name": "Игорь Петров",
                "email": "igor@example.com",
                "password_hash": hash_password("password"),
                "age": 20,
                "role": "student",
            },
        ],
        "tests": [
            {
                "id": 1,
                "title": "Основы HTML и CSS",
                "subject": "Веб-разработка",
                "description": "Базовые теги, селекторы и блочная модель.",
                "pass_percent": 60,
            },
            {
                "id": 2,
                "title": "JavaScript и LocalStorage",
                "subject": "Веб-разработка",
                "description": "Работа с объектами, массивами и хранением данных в браузере.",
                "pass_percent": 70,
            },
        ],
        "results": [
            {
                "id": 1,
                "user_id": 3,
                "test_id": 1,
                "score": 18,
                "max_score": 20,
                "comment": "Отличный результат",
            },
            {
                "id": 2,
                "user_id": 4,
                "test_id": 1,
                "score": 11,
                "max_score": 20,
                "comment": "Нужно повторить тему",
            },
            {
                "id": 3,
                "user_id": 3,
                "test_id": 2,
                "score": 16,
                "max_score": 20,
                "comment": "Хорошее понимание API браузера",
            },
        ],
    }


class MemoryStorage:
    def __init__(self):
        self.data = default_data()

    def list_users(self) -> list[dict[str, Any]]:
        return [self._public_user(user) for user in self.data["users"]]

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        user = self._find_by_id(self.data["users"], user_id)
        return deepcopy(user) if user else None

    def get_public_user(self, user_id: int) -> dict[str, Any] | None:
        user = self._find_by_id(self.data["users"], user_id)
        return self._public_user(user) if user else None

    def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        normalized = email.strip().lower()
        for user in self.data["users"]:
            if user["email"].lower() == normalized:
                return deepcopy(user)
        return None

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.find_user_by_email(payload["email"]) is not None:
            raise HTTPException(status_code=422, detail="Пользователь с таким email уже существует")

        user = {
            "id": self._next_id(self.data["users"]),
            "name": payload["name"].strip(),
            "email": payload["email"].strip().lower(),
            "password_hash": payload["password_hash"],
            "age": payload.get("age"),
            "role": payload["role"],
        }
        self.data["users"].append(user)
        return self._public_user(user)

    def list_tests(self) -> list[dict[str, Any]]:
        return deepcopy(self.data["tests"])

    def get_test(self, test_id: int) -> dict[str, Any] | None:
        test = self._find_by_id(self.data["tests"], test_id)
        return deepcopy(test) if test else None

    def create_test(self, payload: dict[str, Any]) -> dict[str, Any]:
        test = {
            "id": self._next_id(self.data["tests"]),
            "title": payload["title"].strip(),
            "subject": payload["subject"].strip(),
            "description": payload.get("description", "").strip(),
            "pass_percent": payload["pass_percent"],
        }
        self.data["tests"].append(test)
        return deepcopy(test)

    def update_test(self, test_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        test = self._find_by_id(self.data["tests"], test_id)
        if test is None:
            raise HTTPException(status_code=404, detail="Тест не найден")

        test["title"] = payload["title"].strip()
        test["subject"] = payload["subject"].strip()
        test["description"] = payload.get("description", "").strip()
        test["pass_percent"] = payload["pass_percent"]
        return deepcopy(test)

    def delete_test(self, test_id: int) -> None:
        test = self._find_by_id(self.data["tests"], test_id)
        if test is None:
            raise HTTPException(status_code=404, detail="Тест не найден")

        self.data["tests"] = [item for item in self.data["tests"] if int(item["id"]) != int(test_id)]
        self.data["results"] = [item for item in self.data["results"] if int(item["test_id"]) != int(test_id)]

    def list_results(self) -> list[dict[str, Any]]:
        return [self._enrich_result(result) for result in self.data["results"]]

    def get_result(self, result_id: int) -> dict[str, Any] | None:
        result = self._find_by_id(self.data["results"], result_id)
        return self._enrich_result(result) if result else None

    def create_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._validate_result_relations(payload["user_id"], payload["test_id"])
        self._validate_scores(payload["score"], payload["max_score"])

        result = {
            "id": self._next_id(self.data["results"]),
            "user_id": payload["user_id"],
            "test_id": payload["test_id"],
            "score": payload["score"],
            "max_score": payload["max_score"],
            "comment": payload.get("comment", "").strip(),
        }
        self.data["results"].append(result)
        return self._enrich_result(result)

    def update_result(self, result_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._find_by_id(self.data["results"], result_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Результат не найден")

        self._validate_result_relations(payload["user_id"], payload["test_id"])
        self._validate_scores(payload["score"], payload["max_score"])

        result["user_id"] = payload["user_id"]
        result["test_id"] = payload["test_id"]
        result["score"] = payload["score"]
        result["max_score"] = payload["max_score"]
        result["comment"] = payload.get("comment", "").strip()
        return self._enrich_result(result)

    def delete_result(self, result_id: int) -> None:
        result = self._find_by_id(self.data["results"], result_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Результат не найден")
        self.data["results"] = [item for item in self.data["results"] if int(item["id"]) != int(result_id)]

    def _validate_result_relations(self, user_id: int, test_id: int) -> None:
        user = self.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=422, detail="Пользователь не найден")
        if user["role"] != "student":
            raise HTTPException(status_code=422, detail="Результат можно создавать только для студента")

        if self.get_test(test_id) is None:
            raise HTTPException(status_code=422, detail="Тест не найден")

    def _validate_scores(self, score: int, max_score: int) -> None:
        if score < 0:
            raise HTTPException(status_code=422, detail="Балл не может быть отрицательным")
        if max_score <= 0:
            raise HTTPException(status_code=422, detail="Максимальный балл должен быть больше нуля")
        if score > max_score:
            raise HTTPException(status_code=422, detail="Балл не может быть больше максимума")

    def _enrich_result(self, result: dict[str, Any]) -> dict[str, Any]:
        test = self.get_test(int(result["test_id"]))
        user = self.get_user(int(result["user_id"]))
        if test is None or user is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Связанные данные не найдены")

        score = int(result["score"])
        max_score = int(result["max_score"])
        percent = round((score / max_score) * 100)
        grade = 2
        if percent >= 90:
            grade = 5
        elif percent >= 75:
            grade = 4
        elif percent >= 60:
            grade = 3

        return {
            "id": int(result["id"]),
            "user_id": int(result["user_id"]),
            "test_id": int(result["test_id"]),
            "score": score,
            "max_score": max_score,
            "percent": percent,
            "grade": grade,
            "passed": percent >= int(test["pass_percent"]),
            "comment": result.get("comment", "").strip(),
            "student_name": user["name"],
            "test_title": test["title"],
        }

    def _public_user(self, user: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": int(user["id"]),
            "name": user["name"],
            "email": user["email"],
            "age": user.get("age"),
            "role": user["role"],
        }

    def _find_by_id(self, items: list[dict[str, Any]], item_id: int) -> dict[str, Any] | None:
        for item in items:
            if int(item["id"]) == int(item_id):
                return item
        return None

    def _next_id(self, items: list[dict[str, Any]]) -> int:
        if not items:
            return 1
        return max(int(item["id"]) for item in items) + 1


def log_auth_event(path: Path, event: str, email: str, ip_address: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    line = f"{timestamp} {event} email={email} ip={ip_address}\n"
    with path.open("a", encoding="utf-8") as log_file:
        log_file.write(line)
