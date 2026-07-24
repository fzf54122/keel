# -*- coding: utf-8 -*-
import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "keel"


@pytest.mark.asyncio
async def test_login_and_items_crud(client):
    login = await client.post(
        "/api/auth/login/",
        json={"username": "admin", "password": "AdminPass123"},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    data = body.get("data") or {}
    token = data.get("access_token")
    assert token, body

    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/api/items/",
        json={"name": "hello", "content": "world"},
        headers=headers,
    )
    assert create.status_code in (200, 201), create.text
    item = (create.json().get("data") or create.json())
    assert item.get("uuid") or item.get("id")

    listed = await client.get("/api/items/", headers=headers)
    assert listed.status_code == 200
    payload = listed.json().get("data") or {}
    assert payload.get("total", 0) >= 1

    lookup = item.get("uuid") or item.get("id")
    detail = await client.get(f"/api/items/{lookup}/", headers=headers)
    assert detail.status_code == 200, detail.text

    deleted = await client.delete(f"/api/items/{lookup}/", headers=headers)
    assert deleted.status_code in (200, 204)
