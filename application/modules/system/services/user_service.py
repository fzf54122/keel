# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.modules.rbac.models.role import RoleModel
from application.modules.system.models import UserModel
from application.db.backend import get_current_session
from common.core.password import get_password_hash, verify_password
from common.core.service import KeelService


class UserService(KeelService[UserModel]):
    def __init__(self):
        super().__init__(model=UserModel)

    async def get_by_username(self, username: str) -> UserModel | None:
        session = get_current_session()
        result = await session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.username == username, UserModel.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> UserModel | None:
        session = get_current_session()
        result = await session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == user_id, UserModel.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def create_user(self, obj_in) -> UserModel:
        session = get_current_session()
        data = obj_in.model_dump()
        role_ids = data.pop("role_ids", None) or []
        data["password"] = get_password_hash(data.pop("password"))
        user = UserModel(**data)
        if role_ids:
            result = await session.execute(select(RoleModel).where(RoleModel.id.in_(role_ids)))
            user.roles = list(result.scalars().all())
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def update_last_login(self, user_id: int) -> None:
        session = get_current_session()
        user = await session.get(UserModel, user_id)
        if user:
            user.last_login = datetime.now()
            await session.flush()

    async def authenticate(self, credentials) -> UserModel:
        user = await self.get_by_username(credentials.username)
        if not user:
            raise HTTPException(status_code=400, detail="无效的用户名")
        if not verify_password(credentials.password, user.password or ""):
            raise HTTPException(status_code=400, detail="密码错误!")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="用户已被禁用")
        return user

    async def handle_update_user_password(self, data: dict) -> None:
        session = get_current_session()
        uuid = data["uuid"]
        password_data = data["password_data"]
        current_user: UserModel = data["current_user"]

        result = await session.execute(
            select(UserModel).where(UserModel.uuid == str(uuid), UserModel.is_deleted.is_(False))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if str(user.uuid) != str(current_user.uuid) and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="不能修改其他用户密码")
        if not current_user.is_superuser or str(user.uuid) == str(current_user.uuid):
            if not verify_password(password_data.old_password, user.password or ""):
                raise HTTPException(status_code=400, detail="旧密码错误")
        user.password = get_password_hash(password_data.new_password)
        await session.flush()
