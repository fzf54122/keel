# 🚀 Keel

<div align="center">

**The FastAPI application keel: DRF-style ViewSets + SQLAlchemy + RBAC**

[简体中文](README.md) | **English**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-fzf54122%2Fkeel-black.svg)](https://github.com/fzf54122/keel)

[📖 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture) • [📐 Conventions](#-conventions) • [📚 API](#-api) • [🔧 Configuration](#-configuration) • [🙏 Acknowledgments](#-acknowledgments)

</div>

---

## 🌟 Why Keel?

**Keel** is the structural backbone of a backend app: establish conventions first, then grow business modules on top.

It is not another CRUD library. It is a **ready-to-run application scaffold**:

| Source | What you get |
| --- | --- |
| **FastAPI** | Async, dependency injection, OpenAPI |
| **DRF-style DX** | ViewSet / Serializer / Permission / Mixin |
| **SQLAlchemy** | 2.x async models, sessions, Alembic migrations |
| **fast_generic_api** | Generic CRUD engine (dependency, not this repo's name) |

<div align="center">

| 🏗️ **3-Layer Architecture** | 🔐 **RBAC** | ⚡ **Batteries Included** | 🧩 **Extensible** |
| :---: | :---: | :---: | :---: |
| API / Service / Model | User · Role · Menu · API | JWT · Audit · Demo | Grow via modules |

</div>

Current version: **0.1.0**

---

## ✨ Features

### 🔧 Application Skeleton

- **App factory** `create_app` with lifespan bootstrap
- **SQLAlchemy async** session middleware + `backend_provider`
- **Alembic** migration layout (recommended for production; `AUTO_CREATE_TABLES` for local)
- **Redis cache** with graceful degradation when unavailable
- **Unified exceptions / rate limit / security headers / request logs / audit logs**

### 🔐 RBAC

- User / Role / Menu / Api / Dept / AuditLog
- JWT access + refresh
- `DependAuth` / `DependPermisson`
- First-boot bootstrap: menus, roles, superuser, API registry sync

### 📦 Demo

- Minimal CRUD at `/api/items/` to prove the scaffold works end-to-end

---

## 🛠️ Tech Stack

| Component | Choice |
| --- | --- |
| Web | FastAPI 0.100+ |
| CRUD engine | [fast_generic_api](https://github.com/fzf54122/fast_generic_api) |
| ORM | SQLAlchemy 2.x async |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Cache | Redis (optional) |
| Password hashing | argon2 |
| Python | 3.11+ |

---

## 🏗️ Architecture

```text
keel/
├── conf/                         # Settings (env)
├── common/                       # Scaffold infrastructure (easy to separate from business)
│   ├── core/
│   │   ├── app.py                # middleware / exceptions / router mount
│   │   ├── bootstrap.py          # startup initialization
│   │   ├── response.py           # KeelResponse
│   │   ├── service.py            # KeelService
│   │   ├── schemas.py            # KeelSchemas
│   │   ├── permission.py         # JWT + RBAC Depends
│   │   ├── jwt.py / password.py / cache.py / ...
│   └── logger/
├── application/
│   ├── __init__.py               # create_app
│   ├── apis.py                   # route aggregation
│   ├── db/                       # engine / session / backend
│   ├── models/                   # model aggregation (for Alembic)
│   └── modules/                  # business modules
│       ├── system/               # auth / users
│       ├── rbac/                 # roles · menus · apis · depts · audit
│       └── demo/                 # Item example
├── alembic/
├── tests/
├── docker-compose.yaml           # postgres + redis
├── Dockerfile
├── Makefile
└── pyproject.toml
```

### Layering

| Path | Responsibility |
| --- | --- |
| `common/` | Scaffold capabilities, reusable across projects |
| `application/modules/*` | Business modules, grow by domain |
| `conf/` | Configuration only, no business logic |

```text
fast_generic_api  →  library: ViewSet / Mixin / Backend
keel              →  app scaffold: config, RBAC, packaging, module skeleton
```

Keel **depends on** `fast_generic_api`, but does not inherit its project naming.

---

## 🚀 Quick Start

### ⚡ Install

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env

# recommended: uv
uv sync --group dev

# or pip
pip install -e ".[dev]"
```

Optional infrastructure:

```bash
make docker-up   # postgres + redis
```

SQLite works for local development. Switch `DATABASE_URL` in `.env` for PostgreSQL.

### 💻 Run

```bash
make run-reload
# or
uvicorn application:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

On first boot Keel will:

1. Create tables when `AUTO_CREATE_TABLES=true`
2. Seed menus / roles / superuser
3. Sync the API permission registry

Default superuser (change immediately):

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `AdminPass123` (`BOOTSTRAP_ADMIN_PASSWORD`) |

### 🧪 Tests

```bash
make test
# or
pytest -q
```

### 🗄️ Migrations (production)

```bash
# .env: AUTO_CREATE_TABLES=false
make revision m="init"
make migrate
```

---

## 📐 Conventions

Business code should only use these scaffold entry points:

| Class | Purpose | Example |
| --- | --- | --- |
| **`KeelResponse`** | Unified response envelope | `return KeelResponse(data=..., msg="...")` |
| **`KeelService`** | Service base class | `class UserService(KeelService[UserModel])` |
| **`KeelSchemas`** | Schema base class | inherit as needed |
| **`KeelModel`** | ORM abstract model | `class ItemModel(KeelModel)` |
| **`KeelTask`** | Background task context | used internally by middleware |

Response envelope:

```json
{
  "code": 200,
  "status": "success",
  "data": {},
  "msg": "OK"
}
```

Example:

```python
from common.core.response import KeelResponse

return KeelResponse(data=token_out, msg="login success")
return KeelResponse(msg="logout success")
return KeelResponse(data=None, code=400, status="error", msg="invalid password")
```

> Do not use the raw `fast_generic_api` Response class in business code.

---

## 📚 API

| Module | Prefix |
| --- | --- |
| Auth | `/api/auth/login/` `/api/auth/refresh/` `/api/auth/me/` |
| Users | `/api/users/` |
| Roles | `/api/roles/` |
| Menus | `/api/menus/` |
| APIs | `/api/apis/` `/api/apis/refresh/` |
| Depts | `/api/depts/` |
| Audit | `/api/auditlogs/` |
| Demo | `/api/items/` |

Recommended layout for a new module:

```text
application/modules/<name>/{apis,models,serializers,services}
```

Register routes in `application/apis.py` and models in `application/models/__init__.py`.

---

## 🔧 Configuration

See [`.env.example`](.env.example). Common keys:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy async URL |
| `TABLE_PREFIX` | Table prefix, default `keel_` |
| `REDIS_URL` | Cache / token blacklist |
| `SECRET_KEY` | JWT secret (≥ 32 chars) |
| `DISABLE_AUTH` | Skip auth for local debugging |
| `AUTO_CREATE_TABLES` | Auto-create tables in development |
| `BOOTSTRAP_ADMIN_*` | First-boot superuser |

---

## 🙏 Acknowledgments

Keel stands on the shoulders of these projects and communities:

| Project | Role |
| --- | --- |
| [fast_generic_api](https://github.com/fzf54122/fast_generic_api) | DRF-style ViewSet / Mixin / Backend — Keel's CRUD engine |
| [FastAPI](https://fastapi.tiangolo.com/) | Modern async web framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.x async ORM |
| [Django REST Framework](https://www.django-rest-framework.org/) | Design inspiration for ViewSet / Serializer / Permission |
| [Pydantic](https://docs.pydantic.dev/) | Validation and settings |
| [Alembic](https://alembic.sqlalchemy.org/) | Database migrations |

Thanks to the open-source community. If Keel helps you, please star this repo — and also star [fast_generic_api](https://github.com/fzf54122/fast_generic_api).

---

## 📄 License

[Apache-2.0](LICENSE)
