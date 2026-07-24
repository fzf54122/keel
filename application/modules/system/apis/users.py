# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.system.models import UserModel
from application.modules.system.serializers import (
    UsersCreateSerializers,
    UsersSerializers,
    UsersUpdatePasswordSerializers,
    UsersUpdateSerializers,
)
from application.modules.system.services import UserService
from common.core.permission import DependPermisson
from common.core.response import KeelResponse
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["用户管理"])
service = UserService()


class UserViewSet(KeelViewSet):
    router = router
    prefix = "/users"
    queryset = UserModel
    serializer_class = UsersSerializers
    serializer_create_class = UsersCreateSerializers
    serializer_update_class = UsersUpdateSerializers

    @staticmethod
    @router.post("/{uuid}/update_password/", summary="修改用户密码")
    async def update_user_password(
        uuid: str,
        password_data: UsersUpdatePasswordSerializers,
        current_user: UserModel = DependPermisson,
    ):
        await service.handle_update_user_password(
            {
                "uuid": uuid,
                "current_user": current_user,
                "password_data": password_data,
            }
        )
        return KeelResponse(msg="密码修改成功")
