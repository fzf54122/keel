# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.rbac.models import RoleModel
from application.modules.rbac.serializers import (
    RoleCreateSerializers,
    RoleSerializers,
    RoleUpdateSerializers,
)
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["角色管理"])


class RoleViewSet(KeelViewSet):
    router = router
    prefix = "/roles"
    queryset = RoleModel
    ordering = ["created_at"]
    serializer_class = RoleSerializers
    serializer_create_class = RoleCreateSerializers
    serializer_update_class = RoleUpdateSerializers
