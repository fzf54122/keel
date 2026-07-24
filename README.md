# Keel

<div align="center">

**先立龙骨，再长业务。**

FastAPI 应用脚手架 · DRF 手感 · SQLAlchemy · RBAC

[简体中文](README.md) · [English](README.en.md)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](LICENSE)

</div>

---

船可以没有装修，但不能没有龙骨。

**Keel** 不做又一个 CRUD 库。它给你一套能直接开干的后端骨架：

- 用 **ViewSet** 写接口（DRF 那套肌肉记忆）
- 用 **SQLAlchemy 2.x async** 落库
- 自带 **JWT + RBAC + 审计 + Demo**
- 底层 CRUD 引擎交给 [`fast_generic_api`](https://github.com/fzf54122/fast_generic_api)

你负责业务；规范、分层、启动引导，Keel 先钉死。

```text
common/                 脚手架能力（可复用）
application/modules/    业务模块（按领域长）
conf/                   配置（不写业务）
```

业务只认这几个名字：

```python
from common.core.response import KeelResponse
from common.core.service import KeelService
from common.core.viewsets import KeelViewSet
from application.db.base import KeelModel

return KeelResponse(data=user, msg="ok")
```

---

## 快速启动

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env
pip install -e ".[dev]"   # 或: uv sync --group dev
make run-reload
```

| | |
| --- | --- |
| Docs | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |
| 默认超管 | `admin` / `AdminPass123`（立刻改掉） |

可选依赖：

```bash
make docker-up       # postgres + redis
make celery-worker   # 异步任务 worker
make celery-beat     # 定时调度
```

任务接口：`POST /api/jobs/add/` · `GET /api/jobs/{task_id}/`

第一次启动会自动：建表（开发模式）→ 种菜单/角色/超管 → 同步 API 权限表。  
打开 Docs，先打 `POST /api/auth/login/`，再玩 `/api/items/`。

---

## 已有能力

| 层 | 内容 |
| --- | --- |
| 骨架 | `create_app`、中间件、异常、限流、日志、审计 |
| 数据 | SQLAlchemy async、Alembic 目录、表前缀 `keel_` |
| 权限 | User / Role / Menu / Api / Dept + JWT |
| 示例 | `/api/items/` 最小 CRUD |
| 规范 | `KeelResponse` · `KeelService` · `KeelViewSet` · `KeelModel` |

常用接口：

| 模块 | 路径 |
| --- | --- |
| 登录 | `POST /api/auth/login/` |
| 当前用户 | `GET /api/auth/me/` |
| 用户 / 角色 / 菜单 | `/api/users/` `/api/roles/` `/api/menus/` |
| API 同步 | `POST /api/apis/refresh/` |
| Demo | `/api/items/` |

---

## 业务扩展

生成模块：`make module name=order`


别在 `common/` 里塞业务。新能力按模块长：

```text
application/modules/<name>/
├── apis/            # ViewSet / 路由
├── models/          # SQLAlchemy 模型
├── serializers/     # 入参 / 出参
└── services/        # 业务动作
```

三步挂上去：

1. 在模块里写好 `apis` / `models` / `serializers` / `services`
2. 路由汇总进 [`application/apis.py`](application/apis.py)
3. 模型登记进 [`application/models/__init__.py`](application/models/__init__.py)（给 Alembic / `create_all` 看见）

约定尽量简单：

- 响应：`return KeelResponse(data=..., msg="...")`
- 模型：继承 `KeelModel`
- 服务：继承 `KeelService`
- 接口：继承 `KeelViewSet`（uuid / 分页 / 鉴权 / SQLAlchemy 已内置）
- 鉴权：`DependAuth` / `DependPermisson`（本地可 `DISABLE_AUTH=true`）

---

## 配置上线

完整变量见 [`.env.example`](.env.example)。真正常改的只有这些：

| 变量 | 干嘛的 |
| --- | --- |
| `DATABASE_URL` | 库连接（默认 SQLite 可跑） |
| `SECRET_KEY` | JWT 密钥（≥ 32） |
| `REDIS_URL` | 缓存 / token 黑名单（挂了会降级） |
| `AUTO_CREATE_TABLES` | 开发自动建表；生产改 `false` |
| `BOOTSTRAP_ADMIN_*` | 首启超管 |

本地可以偷懒：

```bash
AUTO_CREATE_TABLES=true
```

上生产前至少做这几件事：

1. `DEBUG=false`，换掉默认超管密码和 `SECRET_KEY`
2. `AUTO_CREATE_TABLES=false`，改用 Alembic：

```bash
make revision m="init"
make migrate
```

3. `DATABASE_URL` 指到 PostgreSQL（或你的目标库）
4. 按需启用 Redis，收紧 `CORS_ORIGINS`

测试：

```bash
make test
# 或
pytest -q
```

---

## 库的分工

```text
fast_generic_api   库：ViewSet / Mixin / Backend
keel               应用：规范、RBAC、工程化、模块骨架
```

一个负责「怎么写接口」，一个负责「项目怎么立起来」。  
Keel **用**它，不 **叫**它的名字。

---

## 鸣谢

| | 项目 | 角色 |
| --- | --- | --- |
| ⚙️ | [fast_generic_api](https://github.com/fzf54122/fast_generic_api) | CRUD 引擎 |
| ⚡ | [FastAPI](https://fastapi.tiangolo.com/) | 异步 Web 骨架 |
| 🗄️ | [SQLAlchemy](https://www.sqlalchemy.org/) · [Alembic](https://alembic.sqlalchemy.org/) | ORM · 迁移 |
| 🎯 | [Django REST framework](https://www.django-rest-framework.org/) | ViewSet 手感的源头 |

<div align="center">

龙骨立好了。剩下的，交给你的业务。

有用的话，给 [Keel](https://github.com/fzf54122/keel) 和 [fast_generic_api](https://github.com/fzf54122/fast_generic_api) 各一颗 ⭐

<br/>

[Issues](https://github.com/fzf54122/keel/issues) · [License](LICENSE)

</div>
