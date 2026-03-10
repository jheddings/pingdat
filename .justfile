# justfile for pingdat

basedir := justfile_directory()
srcdir := basedir / "src"

appname := "pingdat"
appver := `uv version --short`

# run venv setup and preflight checks
default: setup preflight

# setup the local development environment
setup: venv
  uv run pre-commit install --install-hooks --overwrite

# sync the virtual environment
venv:
  uv sync --all-extras

# auto-format, lint-fix
tidy: setup
  uv run ruff format "{{srcdir}}" "{{basedir}}/tests"
  uv run ruff check --fix "{{srcdir}}" "{{basedir}}/tests"

# run all static checks
check: setup
  uv run ruff format --check "{{srcdir}}" "{{basedir}}/tests"
  uv run ruff check "{{srcdir}}" "{{basedir}}/tests"
  uv run pyright "{{srcdir}}" "{{basedir}}/tests"

# run unit tests
test: setup
  uv run coverage run "--source={{srcdir}}" -m pytest "{{basedir}}/tests"

# full static checks and unit tests
preflight: check test

# run pingdat from source
run *args: setup
  uv run python3 -m pingdat --config "{{basedir}}/local.yaml" {{args}}

# generate coverage reports
coverage: test
  uv run coverage report
  uv run coverage html

# build distribution packages
build-dist: preflight
  uv build

# build Docker image
build-image: preflight
  docker image build --tag "{{appname}}:dev" "{{basedir}}"

# run in Docker container
runc: build-image
  docker container run --rm --tty --publish 9056:9056 \
    --volume "{{basedir}}:/opt/pingdat" \
    "{{appname}}:dev" --config=/opt/pingdat/local.yaml

# verify no uncommitted changes to tracked files
repo-guard:
  test -z "$(git status --porcelain -uno)" || (echo "ERROR: working tree is dirty"; exit 1)

# bump version, commit, tag, and push
release bump="patch": preflight repo-guard
  #!/usr/bin/env bash
  uv version --bump {{bump}}
  VERSION=$(uv version --short)
  git add pyproject.toml uv.lock
  git commit -m "bump version to $VERSION"
  git tag -a "v$VERSION" -m "v$VERSION"
  git push && git push --tags

# remove caches and compiled files
clean:
  rm -f "{{basedir}}/.coverage"
  rm -rf "{{basedir}}/.pytest_cache"
  rm -rf "{{basedir}}/.ruff_cache"
  find "{{basedir}}" -name "*.pyc" -delete
  find "{{basedir}}" -name "__pycache__" -type d -exec rm -rf {} +
  docker image rm "{{appname}}:dev" 2>/dev/null || true

# remove everything including venv and dist
clobber: clean
  uv run pre-commit uninstall || true
  rm -rf "{{basedir}}/htmlcov"
  rm -rf "{{basedir}}/dist"
  rm -rf "{{basedir}}/.venv"
  find "{{basedir}}" -name "*.log" -delete
  docker image rm "{{appname}}:latest" 2>/dev/null || true
  docker image rm "{{appname}}:{{appver}}" 2>/dev/null || true
