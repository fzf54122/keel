# -*- coding: utf-8 -*-
"""Auth-required tests in an isolated process (fresh settings import)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


SCRIPT = r'''
import os
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["SWAGGER_UI_PASSWORD"] = "test_password"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DISABLE_AUTH"] = "false"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["BOOTSTRAP_ADMIN_PASSWORD"] = "AdminPass123"
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

import asyncio
from httpx import ASGITransport, AsyncClient
from application import create_app

async def main():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with app.router.lifespan_context(app):
            # no token
            r = await client.get("/api/items/")
            assert r.status_code == 401, (r.status_code, r.text)

            # bad token
            r = await client.get(
                "/api/items/",
                headers={"Authorization": "Bearer not-a-token"},
            )
            assert r.status_code == 401, (r.status_code, r.text)

            # login + access
            login = await client.post(
                "/api/auth/login/",
                json={"username": "admin", "password": "AdminPass123"},
            )
            assert login.status_code == 200, login.text
            token = (login.json().get("data") or {})["access_token"]
            r = await client.get(
                "/api/items/",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 200, (r.status_code, r.text)
    print("auth-required-ok")

asyncio.run(main())
'''


def test_auth_required_isolated_process():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "auth-required-ok" in proc.stdout
