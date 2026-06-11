#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> [--setup-only] [--decompose-only] [--run-only] [--status] [--judge]"
  exit 1
}

PROJECT=""
MODE="full"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p)     PROJECT="$2"; shift 2 ;;
    --setup-only)     MODE="setup"; shift ;;
    --decompose-only)  MODE="decompose"; shift ;;
    --run-only)       MODE="run"; shift ;;
    --status)         MODE="status"; shift ;;
    --judge)          MODE="judge"; shift ;;
    *) usage ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "Error: --project is required"
  usage
fi

BUILD_LOOP_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔═══════════════════════════════════════════════╗"
echo "║        Build Loop — Full Pipeline             ║"
echo "╚═══════════════════════════════════════════════╝"
echo "Project: $PROJECT"
echo "Mode:    $MODE"
echo ""

case "$MODE" in
  setup)
    bash "$BUILD_LOOP_DIR/setup.sh"
    bash "$BUILD_LOOP_DIR/init.sh" --project "$PROJECT"
    ;;
  decompose)
    bash "$BUILD_LOOP_DIR/decompose.sh" --project "$PROJECT"
    echo ""
    echo "Next:"
    echo "  bash $BUILD_LOOP_DIR/next-phase.sh --project \"$PROJECT\""
    ;;
  run)
    bash "$BUILD_LOOP_DIR/run-loop.sh" --project "$PROJECT"
    ;;
  status)
    bash "$BUILD_LOOP_DIR/run-loop.sh" --project "$PROJECT"
    ;;
  judge)
    echo "Running judge on next pending phase..."
    next=$("$BUILD_LOOP_DIR/next-phase.sh" --project "$PROJECT" 2>/dev/null | grep "ID:" | awk '{print $NF}')
    if [ -z "$next" ]; then
      echo "No pending phases found."
      exit 0
    fi
    summary_file="/tmp/p${next}-summary.txt"
    if [ ! -f "$summary_file" ]; then
      echo "Summary file not found: $summary_file"
      echo "Phase $next was not implemented yet — run --run-only first."
      exit 1
    fi
    bash "$BUILD_LOOP_DIR/run-loop.sh" --project "$PROJECT" --judge --phase "$next" --summary "$summary_file"
    ;;
  full)
    bash "$BUILD_LOOP_DIR/setup.sh"
    bash "$BUILD_LOOP_DIR/init.sh" --project "$PROJECT"
    echo ""
    echo "=== Edit docs/specs/ in $PROJECT ==="
    echo "Write your project description, then re-run with --decompose-only"
    echo ""
    echo "  $0 --project $PROJECT --decompose-only"
    echo "  $0 --project $PROJECT --run-only"
    ;;
esac

echo ""
echo "=== Build Loop done ==="
