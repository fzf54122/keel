"""Import all models so metadata is complete for Alembic / create_all."""

from application.modules.rbac.models import (  # noqa: F401
    ApiModel,
    AuditLogModel,
    DeptsModel,
    FileModel,
    MenuModel,
    RoleModel,
)
from application.modules.demo.models import ItemModel  # noqa: F401
from application.modules.system.models import SettingsModel, UserModel  # noqa: F401
from application.db.base import Base, KeelModel  # noqa: F401

__all__ = [
    "Base",
    "KeelModel",
    "UserModel",
    "SettingsModel",
    "RoleModel",
    "MenuModel",
    "ApiModel",
    "DeptsModel",
    "AuditLogModel",
    "FileModel",
    "ItemModel",
]
