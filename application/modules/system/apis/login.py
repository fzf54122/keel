# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fast_generic_api.decorator import api_meta
from sqlalchemy import select

from application.modules.system.models import UserModel
from application.modules.system.serializers import (
    CredentialsSerializers,
    JWTOut,
    RefreshTokenRequest,
    TokenRefreshOut,
    UsersSerializers,
)
from application.modules.system.services import UserService
from application.db.backend import get_current_session
from common.core.cache import cache_manager
from common.core.jwt import create_token_pair, verify_token
from common.core.limit import apply_rate_limit
from common.core.response import KeelResponse
from conf import settings

router = APIRouter(tags=["登录接口"])
service = UserService()
security = HTTPBearer(auto_error=False)


class LoginViewSet:
    @staticmethod
    @api_meta(summary="用户登录")
    @router.post("/auth/login/", summary="用户登录")
    async def login(request: Request, credentials: CredentialsSerializers):
        user = await service.authenticate(credentials)
        await service.update_last_login(user.id)
        access_token, refresh_token = create_token_pair(
            user_id=user.id,
            username=user.username,
            is_superuser=user.is_superuser,
        )
        await cache_manager.set(
            f"refresh_token:{user.id}",
            refresh_token,
            ttl=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )
        return KeelResponse(
            data=JWTOut(
                access_token=access_token,
                refresh_token=refresh_token,
                username=user.username,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_uuid=user.uuid,
            ),
            msg="登录成功",
        )

    @staticmethod
    @router.post("/auth/logout/", summary="用户退出")
    async def logout(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ):
        if not credentials:
            return KeelResponse(msg="退出登录成功")
        token = credentials.credentials
        try:
            payload = verify_token(token, token_type="access")
            await cache_manager.set(f"blacklist_token:{token}", "logged_out", ttl=86400)
            await cache_manager.delete(f"refresh_token:{payload.user_id}")
        except Exception:
            pass
        return KeelResponse(msg="退出登录成功")

    @staticmethod
    @apply_rate_limit(rate="5/minute")
    @router.post("/auth/refresh/", summary="刷新Token")
    async def refresh_token(request: Request, body: RefreshTokenRequest):
        payload = verify_token(body.refresh_token, token_type="refresh")
        stored = await cache_manager.get(f"refresh_token:{payload.user_id}")
        if stored and stored != body.refresh_token:
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Invalid refresh token")

        session = get_current_session()
        result = await session.execute(
            select(UserModel).where(
                UserModel.id == payload.user_id, UserModel.is_deleted.is_(False)
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="User not found")

        access_token, refresh_token = create_token_pair(
            user_id=user.id,
            username=user.username,
            is_superuser=user.is_superuser,
        )
        await cache_manager.set(
            f"refresh_token:{user.id}",
            refresh_token,
            ttl=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )
        return KeelResponse(
            data=TokenRefreshOut(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            msg="刷新成功",
        )

    @staticmethod
    @router.get("/auth/me/", summary="获取当前用户信息")
    async def me(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
        from fastapi import HTTPException

        if not credentials:
            raise HTTPException(status_code=401, detail="Missing token")
        payload = verify_token(credentials.credentials, token_type="access")
        user = await service.get_by_id(payload.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return KeelResponse(data=UsersSerializers.model_validate(user))
