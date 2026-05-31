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
echo "=== Setup complete ==="
