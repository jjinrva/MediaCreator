SHELL := /bin/bash

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
NODE_VERSION := 22.22.2
NODE_DIST := node-v$(NODE_VERSION)-linux-x64
NODE_ROOT := $(ROOT_DIR)/infra/node/$(NODE_DIST)
NODE_BIN := $(NODE_ROOT)/bin/node
NPM_BIN := $(NODE_ROOT)/bin/npm
PNPM_ROOT := $(ROOT_DIR)/infra/pnpm
PNPM_CLI := $(PNPM_ROOT)/node_modules/pnpm/bin/pnpm.cjs
API_VENV := $(ROOT_DIR)/apps/api/.venv
API_PYTHON := $(API_VENV)/bin/python
WORKER_VENV := $(ROOT_DIR)/apps/worker/.venv
WORKER_PYTHON := $(WORKER_VENV)/bin/python
PLAYWRIGHT_BROWSERS_PATH := $(ROOT_DIR)/infra/playwright
COMPOSE_FILE := $(ROOT_DIR)/infra/docker-compose.yml

.PHONY: help install bootstrap toolchain pnpm-install bootstrap-api bootstrap-worker lint typecheck test-api test-web smoke-api smoke-web dev api web dev-api dev-web worker

help:
	@printf '%s\n' \
		'bootstrap         Bootstrap local toolchains and Python environments.' \
		'dev               Start PostgreSQL, then run API, web, and worker from source.' \
		'api               Run the FastAPI app from source.' \
		'web               Run the Next.js app from source.' \
		'worker            Run the worker bootstrap entrypoint.' \
		'lint              Run minimal lint checks for web, API, and worker.' \
		'typecheck         Run TypeScript and Python type checks.' \
		'test-api          Run targeted API tests.' \
		'test-web          Run targeted web unit and Playwright smoke tests.'

install: toolchain pnpm-install bootstrap-api bootstrap-worker
bootstrap: install

toolchain: $(NODE_BIN) $(PNPM_CLI)

$(NODE_BIN):
	@mkdir -p "$(ROOT_DIR)/infra/node"
	@curl -fsSL "https://nodejs.org/dist/v$(NODE_VERSION)/$(NODE_DIST).tar.xz" -o "$(ROOT_DIR)/infra/node/$(NODE_DIST).tar.xz"
	@tar -xJf "$(ROOT_DIR)/infra/node/$(NODE_DIST).tar.xz" -C "$(ROOT_DIR)/infra/node"
	@rm -f "$(ROOT_DIR)/infra/node/$(NODE_DIST).tar.xz"

$(PNPM_CLI): $(NODE_BIN)
	@mkdir -p "$(PNPM_ROOT)"
	@PATH="$(NODE_ROOT)/bin:$$PATH" "$(NPM_BIN)" install --prefix "$(PNPM_ROOT)" pnpm@9.15.4

pnpm-install: toolchain
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" pnpm install

bootstrap-api:
	@python3 -m venv "$(API_VENV)"
	@"$(API_PYTHON)" -m pip install --upgrade pip
	@cd "$(ROOT_DIR)/apps/api" && "$(API_PYTHON)" -m pip install -e '.[dev]'

bootstrap-worker:
	@python3 -m venv "$(WORKER_VENV)"
	@"$(WORKER_PYTHON)" -m pip install --upgrade pip
	@cd "$(ROOT_DIR)/apps/worker" && "$(WORKER_PYTHON)" -m pip install -e '.[dev]'

lint:
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" pnpm --dir "$(ROOT_DIR)/apps/web" lint
	@cd "$(ROOT_DIR)/apps/api" && "$(API_VENV)/bin/ruff" check app tests
	@cd "$(ROOT_DIR)/apps/worker" && "$(WORKER_VENV)/bin/ruff" check src

typecheck:
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" pnpm --dir "$(ROOT_DIR)/packages/shared-types" typecheck
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" pnpm --dir "$(ROOT_DIR)/apps/web" typecheck
	@cd "$(ROOT_DIR)/apps/api" && "$(API_VENV)/bin/mypy" app tests
	@cd "$(ROOT_DIR)/apps/worker" && "$(WORKER_VENV)/bin/mypy" src

test-api:
	@bash "$(ROOT_DIR)/scripts/test_api.sh"

test-web:
	@bash "$(ROOT_DIR)/scripts/test_web.sh"

smoke-api: test-api

smoke-web:
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" PLAYWRIGHT_BROWSERS_PATH="$(PLAYWRIGHT_BROWSERS_PATH)" pnpm --dir "$(ROOT_DIR)/apps/web" exec playwright install chromium
	@PATH="$(ROOT_DIR)/infra/bin:$$PATH" PLAYWRIGHT_BROWSERS_PATH="$(PLAYWRIGHT_BROWSERS_PATH)" pnpm --dir "$(ROOT_DIR)/apps/web" test:e2e

dev:
	@bash "$(ROOT_DIR)/scripts/dev.sh"

api:
	@bash "$(ROOT_DIR)/scripts/run-api.sh"

web:
	@bash "$(ROOT_DIR)/scripts/run-web.sh"

dev-api: api

dev-web: web

worker:
	@bash "$(ROOT_DIR)/scripts/run_worker.sh"
