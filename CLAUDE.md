# CLAUDE.md — pingdat

## Overview

pingdat is a network monitoring tool that pings configured hosts and exports
metrics to Prometheus. It runs as a long-lived service, typically in Docker.

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`

Scope is optional but encouraged (e.g. `fix(metrics): ...`, `feat(config): ...`).

Include the issue number when applicable (e.g. `feat: add jitter metric (#10)`).

## Branch Naming

Use the same type prefixes as commits, followed by a short description:

```
<type>/<short-description>
```

Examples: `feat/jitter-metric`, `fix/timeout-handling`, `chore/update-deps`
