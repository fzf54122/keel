# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.rbac.models import AuditLogModel
from application.modules.rbac.serializers import AuditLogSerializers
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from conf import settings

router = APIRouter(tags=["审计日志"])


class AuditLogViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/auditlogs"
    queryset = AuditLogModel
    ordering = ["-created_at"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    serializer_class = AuditLogSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
    # read-only-ish: still allow destroy soft-delete via generic if needed
