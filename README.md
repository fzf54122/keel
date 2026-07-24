# 🚀 Keel

<div align="center">

**FastAPI 应用龙骨：DRF 风格 ViewSet + SQLAlchemy + RBAC**

**简体中文** | [English](README.en.md)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-fzf54122%2Fkeel-black.svg)](https://github.com/fzf54122/keel)

[📖 快速开始](#-快速开始) • [🏗️ 架构](#-架构) • [📐 命名规范](#-命名规范) • [📚 API](#-api) • [🔧 配置](#-配置) • [🙏 鸣谢](#-鸣谢)

</div>

---

## 🌟 为什么是 Keel？

**Keel（龙骨）** 是后端应用的主梁：先立规范与结构，再往上长业务。

它不是又一个 CRUD 库，而是 **可直接开干的应用脚手架**：

| 来源 | 你得到什么 |
| --- | --- |
| **FastAPI** | 异步、依赖注入、OpenAPI |
| **DRF 手感** | ViewSet / Serializer / Permission / Mixin |
| **SQLAlchemy** | 2.x async 模型、会话、Alembic 迁移 |
| **fast_generic_api** | 底层通用 CRUD 能力（依赖库，不是本仓库名字） |

<div align="center">

| 🏗️ **三层架构** | 🔐 **RBAC** | ⚡ **开箱即用** | 🧩 **可扩展** |
| :---: | :---: | :---: | :---: |
| API / Service / Model | 用户 · 角色 · 菜单 · API | JWT · 审计 · Demo | 按 modules 加业务 |

</div>

当前版本：**0.1.0**

---

## ✨ 核心能力

### 🔧 应用骨架

- **应用工厂** `create_app` + lifespan 启动引导
- **SQLAlchemy async** 会话中间件 + `backend_provider`
- **Alembic** 迁移目录（生产推荐；开发可 `AUTO_CREATE_TABLES`）
- **Redis 缓存**（不可用时自动降级）
- **统一异常 / 限流 / 安全头 / 请求日志 / 审计日志**

### 🔐 RBAC

- User / Role / Menu / Api / Dept / AuditLog
- JWT access + refresh
- `DependAuth` / `DependPermisson`
- 首次启动引导：菜单、角色、超管、API 同步

### 📦 Demo

- `/api/items/` 最小 CRUD，验证脚手架可跑通

---

## 🛠️ 技术栈

| 组件 | 选型 |
| --- | --- |
| Web | FastAPI 0.100+ |
| CRUD 引擎 | [fast_generic_api](https://github.com/fzf54122/fast_generic_api) |
| ORM | SQLAlchemy 2.x async |
| 迁移 | Alembic |
| 校验 | Pydantic v2 |
| 缓存 | Redis（可选） |
| 密码 | argon2 |
| Python | 3.11+ |

---

## 🏗️ 架构

```text
keel/
├── conf/                         # Settings（环境变量）
├── common/                       # 脚手架基建（易与业务区分）
│   ├── core/
│   │   ├── app.py                # 中间件 / 异常 / 路由挂载
│   │   ├── bootstrap.py          # 启动初始化
│   │   ├── response.py           # KeelResponse
│   │   ├── service.py            # KeelService
│   │   ├── schemas.py            # KeelSchemas
│   │   ├── permission.py         # JWT + RBAC Depends
│   │   ├── jwt.py / password.py / cache.py / ...
│   └── logger/
├── application/
│   ├── __init__.py               # create_app
│   ├── apis.py                   # 路由汇总
│   ├── db/                       # engine / session / backend
│   ├── models/                   # 模型聚合（Alembic 用）
│   └── modules/                  # 业务模块
│       ├── system/               # 登录 / 用户
│       ├── rbac/                 # 角色 · 菜单 · API · 部门 · 审计
│       └── demo/                 # Item 示例
├── alembic/
├── tests/
├── docker-compose.yaml           # postgres + redis
├── Dockerfile
├── Makefile
└── pyproject.toml
```

### 分层约定

| 目录 | 职责 |
| --- | --- |
| `common/` | 脚手架能力，跨项目可复用 |
| `application/modules/*` | 业务模块，按领域增长 |
| `conf/` | 配置，不写业务 |

```text
fast_generic_api  →  库：ViewSet / Mixin / Backend
keel              →  应用脚手架：配置、RBAC、工程化、业务模块骨架
```

Keel **使用** `fast_generic_api`，但不继承其项目命名。

---

## 🚀 快速开始

### ⚡ 安装

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env

# 推荐 uv
uv sync --group dev

# 或 pip
pip install -e ".[dev]"
```

可选依赖服务：

```bash
make docker-up   # postgres + redis
```

开发默认可用 SQLite（`.env` 里改 `DATABASE_URL` 即可切 PostgreSQL）。

### 💻 启动

```bash
make run-reload
# 或
uvicorn application:app --reload --host 0.0.0.0 --port 8000
```

- Swagger：http://127.0.0.1:8000/docs
- Health：http://127.0.0.1:8000/health

首次启动会自动：

1. 建表（`AUTO_CREATE_TABLES=true` 时）
2. 初始化菜单 / 角色 / 超管
3. 同步 API 权限表

默认超管（请立刻修改）：

| 项 | 值 |
| --- | --- |
| 用户名 | `admin` |
| 密码 | `AdminPass123`（`BOOTSTRAP_ADMIN_PASSWORD`） |

### 🧪 测试

```bash
make test
# 或
pytest -q
```

### 🗄️ 迁移（生产）

```bash
# .env: AUTO_CREATE_TABLES=false
make revision m="init"
make migrate
```

---

## 📐 命名规范

脚手架制定规范，业务只面向这些入口：

| 规范类 | 用途 | 写法 |
| --- | --- | --- |
| **`KeelResponse`** | 统一响应信封 | `return KeelResponse(data=..., msg="...")` |
| **`KeelService`** | Service 基类 | `class UserService(KeelService[UserModel])` |
| **`KeelSchemas`** | Schema 基类 | 按需继承 |
| **`KeelModel`** | ORM 抽象模型 | `class ItemModel(KeelModel)` |
| **`KeelTask`** | 后台任务上下文 | 中间件内部 |

响应体统一：

```json
{
  "code": 200,
  "status": "success",
  "data": {},
  "msg": "OK"
}
```

示例：

```python
from common.core.response import KeelResponse

return KeelResponse(data=token_out, msg="登录成功")
return KeelResponse(msg="退出登录成功")
return KeelResponse(data=None, code=400, status="error", msg="密码错误")
```

> 业务代码不要直接使用 `fast_generic_api` 的 Response 类。

---

## 📚 API

| 模块 | 前缀 |
| --- | --- |
| 登录 | `/api/auth/login/` `/api/auth/refresh/` `/api/auth/me/` |
| 用户 | `/api/users/` |
| 角色 | `/api/roles/` |
| 菜单 | `/api/menus/` |
| API 权限 | `/api/apis/` `/api/apis/refresh/` |
| 部门 | `/api/depts/` |
| 审计 | `/api/auditlogs/` |
| Demo | `/api/items/` |

新增业务模块建议：

```text
application/modules/<name>/{apis,models,serializers,services}
```

在 `application/apis.py` 挂路由，在 `application/models/__init__.py` 注册模型。

---

## 🔧 配置

见 [`.env.example`](.env.example)，常用项：

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy async URL |
| `TABLE_PREFIX` | 表前缀，默认 `keel_` |
| `REDIS_URL` | 缓存 / token 黑名单 |
| `SECRET_KEY` | JWT 密钥（≥ 32） |
| `DISABLE_AUTH` | 本地调试跳过鉴权 |
| `AUTO_CREATE_TABLES` | 开发自动建表 |
| `BOOTSTRAP_ADMIN_*` | 首启超管 |

---

## 🙏 鸣谢

Keel 站在这些优秀项目与社区之上：

| 项目 | 说明 |
| --- | --- |
| [fast_generic_api](https://github.com/fzf54122/fast_generic_api) | DRF 风格 ViewSet / Mixin / Backend，Keel 的 CRUD 引擎 |
| [FastAPI](https://fastapi.tiangolo.com/) | 现代异步 Web 框架 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.x async ORM |
| [Django REST Framework](https://www.django-rest-framework.org/) | ViewSet / Serializer / Permission 的设计灵感 |
| [Pydantic](https://docs.pydantic.dev/) | 数据校验与设置 |
| [Alembic](https://alembic.sqlalchemy.org/) | 数据库迁移 |

感谢开源社区的持续贡献。如果你觉得 Keel 有用，欢迎 Star 本仓库，也请给 [fast_generic_api](https://github.com/fzf54122/fast_generic_api) 一个 Star。

---

## 📄 License

[Apache-2.0](LICENSE)
