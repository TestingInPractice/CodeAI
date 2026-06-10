#!/bin/bash
# add-wikilinks.sh — Link transcript ↔ thesis pairs
# Run from repo root
set -e

DOCS="scripts/build-loop/docs"

link_pair() {
  local file_a="$1"
  local name_a="$2"
  local file_b="$3"
  local name_b="$4"

  # Add link to file_a → file_b
  if ! grep -q "\[\[$name_b\]\]" "$file_a" 2>/dev/null; then
    echo "" >> "$file_a"
    echo "---" >> "$file_a"
    echo "" >> "$file_a"
    echo "**↪️ $name_b:** [[$name_b]]" >> "$file_a"
    echo "  linked $name_a → $name_b"
  fi

  # Add link to file_b → file_a
  if ! grep -q "\[\[$name_a\]\]" "$file_b" 2>/dev/null; then
    echo "" >> "$file_b"
    echo "---" >> "$file_b"
    echo "" >> "$file_b"
    echo "**↪️ $name_a:** [[$name_a]]" >> "$file_b"
    echo "  linked $name_b → $name_a"
  fi
}

echo "=== Linking transcript ↔ thesis ==="

# 01-frameworks
link_pair "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul.md" "2025-06-07_GSD-vs-Paul" \
          "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md" "2025-06-07_GSD-vs-Paul-thesis"

link_pair "$DOCS/01-frameworks/2025-07-26_DOTI.md" "2025-07-26_DOTI" \
          "$DOCS/01-frameworks/2025-07-26_DOTI-thesis.md" "2025-07-26_DOTI-thesis"

link_pair "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers.md" "2025-07-26_GSD-Superpowers" \
          "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers-thesis.md" "2025-07-26_GSD-Superpowers-thesis"

link_pair "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode.md" "2025-07-26_GSD-for-OpenCode" \
          "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md" "2025-07-26_GSD-for-OpenCode-thesis"

link_pair "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec.md" "2025-07-26_GSD-vs-OpenSpec" \
          "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md" "2025-07-26_GSD-vs-OpenSpec-thesis"

# 02-mcp
link_pair "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher.md" "2025-06-07_MCP-tools-telegram-watcher" \
          "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md" "2025-06-07_MCP-tools-telegram-watcher-thesis"

# 03-opencode-config
link_pair "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto.md" "2025-06-07_AGENTS-CLAUDE-howto" \
          "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md" "2025-06-07_AGENTS-CLAUDE-howto-thesis"

# 04-best-practices
link_pair "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement.md" "2025-07-26_AI-products-systematic-improvement" \
          "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md" "2025-07-26_AI-products-systematic-improvement-thesis"

link_pair "$DOCS/04-best-practices/2025-07-26_Hermes-agent.md" "2025-07-26_Hermes-agent" \
          "$DOCS/04-best-practices/2025-07-26_Hermes-agent-thesis.md" "2025-07-26_Hermes-agent-thesis"

link_pair "$DOCS/04-best-practices/2025-LLM-testing-guide.md" "2025-LLM-testing-guide" \
          "$DOCS/04-best-practices/2025-LLM-testing-guide-thesis.md" "2025-LLM-testing-guide-thesis"

link_pair "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend.md" "2025-vitaly-kharisov-ai-frontend" \
          "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend-thesis.md" "2025-vitaly-kharisov-ai-frontend-thesis"

link_pair "$DOCS/04-best-practices/2025-polyakov-test-generation.md" "2025-polyakov-test-generation" \
          "$DOCS/04-best-practices/2025-polyakov-test-generation-thesis.md" "2025-polyakov-test-generation-thesis"

link_pair "$DOCS/04-best-practices/2025-LLM-better-than-you.md" "2025-LLM-better-than-you" \
          "$DOCS/04-best-practices/2025-LLM-better-than-you-thesis.md" "2025-LLM-better-than-you-thesis"

link_pair "$DOCS/04-best-practices/2025-AI-code-unsupportable.md" "2025-AI-code-unsupportable" \
          "$DOCS/04-best-practices/2025-AI-code-unsupportable-thesis.md" "2025-AI-code-unsupportable-thesis"

# 07-articles
link_pair "$DOCS/07-articles/2025-06-07_AI-news-digest.md" "2025-06-07_AI-news-digest" \
          "$DOCS/07-articles/2025-06-07_AI-news-digest-thesis.md" "2025-06-07_AI-news-digest-thesis"

echo ""
echo "=== Linking paired files to MOCs ==="

add_moc_link_to_pair() {
  local file="$1"
  local moc_path="$2"
  if ! grep -q "\[\[$moc_path\]\]" "$file" 2>/dev/null; then
    echo "" >> "$file"
    echo "**↪️ Категория:** [[$moc_path]]" >> "$file"
    echo "  linked $file → $moc_path"
  fi
}

add_moc_link_to_pair "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_DOTI.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_DOTI-thesis.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers-thesis.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec.md" "../01-frameworks/README"
add_moc_link_to_pair "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md" "../01-frameworks/README"

add_moc_link_to_pair "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher.md" "../02-mcp/README"
add_moc_link_to_pair "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md" "../02-mcp/README"

add_moc_link_to_pair "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto.md" "../03-opencode-config/README"
add_moc_link_to_pair "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md" "../03-opencode-config/README"

add_moc_link_to_pair "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-07-26_Hermes-agent.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-07-26_Hermes-agent-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-LLM-testing-guide-transcript.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-LLM-testing-guide-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-polyakov-test-generation.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-polyakov-test-generation-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-LLM-better-than-you.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-LLM-better-than-you-thesis.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-AI-code-unsupportable.md" "../04-best-practices/README"
add_moc_link_to_pair "$DOCS/04-best-practices/2025-AI-code-unsupportable-thesis.md" "../04-best-practices/README"

add_moc_link_to_pair "$DOCS/07-articles/2025-06-07_AI-news-digest.md" "../07-articles/README"
add_moc_link_to_pair "$DOCS/07-articles/2025-06-07_AI-news-digest-thesis.md" "../07-articles/README"

echo ""
echo "=== Done ==="
