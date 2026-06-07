from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from .storage import MemoryStorage


def build_data(payload):
    return {"data": payload}


def get_storage(request: Request) -> MemoryStorage:
    return request.app.state.storage


StorageDep = Annotated[MemoryStorage, Depends(get_storage)]


def get_current_user(request: Request, storage: StorageDep) -> dict | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = storage.get_public_user(int(user_id))
    if user is None:
        request.session.clear()
    return user


CurrentUserDep = Annotated[dict | None, Depends(get_current_user)]


def require_user(user: CurrentUserDep) -> dict:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходима авторизация")
    return user


UserDep = Annotated[dict, Depends(require_user)]


def require_editor(user: UserDep) -> dict:
    if user["role"] not in {"admin", "teacher"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    return user


EditorDep = Annotated[dict, Depends(require_editor)]


def require_admin(user: UserDep) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    return user


AdminDep = Annotated[dict, Depends(require_admin)]
