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

# Run GSD decomposition
echo "Running GSD on $SPECS_DIR..."
npx @opengsd/get-shit-done-redux decompose "$SPECS_DIR" \
  --output "$STATE_DIR/phases.json"

echo "=== Decompose complete ==="
echo "Phases written to $STATE_DIR/phases.json"
