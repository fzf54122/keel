# Keel

<div align="center">

**Raise the keel first. Grow the product later.**

FastAPI app scaffold · DRF-style ViewSets · SQLAlchemy · RBAC

[简体中文](README.md) · [English](README.en.md)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](LICENSE)

</div>

---

A ship can launch without furniture. It cannot launch without a keel.

**Keel** is not another CRUD library. It is a backend skeleton you can start shipping on:

- Write APIs with **ViewSets** (DRF muscle memory)
- Persist with **SQLAlchemy 2.x async**
- Ship with **JWT + RBAC + audit + a demo module**
- Leave generic CRUD to [`fast_generic_api`](https://github.com/fzf54122/fast_generic_api)

You own the business. Keel nails structure, conventions, and bootstrap.

```text
common/                 scaffold primitives (reusable)
application/modules/    business modules (grow by domain)
conf/                   settings only
```

Business code speaks these names:

```python
from common.core.response import KeelResponse
from common.core.service import KeelService
from application.db.base import KeelModel

return KeelResponse(data=user, msg="ok")
```

---

## 30-second start

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env
pip install -e ".[dev]"   # or: uv sync --group dev
make run-reload
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

Default admin: `admin` / `AdminPass123` (change it)

Optional infra:

```bash
make docker-up   # postgres + redis
```

---

## What you get

| Layer | Contents |
| --- | --- |
| Skeleton | `create_app`, middleware, exceptions, rate limit, logging, audit |
| Data | SQLAlchemy async, Alembic layout, table prefix `keel_` |
| Access | User / Role / Menu / Api / Dept + JWT |
| Demo | `/api/items/` minimal CRUD |
| Conventions | `KeelResponse` · `KeelService` · `KeelSchemas` · `KeelModel` |

Common endpoints:

| Area | Path |
| --- | --- |
| Login | `POST /api/auth/login/` |
| Me | `GET /api/auth/me/` |
| Users / roles / menus | `/api/users/` `/api/roles/` `/api/menus/` |
| API sync | `POST /api/apis/refresh/` |
| Demo | `/api/items/` |

Add business here:

```text
application/modules/<name>/{apis,models,serializers,services}
```

Wire routes in `application/apis.py`, register models in `application/models/__init__.py`.

---

## Config that matters

See [`.env.example`](.env.example).

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | DB URL (SQLite works out of the box) |
| `SECRET_KEY` | JWT secret (≥ 32) |
| `REDIS_URL` | cache / token blacklist (degrades if down) |
| `AUTO_CREATE_TABLES` | local auto-create; production: `false` + Alembic |
| `BOOTSTRAP_ADMIN_*` | first-boot superuser |

Production migrations:

```bash
# AUTO_CREATE_TABLES=false
make revision m="init"
make migrate
```

---

## vs fast_generic_api

```text
fast_generic_api   library: ViewSet / Mixin / Backend
keel               app: conventions, RBAC, packaging, modules
```

Keel **uses** it. Keel is **not** named after it.

---

## Acknowledgments

- [fast_generic_api](https://github.com/fzf54122/fast_generic_api) — CRUD engine  
- [FastAPI](https://fastapi.tiangolo.com/) · [SQLAlchemy](https://www.sqlalchemy.org/) · [Alembic](https://alembic.sqlalchemy.org/)  
- [Django REST framework](https://www.django-rest-framework.org/) — the ViewSet feel  

If this helps, star the repo — and star `fast_generic_api` too.

---

## License

[Apache-2.0](LICENSE)
