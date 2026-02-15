# Makefile for pingdat

# use a local.env file if it exists
-include local.env

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= $(shell grep -m1 '^name' "$(BASEDIR)/pyproject.toml" | sed -e 's/name.*"\(.*\)"/\1/')
APPVER ?= $(shell grep -m1 '^version' "$(BASEDIR)/pyproject.toml" | sed -e 's/version.*"\(.*\)"/\1/')

WITH_VENV := uv run

# for using API keys from environment variables
export


.PHONY: all
all: venv preflight build


.PHONY: venv
venv:
	uv sync --all-extras
	$(WITH_VENV) pre-commit install --install-hooks --overwrite


uv.lock: venv
	uv lock


.PHONY: tidy
tidy: venv uv.lock
	$(WITH_VENV) ruff format "$(SRCDIR)" "$(BASEDIR)/tests"
	$(WITH_VENV) ruff check --fix "$(SRCDIR)" "$(BASEDIR)/tests"
	$(WITH_VENV) pyright "$(SRCDIR)" "$(BASEDIR)/tests"


.PHONY: build-dist
build-dist: preflight
	uv build


.PHONY: build-image
build-image: preflight
	docker image build --tag "$(APPNAME):dev" "$(BASEDIR)"


.PHONY: build
build: build-dist build-image


.PHONY: release
release: preflight
	git tag "v$(APPVER)" main
	git push origin "v$(APPVER)"


.PHONY: run
run: venv
	$(WITH_VENV) python3 -m pingdat --config $(BASEDIR)/local.yaml


.PHONY: runc
runc: build-image
	docker container run --rm --tty --publish 9056:9056 \
		--volume "$(BASEDIR):/opt/pingdat" \
		"$(APPNAME):dev" --config=/opt/pingdat/local.yaml


.PHONY: precommit
precommit: venv
	$(WITH_VENV) pre-commit run --all-files --verbose


.PHONY: unit-tests
unit-tests: venv
	$(WITH_VENV) coverage run "--source=$(SRCDIR)" -m pytest "$(BASEDIR)/tests"


.PHONY: coverage-report
coverage-report: venv unit-tests
	$(WITH_VENV) coverage report


.PHONY: coverage-html
coverage-html: venv unit-tests
	$(WITH_VENV) coverage html


.PHONY: coverage
coverage: coverage-report coverage-html


.PHONY: test
test: unit-tests


.PHONY: preflight
preflight: precommit unit-tests


.PHONY: clean
clean:
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	rm -Rf "$(BASEDIR)/.ruff_cache"
	find "$(BASEDIR)" -name "*.pyc" -print | xargs rm -f
	find "$(BASEDIR)" -name '__pycache__' -print | xargs rm -Rf
	docker image rm "$(APPNAME):dev" 2>/dev/null || true


.PHONY: clobber
clobber: clean
	$(WITH_VENV) pre-commit uninstall || true
	rm -Rf "$(BASEDIR)/htmlcov"
	rm -Rf "$(BASEDIR)/dist"
	rm -Rf "$(BASEDIR)/.venv"
	find "$(BASEDIR)" -name "*.log" -print | xargs rm -f
	docker image rm "$(APPNAME):latest" 2>/dev/null || true
	docker image rm "$(APPNAME):$(APPVER)" 2>/dev/null || true
