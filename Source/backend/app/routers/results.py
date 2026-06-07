from __future__ import annotations

from fastapi import APIRouter, status

from ..dependencies import EditorDep, StorageDep, UserDep, build_data
from ..schemas import ResultPayload
from ..services import ResultService

router = APIRouter(prefix="/results", tags=["results"])


@router.get("")
def list_results(_: UserDep, storage: StorageDep):
    return build_data(ResultService(storage).list())


@router.get("/{result_id}")
def show_result(result_id: int, user: UserDep, storage: StorageDep):
    return build_data(ResultService(storage).get(result_id, user))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_result(payload: ResultPayload, _: EditorDep, storage: StorageDep):
    return build_data(ResultService(storage).create(payload))


@router.put("/{result_id}")
def update_result(result_id: int, payload: ResultPayload, _: EditorDep, storage: StorageDep):
    return build_data(ResultService(storage).update(result_id, payload))


@router.delete("/{result_id}")
def delete_result(result_id: int, _: EditorDep, storage: StorageDep):
    return build_data(ResultService(storage).delete(result_id))
