# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.rbac.models import DeptsModel
from application.modules.rbac.serializers import (
    DeptCreateSerializers,
    DeptSerializers,
    DeptUpdateSerializers,
)
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["部门管理"])


class DeptViewSet(KeelViewSet):
    router = router
    prefix = "/depts"
    queryset = DeptsModel
    ordering = ["order", "id"]
    serializer_class = DeptSerializers
    serializer_create_class = DeptCreateSerializers
    serializer_update_class = DeptUpdateSerializers
