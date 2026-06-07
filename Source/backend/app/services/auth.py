from __future__ import annotations

from fastapi import HTTPException, Request, status

from ..auth import verify_password
from ..config import settings
from ..schemas import LoginPayload
from ..storage import MemoryStorage, log_auth_event


class AuthService:
    def __init__(self, storage: MemoryStorage | None):
        self.storage = storage

    def me(self, user: dict | None):
        return user

    def login(self, payload: LoginPayload, request: Request):
        user = self.storage.find_user_by_email(payload.email)
        ip_address = request.client.host if request.client else "unknown"

        if user is None or not verify_password(payload.password, user["password_hash"]):
            log_auth_event(settings.auth_log_path, "FAIL_LOGIN", payload.email.strip().lower(), ip_address)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

        request.session["user_id"] = int(user["id"])
        log_auth_event(settings.auth_log_path, "SUCCESS_LOGIN", user["email"], ip_address)
        return self.storage.get_public_user(int(user["id"]))

    def logout(self, request: Request):
        user_id = request.session.get("user_id")
        if user_id:
            user = self.storage.get_public_user(int(user_id))
            ip_address = request.client.host if request.client else "unknown"
            if user:
                log_auth_event(settings.auth_log_path, "LOGOUT", user["email"], ip_address)
        request.session.clear()
        return {"message": "Сессия завершена"}
