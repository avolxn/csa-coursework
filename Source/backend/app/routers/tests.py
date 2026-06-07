from __future__ import annotations

from fastapi import APIRouter, status

from ..dependencies import EditorDep, StorageDep, UserDep, build_data
from ..schemas import TestPayload
from ..services import TestService

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("")
def list_tests(_: UserDep, storage: StorageDep):
    return build_data(TestService(storage).list())


@router.get("/{test_id}")
def show_test(test_id: int, _: UserDep, storage: StorageDep):
    return build_data(TestService(storage).get(test_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_test(payload: TestPayload, _: EditorDep, storage: StorageDep):
    return build_data(TestService(storage).create(payload))


@router.put("/{test_id}")
def update_test(test_id: int, payload: TestPayload, _: EditorDep, storage: StorageDep):
    return build_data(TestService(storage).update(test_id, payload))


@router.delete("/{test_id}")
def delete_test(test_id: int, _: EditorDep, storage: StorageDep):
    return build_data(TestService(storage).delete(test_id))
