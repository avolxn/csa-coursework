from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    title: str = "Test Results API"
    secret_key: str = os.getenv("APP_SECRET_KEY", "test-results-dev-secret")
    auth_log_path: Path = BASE_DIR / "storage" / "auth.log"
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "APP_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
        ).split(",")
        if origin.strip()
    )


settings = Settings()
