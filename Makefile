# Makefile for pingstats

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= $(shell grep -m1 '^name' "$(BASEDIR)/pyproject.toml" | sed -e 's/name.*"\(.*\)"/\1/')
APPVER ?= $(shell grep -m1 '^version' "$(BASEDIR)/pyproject.toml" | sed -e 's/version.*"\(.*\)"/\1/')

WITH_VENV := poetry run

################################################################################
.PHONY: all

all: venv preflight build

################################################################################
.PHONY: venv

venv:
	poetry install --sync
	$(WITH_VENV) pre-commit install --install-hooks --overwrite

################################################################################
.PHONY: build-dist

build-dist: preflight
	poetry --no-interaction build

################################################################################
.PHONY: build-image

build-image: preflight
	docker image build --tag "$(APPNAME):dev" "$(BASEDIR)"

################################################################################
.PHONY: build

build: build-dist build-image

################################################################################
.PHONY: github-reltag

github-reltag: preflight
	git tag "v$(APPVER)" main
	git push origin "v$(APPVER)"

################################################################################
.PHONY: image-reltag

image-reltag: preflight build-image
	docker image tag "$(APPNAME):dev" "jheddings/$(APPNAME):latest"
	docker image tag "jheddings/$(APPNAME):latest" "jheddings/$(APPNAME):$(APPVER)"

################################################################################
.PHONY: publish-pypi

publish-pypi: preflight build-dist
	poetry publish --no-interaction

################################################################################
.PHONY: publish-docker

publish-docker: preflight image-reltag
	docker push "jheddings/$(APPNAME):$(APPVER)"
	docker push "jheddings/$(APPNAME):latest"

################################################################################
.PHONY: publish

publish: publish-pypi publish-docker

################################################################################
.PHONY: release

release: publish github-reltag

################################################################################
.PHONY: run

run: venv
	$(WITH_VENV) python3 -m pingstats --config $(BASEDIR)/etc/pingstats.yaml

################################################################################
.PHONY: runc

runc: build-image
	docker container run --rm --tty --publish 9056:9056 "$(APPNAME):dev"

################################################################################
.PHONY: static-checks

static-checks: venv
	$(WITH_VENV) pre-commit run --all-files --verbose

################################################################################
.PHONY: unit-tests

unit-tests: venv
	$(WITH_VENV) coverage run "--source=$(SRCDIR)" -m pytest "$(BASEDIR)/tests"

################################################################################
.PHONY: coverage-report

coverage-report: venv unit-tests
	$(WITH_VENV) coverage report

################################################################################
.PHONY: coverage-html

coverage-html: venv unit-tests
	$(WITH_VENV) coverage html

################################################################################
.PHONY: coverage

coverage: coverage-report coverage-html

################################################################################
.PHONY: preflight

preflight: static-checks unit-tests coverage-report

################################################################################
.PHONY: clean

clean:
	rm -f "$(BASEDIR)/.coverage"
	rm -Rf "$(BASEDIR)/.pytest_cache"
	find "$(BASEDIR)" -name "*.pyc" -print | xargs rm -f
	find "$(BASEDIR)" -name '__pycache__' -print | xargs rm -Rf
	docker image rm "$(APPNAME):dev" 2>/dev/null || true

################################################################################
.PHONY: clobber

clobber: clean
	$(WITH_VENV) pre-commit uninstall || true
	rm -Rf "$(BASEDIR)/htmlcov"
	rm -Rf "$(BASEDIR)/dist"
	rm -Rf "$(BASEDIR)/.venv"
	docker image rm "$(APPNAME):latest" 2>/dev/null || true
	docker image rm "$(APPNAME):$(APPVER)" 2>/dev/null || true
