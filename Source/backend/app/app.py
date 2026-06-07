from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .handlers import http_exception_handler, validation_exception_handler
from .routers.auth import router as auth_router
from .routers.results import router as results_router
from .routers.tests import router as tests_router
from .routers.users import router as users_router
from .storage import MemoryStorage

app = FastAPI(title=settings.title)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.state.storage = MemoryStorage()
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tests_router)
app.include_router(results_router)
