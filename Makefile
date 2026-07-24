.DEFAULT_GOAL := help
SHELL := /bin/bash

APP ?= application:app
HOST ?= 0.0.0.0
PORT ?= 8000

HAS_UV := $(shell command -v uv >/dev/null 2>&1 && echo 1 || echo 0)
ifeq ($(HAS_UV),1)
	RUN := uv run
	INSTALL := uv sync --group dev
else
	RUN := python
	INSTALL := python -m pip install -e ".[dev]"
endif

.PHONY: help install run run-reload test lint fmt migrate revision docker-up docker-down

help:
	@awk 'BEGIN {FS=":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安装依赖
	$(INSTALL)

run: ## 启动服务
	$(RUN) uvicorn $(APP) --host $(HOST) --port $(PORT)

run-reload: ## 热重载启动
	$(RUN) uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

test: ## 运行测试
	$(RUN) pytest -q

lint: ## ruff check
	$(RUN) ruff check .

fmt: ## ruff format
	$(RUN) ruff format .

migrate: ## alembic upgrade head
	$(RUN) alembic upgrade head

revision: ## alembic revision --autogenerate -m "msg"  (make revision m="init")
	$(RUN) alembic revision --autogenerate -m "$(m)"

docker-up: ## 启动 postgres/redis
	docker compose up -d

docker-down: ## 停止依赖服务
	docker compose down
