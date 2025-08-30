import logging
import tomllib

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


type WriteMode = Literal["disabled", "enabled"]
type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

SRC_DIR = Path(__file__).parent
BASE_DIR = SRC_DIR.parent
PYPROJECT_TOML_PATH = BASE_DIR / "pyproject.toml"
PYPROJECT_TOML: dict[str, Any] = {}
if PYPROJECT_TOML_PATH.exists():
    PYPROJECT_TOML = tomllib.loads(PYPROJECT_TOML_PATH.read_text())

PROJECT_NAME = PYPROJECT_TOML.get("project", {}).get("name", "google-docs-mcp")


DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    # Drive read-only access ensures listing comments and export work on any file
    # the user can access (not just app-created files).
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSettings(BaseModel):
    client_id: str = Field(description="Google client ID")
    client_secret: str | None = Field(default=None, description="Google client secret")
    oauth_client_file: str | None = Field(default=None, description="OAuth client file")
    service_account_json: str | None = Field(default=None, description="Service account JSON")
    subject: str | None = Field(default=None, description="Subject (email address)")
    scopes: list[str] = Field(default_factory=lambda: list(DEFAULT_SCOPES), description="Google scopes")

    @field_validator("scopes", mode="before")
    @classmethod
    def _split_scopes(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return v  # type: ignore[return-value]
        return list(DEFAULT_SCOPES)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_nested_delimiter="__",
    )

    http_timeout_seconds: int = Field(default=30, description="HTTP timeout in seconds")
    write_mode: WriteMode = Field(
        default="enabled",
        description="Enable write tools like comments.reply, comments.resolve, docs.insert_text",
    )
    auto_auth: bool = Field(
        default=False,
        description="Automatically (re-)authorize on any tool call. This will open a browser to authorize.",
    )
    log_level: LogLevel = Field(default="INFO", description="Logging level")

    google: GoogleSettings = Field(default_factory=GoogleSettings)

    @property
    def is_write_mode(self) -> bool:
        return self.write_mode == "enabled"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Eagerly load settings from environment
    settings = Settings()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return settings
