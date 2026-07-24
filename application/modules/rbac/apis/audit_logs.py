# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.rbac.models import AuditLogModel
from application.modules.rbac.serializers import AuditLogSerializers
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["审计日志"])


class AuditLogViewSet(KeelViewSet):
    router = router
    prefix = "/auditlogs"
    queryset = AuditLogModel
    serializer_class = AuditLogSerializers
