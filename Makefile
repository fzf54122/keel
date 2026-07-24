.DEFAULT_GOAL := help
SHELL := /bin/bash

APP ?= application:app
HOST ?= 0.0.0.0
PORT ?= 8000
CELERY_APP ?= application.celery_app.celery

HAS_UV := $(shell command -v uv >/dev/null 2>&1 && echo 1 || echo 0)
ifeq ($(HAS_UV),1)
	RUN := uv run
	INSTALL := uv sync --group dev
else
	RUN := python
	INSTALL := python -m pip install -e ".[dev]"
endif

.PHONY: help install run run-reload test lint fmt migrate revision \
        docker-up docker-down celery-worker celery-beat celery-flower module new

help:
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安装依赖
	$(INSTALL)

new: ## 用 Copier 从本脚手架创建项目: make new name=my-api [dest=../my-api]
	@test -n "$(name)" || (echo "usage: make new name=my-api [dest=../my-api]" && exit 1)
	@dest="$(if $(dest),$(dest),../$(name))"; \
	if command -v uvx >/dev/null 2>&1; then \
	  uvx --from copier copier copy --trust --defaults \
	    --data project_name=$(name) \
	    . "$$dest"; \
	elif command -v copier >/dev/null 2>&1; then \
	  copier copy --trust --defaults \
	    --data project_name=$(name) \
	    . "$$dest"; \
	else \
	  echo "need uvx or copier: pipx install copier  /  uv tool install copier"; \
	  exit 1; \
	fi

run: ## 启动 API
	$(RUN) uvicorn $(APP) --host $(HOST) --port $(PORT)

run-reload: ## 热重载 API
	$(RUN) uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

test: ## 运行测试
	$(RUN) pytest -q

lint: ## ruff check
	$(RUN) ruff check .

fmt: ## ruff format
	$(RUN) ruff format .

migrate: ## alembic upgrade head
	$(RUN) alembic upgrade head

revision: ## alembic revision --autogenerate -m "msg"
	$(RUN) alembic revision --autogenerate -m "$(m)"

docker-up: ## 启动 postgres/redis
	docker compose up -d

docker-down: ## 停止依赖服务
	docker compose down

celery-worker: ## 启动 Celery worker
	$(RUN) celery -A $(CELERY_APP) worker -l info

celery-beat: ## 启动 Celery beat
	$(RUN) celery -A $(CELERY_APP) beat -l info

celery-flower: ## 启动 Flower 监控（可选）
	$(RUN) celery -A $(CELERY_APP) flower

module: ## 生成业务模块: make module name=order
	@test -n "$(name)" || (echo "usage: make module name=order" && exit 1)
	$(RUN) python scripts/new_module.py $(name)
