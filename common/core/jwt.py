# -*- coding: utf-8 -*-
"""JWT helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel, Field

from conf import settings


class JWTPayload(BaseModel):
    user_id: int
    username: str
    is_superuser: bool
    exp: datetime
    token_type: str = "access"


def create_access_token(*, data: JWTPayload) -> str:
    payload = data.model_dump().copy()
    payload["token_type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str, is_superuser: bool) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = JWTPayload(
        user_id=user_id,
        username=username,
        is_superuser=is_superuser,
        exp=expire,
        token_type="refresh",
    )
    data = payload.model_dump()
    data["token_type"] = "refresh"
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> JWTPayload:
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("token_type") != token_type:
            raise jwt.InvalidTokenError(f"Invalid token type. Expected {token_type}")
        return JWTPayload(**payload)
    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError("Invalid token") from e


def create_token_pair(user_id: int, username: str, is_superuser: bool) -> tuple[str, str]:
    access_expire = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_payload = JWTPayload(
        user_id=user_id,
        username=username,
        is_superuser=is_superuser,
        exp=access_expire,
        token_type="access",
    )
    access_token = create_access_token(data=access_payload)
    refresh_token = create_refresh_token(user_id, username, is_superuser)
    return access_token, refresh_token
