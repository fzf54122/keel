# -*- coding: utf-8 -*-
"""Application settings (pydantic-settings)."""

from __future__ import annotations

import json
import os
import secrets

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    VERSION: str = "0.1.0"
    APP_TITLE: str = "Keel"
    PROJECT_NAME: str = "keel"
    APP_DESCRIPTION: str = "FastAPI scaffold with DRF-style ViewSets, SQLAlchemy and RBAC"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    TABLE_PREFIX: str = "keel_"

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: list[str] = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ]

    DEBUG: bool = True
    APP_ENV: str = "development"

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    LOGS_ROOT: str = os.path.join(PROJECT_ROOT, "logs")

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SQLAlchemy async URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    SWAGGER_UI_USERNAME: str = "admin"
    SWAGGER_UI_PASSWORD: str = "change-me-swagger"

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300

    BOOTSTRAP_ADMIN_USERNAME: str = "admin"
    BOOTSTRAP_ADMIN_PASSWORD: str = "AdminPass123"
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@example.com"

    DISABLE_AUTH: bool = False
    AUTO_CREATE_TABLES: bool = True  # convenient for sqlite/demo; prefer alembic in prod
    ENABLE_DEMO: bool = True
    # Redis 不可用时：false=降级（黑名单失效），true=关键路径失败
    REDIS_REQUIRED: bool = False

    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    CELERY_TASK_ALWAYS_EAGER: bool = False  # True in tests: run tasks inline

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.APP_ENV == "production":
            self._validate_production_config()
        elif self.APP_ENV not in {"testing"}:
            for msg in self.warn_insecure_defaults():
                # late import to avoid logger cycles at import time in some tools
                try:
                    from common.logger import logger
                    logger.warning(f"[keel] {msg}")
                except Exception:
                    print(f"[keel] WARNING: {msg}")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY length must be >= 32")
        return v

    @field_validator("SWAGGER_UI_PASSWORD")
    @classmethod
    def validate_swagger_password(cls, v: str) -> str:
        app_env = os.getenv("APP_ENV", "development")
        if app_env == "testing":
            return v or "test_password"
        if not v:
            raise ValueError("SWAGGER_UI_PASSWORD is required")
        if len(v) < 8:
            raise ValueError("SWAGGER_UI_PASSWORD length must be >= 8")
        return v

    def warn_insecure_defaults(self) -> list[str]:
        """开发期不安全默认项提示。"""
        warnings: list[str] = []
        if self.BOOTSTRAP_ADMIN_PASSWORD in {"AdminPass123", "admin", "password"}:
            warnings.append("BOOTSTRAP_ADMIN_PASSWORD is weak; change it before production")
        if self.SWAGGER_UI_PASSWORD in {"change-me-swagger", "admin", "password"}:
            warnings.append("SWAGGER_UI_PASSWORD is weak")
        if self.DISABLE_AUTH and self.APP_ENV != "testing":
            warnings.append("DISABLE_AUTH=true (auth bypass enabled)")
        if self.AUTO_CREATE_TABLES and self.APP_ENV == "production":
            warnings.append("AUTO_CREATE_TABLES should be false in production")
        return warnings

    def _validate_production_config(self) -> None:
        if self.DEBUG:
            raise ValueError("DEBUG must be false in production")
        if self.DATABASE_URL.startswith("sqlite"):
            raise ValueError("SQLite is not recommended in production")
        if "localhost" in self.CORS_ORIGINS:
            raise ValueError("CORS should not allow localhost in production")
        if self.DISABLE_AUTH:
            raise ValueError("DISABLE_AUTH must be false in production")


settings = Settings()
