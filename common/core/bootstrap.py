# -*- coding: utf-8 -*-
"""Startup bootstrap: tables, seed data, API sync."""

from __future__ import annotations

from sqlalchemy import select

from application.db.base import Base
from application.db.backend import get_current_session
from application.db.session import async_session_factory, engine
from application.modules.rbac.enums import MenuType
from application.modules.rbac.models import ApiModel, MenuModel, RoleModel
from application.modules.rbac.services import ApiService
from application.modules.system.models import UserModel
from common.core.cache import cache_manager
from common.core.password import get_password_hash
from common.logger import logger
from conf import settings


async def init_tables() -> None:
    if not settings.AUTO_CREATE_TABLES:
        logger.info("AUTO_CREATE_TABLES=false, skip metadata.create_all (use Alembic)")
        return
    import application.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")


async def init_menus() -> None:
    session = get_current_session()
    exists = await session.scalar(select(MenuModel.id).limit(1))
    if exists:
        logger.info("Menus already exist, skip")
        return

    parent = MenuModel(
        menu_type=MenuType.CATALOG.value,
        name="系统管理",
        path="/system",
        order=1,
        parent_id=0,
        icon="carbon:gui-management",
        component="Layout",
        redirect="/system/user",
    )
    session.add(parent)
    await session.flush()

    children = [
        ("用户管理", "user", 1, "material-symbols:person-outline-rounded", "/system/user"),
        ("角色管理", "role", 2, "carbon:user-role", "/system/role"),
        ("菜单管理", "menu", 3, "material-symbols:list-alt-outline", "/system/menu"),
        ("API管理", "api", 4, "ant-design:api-outlined", "/system/api"),
        ("部门管理", "dept", 5, "mingcute:department-line", "/system/dept"),
        ("审计日志", "auditlog", 6, "ph:clipboard-text-bold", "/system/auditlog"),
        ("任务中心", "jobs", 7, "mdi:timer-cog-outline", "/system/jobs"),
    ]
    if settings.ENABLE_DEMO:
        children.append(("Demo Items", "items", 8, "mdi:package-variant", "/demo/items"))

    for name, path, order, icon, component in children:
        session.add(
            MenuModel(
                menu_type=MenuType.MENU.value,
                name=name,
                path=path,
                order=order,
                parent_id=parent.id,
                icon=icon,
                component=component,
            )
        )
    await session.flush()
    logger.info("Default menus created")


async def init_roles() -> None:
    session = get_current_session()
    exists = await session.scalar(select(RoleModel.id).limit(1))
    if exists:
        logger.info("Roles already exist, skip")
        return

    menus = list((await session.execute(select(MenuModel))).scalars().all())
    apis = list((await session.execute(select(ApiModel))).scalars().all())

    admin_role = RoleModel(name="管理员", desc="管理员角色", is_active=True)
    user_role = RoleModel(name="普通用户", desc="普通用户角色", is_active=True)
    admin_role.menus = menus
    admin_role.apis = apis
    user_role.menus = menus
    user_role.apis = [api for api in apis if api.method == "GET"]
    session.add_all([admin_role, user_role])
    await session.flush()
    logger.info("Default roles created")


async def init_superuser() -> None:
    session = get_current_session()
    exists = await session.scalar(select(UserModel.id).limit(1))
    if exists:
        logger.info("Users already exist, skip superuser bootstrap")
        return

    result = await session.execute(select(RoleModel).where(RoleModel.name == "管理员"))
    admin_role = result.scalar_one_or_none()
    user = UserModel(
        username=settings.BOOTSTRAP_ADMIN_USERNAME,
        email=settings.BOOTSTRAP_ADMIN_EMAIL,
        password=get_password_hash(settings.BOOTSTRAP_ADMIN_PASSWORD),
        alias="系统管理员",
        is_active=True,
        is_superuser=True,
    )
    if admin_role:
        user.roles = [admin_role]
    session.add(user)
    await session.flush()
    logger.info(
        f"Superuser created: {settings.BOOTSTRAP_ADMIN_USERNAME} "
        f"(change password immediately)"
    )


async def init_apis(app) -> None:
    service = ApiService()
    count = await service.refresh_api(app)
    await service.grant_all_apis_to_admin()
    logger.info(f"API registry refreshed ({count} routes)")


async def init_data(app=None) -> None:
    """启动顺序：
    1) redis
    2) tables
    3) menus / roles / superuser
    4) API sync（路由已挂载后）并给管理员补全权限
    """
    logger.info("System bootstrap start")
    await cache_manager.connect()
    await init_tables()

    async with async_session_factory() as session:
        from application.db.backend import _session_ctx

        token = _session_ctx.set(session)
        try:
            await init_menus()
            await init_roles()
            await init_superuser()
            if app is not None:
                await init_apis(app)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            _session_ctx.reset(token)
    logger.info("System bootstrap done")


async def shutdown_data() -> None:
    await cache_manager.disconnect()
    await engine.dispose()
    logger.info("System shutdown complete")
