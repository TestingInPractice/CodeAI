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

SPECS_DIR="$PROJECT/docs/specs"
STATE_DIR="$PROJECT/.build-loop"

if [ ! -d "$SPECS_DIR" ]; then
  echo "Error: $SPECS_DIR does not exist. Run init.sh first."
  exit 1
fi

echo "=== Build Loop: Decompose $PROJECT ==="

# Find spec file (single .md or directory)
SPEC_FILE=""
for f in "$SPECS_DIR"/*.md "$SPECS_DIR"/*.MD; do
  if [ -f "$f" ]; then
    SPEC_FILE="$f"
    break
  fi
done

if [ -z "$SPEC_FILE" ]; then
  echo "Error: no .md files found in $SPECS_DIR"
  exit 1
fi

echo "Spec file: $SPEC_FILE"
echo "Output:    $STATE_DIR/phases.json"

# Run GSD decomposition
echo "Running GSD on $SPEC_FILE..."
npx @opengsd/get-shit-done-redux decompose "$SPEC_FILE" \
  --output "$STATE_DIR/phases.json" 2>&1

# If GSD fails, error with instructions
if [ ! -f "$STATE_DIR/phases.json" ] || [ ! -s "$STATE_DIR/phases.json" ] || grep -q '"phases":\s*\[\]' "$STATE_DIR/phases.json"; then
  echo ""
  echo "Error: GSD produced empty phases.json."
  echo ""
  echo "Install GSD:  npm install -g @opengsd/get-shit-done-redux"
  echo "Or manually write $STATE_DIR/phases.json with your phase decomposition."
  exit 1
fi

echo "=== Decompose complete ==="
echo "Phases written to $STATE_DIR/phases.json"
