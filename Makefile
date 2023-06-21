# Makefile for pingdat

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= $(shell grep -m1 '^name' "$(BASEDIR)/pyproject.toml" | sed -e 's/name.*"\(.*\)"/\1/')
APPVER ?= $(shell grep -m1 '^version' "$(BASEDIR)/pyproject.toml" | sed -e 's/version.*"\(.*\)"/\1/')

WITH_VENV := poetry run
PLATFORMS ?= linux/amd64,linux/arm64,linux/arm/v7


.PHONY: all
all: venv preflight build


.PHONY: venv
venv:
	poetry install --sync --no-interaction
	$(WITH_VENV) pre-commit install --install-hooks --overwrite


poetry.lock: venv
	poetry lock --no-update --no-interaction


.PHONY: buildx
buildx:
	docker buildx create --use --name $(APPNAME)-buildx


.PHONY: build-dist
build-dist: preflight
	poetry build --no-interaction


.PHONY: build-image
build-image: preflight buildx
	docker image build --tag "$(APPNAME):dev" "$(BASEDIR)"


.PHONY: build
build: build-dist build-image


.PHONY: publish-pypi
publish-pypi: preflight build-dist
	poetry publish --no-interaction


.PHONY: publish-docker
publish-docker: preflight buildx
	docker buildx build --push --platform $(PLATFORMS) \
		--tag "$(APPNAME):$(APPVER)" --tag "$(APPNAME):latest" \
		"$(BASEDIR)"


.PHONY: publish
publish: publish-pypi publish-docker


.PHONY: release
release: publish
	git tag "v$(APPVER)" main
	git push origin "v$(APPVER)"


.PHONY: run
run: venv
	$(WITH_VENV) python3 -m pingdat --config $(BASEDIR)/etc/pingdat.yaml


.PHONY: runc
runc: build-image
	docker container run --rm --tty --publish 9056:9056 "$(APPNAME):dev"


.PHONY: static-checks
static-checks: venv
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


.PHONY: preflight
preflight: static-checks unit-tests coverage-report


.PHONY: clean
clean:
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	find "$(BASEDIR)" -name "*.pyc" -print | xargs rm -f
	find "$(BASEDIR)" -name '__pycache__' -print | xargs rm -Rf
	docker image rm "$(APPNAME):dev" 2>/dev/null || true


.PHONY: clobber
clobber: clean
	$(WITH_VENV) pre-commit uninstall || true
	rm -Rf "$(BASEDIR)/htmlcov"
	rm -Rf "$(BASEDIR)/dist"
	poetry env remove --all --no-interaction
	docker image rm "$(APPNAME):latest" 2>/dev/null || true
	docker image rm "$(APPNAME):$(APPVER)" 2>/dev/null || true
