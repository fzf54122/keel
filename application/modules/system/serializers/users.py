# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from common.core.schemas import KeelSchemas
from pydantic import EmailStr, Field, field_validator, model_validator


class UsersSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    email: EmailStr | None = None
    username: str | None = None
    alias: str | None = None
    phone: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_deleted: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login: datetime | None = None
    roles: list[int] | None = None

    @field_validator("roles", mode="before")
    @classmethod
    def normalize_roles(cls, v):
        if v is None:
            return None
        result = []
        for item in v:
            if isinstance(item, int):
                result.append(item)
            else:
                result.append(getattr(item, "id"))
        return result


class UsersCreateSerializers(KeelSchemas):
    email: str = Field(..., json_schema_extra={"example": "admin@example.com"})
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名（3-20位字母数字下划线）",
    )
    password: str = Field(..., min_length=8, description="密码（至少8位，包含字母和数字）")
    alias: str | None = None
    phone: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    role_ids: list[int] | None = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码长度至少8位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v


class UsersUpdateSerializers(KeelSchemas):
    email: EmailStr | None = None
    alias: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    role_ids: list[int] | None = None


class UsersUpdatePasswordSerializers(KeelSchemas):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(min_length=8, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("新密码长度至少8位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("新密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("新密码必须包含数字")
        return v
