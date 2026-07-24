# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any

from common.core.schemas import KeelSchemas
from pydantic import Field


class CredentialsSerializers(KeelSchemas):
    username: str = Field(..., description="用户名", json_schema_extra={"example": "admin"})
    password: str = Field(..., description="密码", json_schema_extra={"example": "AdminPass123"})


class JWTOut(KeelSchemas):
    access_token: str
    refresh_token: str
    username: str
    token_type: str = "Bearer"
    expires_in: int
    user_uuid: Any = None


class RefreshTokenRequest(KeelSchemas):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenRefreshOut(KeelSchemas):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
