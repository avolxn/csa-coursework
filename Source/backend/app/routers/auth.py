from __future__ import annotations

from fastapi import APIRouter, Request

from ..dependencies import CurrentUserDep, StorageDep, build_data
from ..schemas import LoginPayload
from ..services import AuthService

router = APIRouter()


@router.get("/me")
def me(user: CurrentUserDep):
    return build_data(AuthService(None).me(user))


@router.post("/login")
def login(payload: LoginPayload, request: Request, storage: StorageDep):
    return build_data(AuthService(storage).login(payload, request))


@router.post("/logout")
def logout(request: Request, storage: StorageDep):
    return build_data(AuthService(storage).logout(request))
