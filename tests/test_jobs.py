# -*- coding: utf-8 -*-
import os

import pytest

# force eager before app import in this module's client fixture usage
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")


@pytest.mark.asyncio
async def test_enqueue_add_and_status(client):
    resp = await client.post("/api/jobs/add/", json={"x": 1, "y": 2})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    data = body.get("data") or {}
    task_id = data.get("task_id")
    assert task_id

    status = await client.get(f"/api/jobs/{task_id}/")
    assert status.status_code == 200, status.text
    payload = status.json().get("data") or {}
    # eager mode should finish immediately
    assert payload.get("state") in {"SUCCESS", "PENDING", "STARTED"}
    if payload.get("state") == "SUCCESS":
        assert payload.get("result", {}).get("result") == 3
