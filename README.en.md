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
from common.core.viewsets import KeelViewSet
from application.db.base import KeelModel

return KeelResponse(data=user, msg="ok")
```

---

## Quick Start

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env
pip install -e ".[dev]"   # or: uv sync --group dev
make run-reload
```

| | |
| --- | --- |
| Docs | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |
| Default admin | `admin` / `AdminPass123` (change it) |

Optional infra:

```bash
make docker-up       # postgres + redis
make celery-worker   # async worker
make celery-beat     # scheduler
```

Job APIs: `POST /api/jobs/add/` · `GET /api/jobs/{task_id}/`

On first boot Keel will: create tables (dev mode) → seed menus / roles / superuser → sync the API registry.  
Open Docs, hit `POST /api/auth/login/`, then play with `/api/items/`.

---

## Features

| Layer | Contents |
| --- | --- |
| Skeleton | `create_app`, middleware, exceptions, rate limit, logging, audit |
| Data | SQLAlchemy async, Alembic layout, table prefix `keel_` |
| Access | User / Role / Menu / Api / Dept + JWT |
| Demo | `/api/items/` minimal CRUD |
| Conventions | `KeelResponse` · `KeelService` · `KeelViewSet` · `KeelModel` |

Common endpoints:

| Area | Path |
| --- | --- |
| Login | `POST /api/auth/login/` |
| Me | `GET /api/auth/me/` |
| Users / roles / menus | `/api/users/` `/api/roles/` `/api/menus/` |
| API sync | `POST /api/apis/refresh/` |
| Demo | `/api/items/` |

---

## Extend

Generate a module: `make module name=order`


Do not stuff business logic into `common/`. Grow by module:

```text
application/modules/<name>/
├── apis/            # ViewSets / routes
├── models/          # SQLAlchemy models
├── serializers/     # request / response shapes
└── services/        # domain actions
```

Three hooks:

1. Implement `apis` / `models` / `serializers` / `services` in the module
2. Aggregate routes in [`application/apis.py`](application/apis.py)
3. Register models in [`application/models/__init__.py`](application/models/__init__.py) so Alembic / `create_all` can see them

Keep the conventions boring on purpose:

- Response: `return KeelResponse(data=..., msg="...")`
- Model: inherit `KeelModel`
- Service: inherit `KeelService`
- API: inherit `KeelViewSet` (uuid / pagination / auth / SQLAlchemy included)
- Auth: `DependAuth` / `DependPermisson` (local: `DISABLE_AUTH=true`)

---

## Config

Full list: [`.env.example`](.env.example). The ones you actually touch:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | DB URL (SQLite works out of the box) |
| `SECRET_KEY` | JWT secret (≥ 32) |
| `REDIS_URL` | cache / token blacklist (degrades if down) |
| `AUTO_CREATE_TABLES` | local auto-create; production: `false` |
| `BOOTSTRAP_ADMIN_*` | first-boot superuser |
| `REDIS_REQUIRED` | fail hard if Redis is down (default: degrade) |

Local shortcut:

```bash
AUTO_CREATE_TABLES=true
```

Before production, at least:

1. Set `DEBUG=false`, rotate the default admin password and `SECRET_KEY`
2. Set `AUTO_CREATE_TABLES=false` and use Alembic:

```bash
make revision m="init"
make migrate
```

3. Point `DATABASE_URL` at PostgreSQL (or your target DB)
4. Enable Redis if needed and tighten `CORS_ORIGINS`

Tests:

```bash
make test
# or
pytest -q
```

---

More: `docs/ERROR_CODES.md` · `docs/REDIS.md`

## vs Library

```text
fast_generic_api   library: ViewSet / Mixin / Backend
keel               app: conventions, RBAC, packaging, modules
```

One answers “how do I write endpoints?”  
The other answers “how does the project stand up?”  
Keel **uses** it. Keel is **not** named after it.

---

## Thanks

| | Project | Role |
| --- | --- | --- |
| ⚙️ | [fast_generic_api](https://github.com/fzf54122/fast_generic_api) | CRUD engine |
| ⚡ | [FastAPI](https://fastapi.tiangolo.com/) | async web core |
| 🗄️ | [SQLAlchemy](https://www.sqlalchemy.org/) · [Alembic](https://alembic.sqlalchemy.org/) | ORM · migrations |
| 🎯 | [Django REST framework](https://www.django-rest-framework.org/) | the ViewSet feel |

<div align="center">

The keel is set. The rest is your product.

If it helps, leave a ⭐ on [Keel](https://github.com/fzf54122/keel) and [fast_generic_api](https://github.com/fzf54122/fast_generic_api)

<br/>

[Issues](https://github.com/fzf54122/keel/issues) · [License](LICENSE)

</div>
