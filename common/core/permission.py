# -*- coding: utf-8 -*-
"""Auth + RBAC permission dependencies."""

from __future__ import annotations

import re
import secrets

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.modules.rbac.models.role import RoleModel
from application.modules.system.models import UserModel
from application.db.backend import get_current_session
from common.core.task import CTX_USER_ID
from conf import settings

security = HTTPBasic()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_UI_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_UI_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Required",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class AuthControl:
    @classmethod
    async def is_authed(
        cls,
        token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ) -> UserModel:
        if settings.DISABLE_AUTH:
            session = get_current_session()
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.roles).selectinload(RoleModel.apis))
                .where(UserModel.is_superuser.is_(True))
                .limit(1)
            )
            user = result.scalar_one_or_none()
            if user:
                CTX_USER_ID.set(int(user.id))
                return user

        try:
            if not token:
                raise HTTPException(status_code=401, detail="Missing authentication token")
            token_str = (
                token.credentials
                if isinstance(token, HTTPAuthorizationCredentials)
                else str(token)
            )
            decode_data = jwt.decode(
                token_str,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id = decode_data.get("user_id")
            session = get_current_session()
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.roles).selectinload(RoleModel.apis))
                .where(UserModel.id == user_id, UserModel.is_deleted.is_(False))
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail="无效的Token") from e
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="登录已过期") from e
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="认证失败") from e


class PermissionControl:
    @classmethod
    async def has_permission(
        cls,
        request: Request,
        current_user: UserModel = Depends(AuthControl.is_authed),
    ) -> UserModel:
        if current_user.is_superuser or settings.DISABLE_AUTH:
            return current_user

        method = request.method
        path = request.url.path
        roles = current_user.roles or []
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")

        permission_apis: list[tuple[str, str]] = []
        for role in roles:
            for api in role.apis or []:
                permission_apis.append((api.method, api.path))

        for perm_method, perm_path in permission_apis:
            if method == perm_method:
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", perm_path)
                pattern = f"^{pattern}$"
                if re.match(pattern, path):
                    return current_user

        raise HTTPException(
            status_code=403,
            detail=f"Permission denied method:{method} path:{path}",
        )


DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
