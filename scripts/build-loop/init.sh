#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path>"
  exit 1
}

PROJECT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p) PROJECT="$2"; shift 2 ;;
    *) usage ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "Error: --project is required"
  usage
fi

if [ ! -d "$PROJECT" ]; then
  echo "Error: project directory $PROJECT does not exist"
  exit 1
fi

echo "=== Build Loop: Init $PROJECT ==="

# State directory
mkdir -p "$PROJECT/.build-loop"

# docs/specs/ — only if not exists (user writes their 1 file there)
if [ ! -d "$PROJECT/docs/specs" ]; then
  echo "Creating docs/specs/ skeleton..."
  mkdir -p "$PROJECT/docs/specs/contracts"

  cat > "$PROJECT/docs/specs/goals.md" << 'GOALS'
# Project Goals

> Опишите цели проекта, пользовательские потребности и tech stack.

GOALS

  cat > "$PROJECT/docs/specs/contracts/api.md" << 'API'
# API Contracts

> Опишите эндпоинты: метод, путь, тело запроса, ответ.

API

  cat > "$PROJECT/docs/specs/contracts/data-models.md" << 'MODELS'
# Data Models

> Опишите сущности: поля, типы, связи.

MODELS

  cat > "$PROJECT/docs/specs/acceptance-criteria.md" << 'AC'
# Acceptance Criteria

> Опишите проверяемые условия для done.
> Формат: - [ ] условие

AC

  echo "  docs/specs/ skeleton created — fill the files with your project description"
else
  echo "  docs/specs/ already exists"
fi

# phases.json stub
if [ ! -f "$PROJECT/.build-loop/phases.json" ]; then
  echo '{"phases":[]}' > "$PROJECT/.build-loop/phases.json"
  echo "  .build-loop/phases.json initialized"
fi

# AGENTS.md for the project — tells OpenCode to run Build Loop
if [ ! -f "$PROJECT/AGENTS.md" ]; then
  cat > "$PROJECT/AGENTS.md" << 'AGENTS'
# Build Loop project

You are a Build Loop orchestrator. Work in this project only.

## Workflow

1. Read `docs/specs/` — understand goals, contracts, acceptance criteria
2. If `.build-loop/phases.json` is empty, run GSD to decompose specs into phases
3. Execute Ralph Loop: for each pending phase, generate a prompt from `docs/specs/`,
   delegate to a sub-agent, verify, and update `.build-loop/phases.json`
4. When all phases complete — report summary

## Source of Truth

The only source of truth is `docs/specs/`. Never invent requirements outside it.
AGENTS
  echo "  AGENTS.md created"
fi

# .gitignore for build artifacts
if [ ! -f "$PROJECT/.gitignore" ]; then
  cat > "$PROJECT/.gitignore" << 'GITIGNORE'
.build-loop/
GITIGNORE
  echo "  .gitignore created"
fi

echo "=== Init complete ==="
