#!/bin/bash
# check-agents-links.sh — Validate file references in AGENTS.md
# Usage: bash scripts/check-agents-links.sh
# Exit code: 0 = all references valid, 1 = broken references found

set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)

check_agents_file() {
  local agents_file="$1"
  local broken=0
  local checked=0

  echo "Checking: $agents_file"

  # 1. Backtick-quoted file paths: `path/to/file.ext`
  while IFS= read -r f; do
    case "$f" in
      http*|~/*|/tmp/*|.workflow/*|.opencode/*|.build-loop/*) continue ;;
    esac
    checked=$((checked + 1))
    if [ ! -e "$ROOT/$f" ]; then
      echo "  BROKEN: $f"
      broken=$((broken + 1))
    fi
  done < <(grep -oE '`[a-zA-Z0-9_./-]+\.[a-z]+`' "$agents_file" 2>/dev/null | tr -d '`' | sort -u)

  # 2. Command paths: python3 scripts/... or bash scripts/...
  while IFS= read -r f; do
    checked=$((checked + 1))
    if [ ! -e "$ROOT/$f" ]; then
      echo "  BROKEN: $f"
      broken=$((broken + 1))
    fi
  done < <(grep -oE '(python3|bash) scripts/[A-Za-z0-9_./-]+' "$agents_file" 2>/dev/null | awk '{print $2}' | sort -u)

  echo "  Checked: $checked references"
  if [ "$broken" -eq 0 ]; then
    echo "  PASS — all references valid"
  else
    echo "  FAIL — $broken broken reference(s)"
  fi
  return "$broken"
}

TOTAL_BROKEN=0

# Check root AGENTS.md
if [ -f "$ROOT/AGENTS.md" ]; then
  check_agents_file "$ROOT/AGENTS.md" || TOTAL_BROKEN=$((TOTAL_BROKEN + $?))
fi

# Future: check other AGENTS.md files here

echo ""
if [ "$TOTAL_BROKEN" -eq 0 ]; then
  echo "All AGENTS.md files valid"
  exit 0
else
  echo "$TOTAL_BROKEN broken reference(s) found"
  exit 1
fi
