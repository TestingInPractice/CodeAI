#!/usr/bin/env bash
set -euo pipefail

BUILD_LOOP_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Build Loop: Setup ==="

echo ""
echo "--- GStack ---"
if command -v gstack &>/dev/null || [ -d "$HOME/.claude/skills/gstack" ]; then
  echo "GStack already installed"
else
  echo "Installing GStack..."
  git clone --single-branch --depth 1 \
    https://github.com/garrytan/gstack.git "$HOME/.claude/skills/gstack"
  cd "$HOME/.claude/skills/gstack"
  ./setup --host opencode
  echo "GStack installed"
fi

echo ""
echo "--- GSD ---"
if command -v gsd &>/dev/null; then
  echo "GSD already installed"
else
  echo "Installing GSD..."
  npx @opengsd/get-shit-done-redux@latest --profile=core
  echo "GSD installed"
fi

echo ""
echo "--- Superpowers ---"
if grep -q "superpowers" "$HOME/.config/opencode/opencode.json" 2>/dev/null; then
  echo "Superpowers plugin already registered"
else
  echo ""
  echo "To enable Superpowers, add to your opencode.json:"
  echo ""
  echo '  {'
  echo '    "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]'
  echo '  }'
  echo ""
fi

echo ""
echo "--- Verifying Mode C tools ---"
GSTACK_OK=false
GSD_OK=false
command -v gstack &>/dev/null && GSTACK_OK=true && echo "  GStack: OK"
command -v gstack &>/dev/null || echo "  GStack: not found (install manually or re-run setup)"
command -v gsd &>/dev/null && GSD_OK=true && echo "  GSD: OK"
command -v gsd &>/dev/null || echo "  GSD: not found (npx @opengsd/get-shit-done-redux)"
if [ -f "$HOME/.config/opencode/opencode.json" ]; then
  echo "  opencode config: found"
else
  echo "  opencode config: not found"
fi
# Verify transition.py exists
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SCRIPT_DIR/transition.py" ]; then
  echo "  transition.py: OK"
fi
if [ -f "$SCRIPT_DIR/workflow/run-task.sh" ]; then
  echo "  run-task.sh: OK"
fi

echo ""
echo "=== Setup complete ==="
