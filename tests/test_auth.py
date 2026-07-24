# -*- coding: utf-8 -*-
import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    resp = await client.post(
        "/api/auth/login/",
        json={"username": "admin", "password": "AdminPass123"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json().get("data") or {}
    assert data.get("access_token")
    assert data.get("refresh_token")


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post(
        "/api/auth/login/",
        json={"username": "admin", "password": "wrong-pass-1"},
    )
    assert resp.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_me_and_refresh(client):
    login = await client.post(
        "/api/auth/login/",
        json={"username": "admin", "password": "AdminPass123"},
    )
    tokens = login.json().get("data") or {}
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    me = await client.get(
        "/api/auth/me/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert me.status_code == 200, me.text
    user = me.json().get("data") or {}
    assert user.get("username") == "admin"
    assert isinstance(user.get("roles"), list)

    refreshed = await client.post(
        "/api/auth/refresh/",
        json={"refresh_token": refresh},
    )
    assert refreshed.status_code == 200, refreshed.text
    new_tokens = refreshed.json().get("data") or {}
    assert new_tokens.get("access_token")


@pytest.mark.asyncio
async def test_me_without_token(client):
    resp = await client.get("/api/auth/me/")
    assert resp.status_code in (401, 403, 422, 500) or resp.json().get("code") in {401, 403}
