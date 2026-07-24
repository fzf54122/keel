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
from application.db.base import KeelModel

return KeelResponse(data=user, msg="ok")
```

---

## 30 秒启动

```bash
git clone git@github.com:fzf54122/keel.git
cd keel
cp .env.example .env
pip install -e ".[dev]"   # 或: uv sync --group dev
make run-reload
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

默认超管：`admin` / `AdminPass123`（立刻改掉）

可选依赖：

```bash
make docker-up   # postgres + redis
```

---

## 你拿到什么

| 层 | 内容 |
| --- | --- |
| 骨架 | `create_app`、中间件、异常、限流、日志、审计 |
| 数据 | SQLAlchemy async、Alembic 目录、表前缀 `keel_` |
| 权限 | User / Role / Menu / Api / Dept + JWT |
| 示例 | `/api/items/` 最小 CRUD |
| 规范 | `KeelResponse` · `KeelService` · `KeelSchemas` · `KeelModel` |

常用接口：

| 模块 | 路径 |
| --- | --- |
| 登录 | `POST /api/auth/login/` |
| 当前用户 | `GET /api/auth/me/` |
| 用户 / 角色 / 菜单 | `/api/users/` `/api/roles/` `/api/menus/` |
| API 同步 | `POST /api/apis/refresh/` |
| Demo | `/api/items/` |

新业务往这里长：

```text
application/modules/<name>/{apis,models,serializers,services}
```

然后挂到 `application/apis.py`，模型登记进 `application/models/__init__.py`。

---

## 配置就这几项

见 [`.env.example`](.env.example)。

| 变量 | 干嘛的 |
| --- | --- |
| `DATABASE_URL` | 库连接（默认 SQLite 可跑） |
| `SECRET_KEY` | JWT 密钥（≥ 32） |
| `REDIS_URL` | 缓存 / token 黑名单（挂了会降级） |
| `AUTO_CREATE_TABLES` | 开发自动建表；生产改 `false` + Alembic |
| `BOOTSTRAP_ADMIN_*` | 首启超管 |

生产迁移：

```bash
# AUTO_CREATE_TABLES=false
make revision m="init"
make migrate
```

---

## 和 fast_generic_api 的分工

```text
fast_generic_api   库：ViewSet / Mixin / Backend
keel               应用：规范、RBAC、工程化、模块骨架
```

Keel **用**它，不 **叫**它的名字。

---

## 鸣谢

- [fast_generic_api](https://github.com/fzf54122/fast_generic_api) — CRUD 引擎  
- [FastAPI](https://fastapi.tiangolo.com/) · [SQLAlchemy](https://www.sqlalchemy.org/) · [Alembic](https://alembic.sqlalchemy.org/)  
- [Django REST framework](https://www.django-rest-framework.org/) — ViewSet 手感的源头  

有用就 Star；也请给 `fast_generic_api` 一颗。

---

## License

[Apache-2.0](LICENSE)
