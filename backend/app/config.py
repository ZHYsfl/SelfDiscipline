from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # App
    app_name: str = Field(default="HeartSync", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")
    version: str = Field(default="0.1.0", alias="VERSION")

    # Security / JWT
    secret_key: str = Field(default="CHANGE_ME_SUPER_SECRET", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Database
    database_url: str = Field(default="sqlite:///./data/app.db", alias="DATABASE_URL")

    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

    # Derived paths
    @property
    def app_dir(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def project_dir(self) -> Path:
        # backend directory
        return self.app_dir.parent

    @property
    def data_dir(self) -> Path:
        return self.project_dir / "data"

    @property
    def static_dir(self) -> Path:
        return self.app_dir / "static"


settings = Settings()
