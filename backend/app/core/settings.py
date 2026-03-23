from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = BACKEND_DIR / "data"
DEFAULT_DB_PATH = BACKEND_DIR / "events.db"
DEFAULT_ICS_PATH = BACKEND_DIR / "pokemon_madrid.ics"


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def _load_env_file(env_path: Path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    backend_dir: Path
    data_dir: Path
    db_path: Path
    raw_events_path: Path
    clean_events_path: Path
    calendar_path: Path
    cors_origins: list[str]
    host: str
    port: int
    frontend_url: str | None
    scraper_headless: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_env_file(BACKEND_DIR / ".env")

    data_dir = Path(os.getenv("DATA_DIR", DEFAULT_DATA_DIR))
    db_path = Path(os.getenv("DB_PATH", DEFAULT_DB_PATH))
    calendar_path = Path(os.getenv("CALENDAR_PATH", DEFAULT_ICS_PATH))
    frontend_url = os.getenv("FRONTEND_URL")
    cors_origins = _split_csv(os.getenv("CORS_ORIGINS"))

    if frontend_url and frontend_url not in cors_origins:
        cors_origins.append(frontend_url)

    if not cors_origins:
        cors_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    return Settings(
        backend_dir=BACKEND_DIR,
        data_dir=data_dir,
        db_path=db_path,
        raw_events_path=Path(os.getenv("RAW_EVENTS_PATH", data_dir / "events_raw.json")),
        clean_events_path=Path(os.getenv("CLEAN_EVENTS_PATH", data_dir / "events_clean.json")),
        calendar_path=calendar_path,
        cors_origins=cors_origins,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        frontend_url=frontend_url,
        scraper_headless=os.getenv("SCRAPER_HEADLESS", "false").lower() == "true",
    )
