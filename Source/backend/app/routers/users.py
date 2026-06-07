from __future__ import annotations

from fastapi import APIRouter, status

from ..dependencies import AdminDep, StorageDep, UserDep, build_data
from ..schemas import UserCreate
from ..services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(_: UserDep, storage: StorageDep):
    return build_data(UserService(storage).list())


@router.get("/{user_id}")
def show_user(user_id: int, _: UserDep, storage: StorageDep):
    return build_data(UserService(storage).get(user_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, _: AdminDep, storage: StorageDep):
    return build_data(UserService(storage).create(payload))
