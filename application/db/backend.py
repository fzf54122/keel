# -*- coding: utf-8 -*-
"""fast_generic_api SQLAlchemy backend provider."""

from __future__ import annotations

from contextvars import ContextVar

from fastapi import Request
from fast_generic_api.backends import SQLAlchemyBackend
from sqlalchemy.ext.asyncio import AsyncSession

from application.db.session import async_session_factory

_session_ctx: ContextVar[AsyncSession | None] = ContextVar("sa_session", default=None)


def get_current_session() -> AsyncSession:
    session = _session_ctx.get()
    if session is None:
        raise RuntimeError("No SQLAlchemy session bound to current request")
    return session


async def bind_session() -> AsyncSession:
    """Create a session and bind to context for this request."""
    session = async_session_factory()
    _session_ctx.set(session)
    return session


async def unbind_session(session: AsyncSession | None = None) -> None:
    current = session or _session_ctx.get()
    if current is not None:
        await current.close()
    _session_ctx.set(None)


def backend_provider() -> SQLAlchemyBackend:
    """Used by ViewSet.backend_provider for per-request ORM backend."""
    return SQLAlchemyBackend(get_current_session())


async def sa_session_dependency(request: Request):
    """FastAPI dependency: open session for the whole request lifecycle."""
    session = async_session_factory()
    token = _session_ctx.set(session)
    request.state.db = session
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        _session_ctx.reset(token)
