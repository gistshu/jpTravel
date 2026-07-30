import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str
    app_env: str
    debug: bool
    database_url: str
    secret_key: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str


def _read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.lower() in {"1", "true", "yes", "on"}


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(
            key.strip(),
            value.strip().strip('"').strip("'"),
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    _load_dotenv()
    return Settings(
        app_name=os.getenv("APP_NAME", "JP Travel"),
        app_env=os.getenv("APP_ENV", "local"),
        debug=_read_bool_env("DEBUG", False),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./jp_travel.sqlite3"),
        secret_key=os.getenv("SECRET_KEY", "change-me"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        google_redirect_uri=os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/v1/auth/google/callback",
        ),
    )


settings = get_settings()
