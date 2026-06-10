#!/bin/bash
# add-frontmatter.sh — Add frontmatter (tags, aliases) to thesis files
set -e

DOCS="scripts/build-loop/docs"

add_frontmatter() {
  local file="$1"
  local tags="$2"
  local aliases="$3"

  # Skip if already has frontmatter
  if head -1 "$file" 2>/dev/null | grep -q '^---$'; then
    echo "  SKIP $file (has frontmatter)"
    return
  fi

  # Get first line (title)
  title=$(head -1 "$file" 2>/dev/null | sed 's/^# //;s/ — .*//')

  # Prepend frontmatter
  tmp=$(mktemp)
  {
    echo "---"
    echo "tags: [$tags]"
    echo "aliases: [$aliases]"
    echo "---"
    cat "$file"
  } > "$tmp"
  mv "$tmp" "$file"
  echo "  ADDED frontmatter: $(basename $file)"
}

echo "=== Adding frontmatter to thesis files ==="

# 01-frameworks
add_frontmatter "$DOCS/01-frameworks/2025-06-07_AI-news-digest-thesis.md" "ai-news, дайджест" "AI News Digest тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md" "gsd, paul" "GSD vs Paul тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_DOTI-thesis.md" "doti" "DOTI тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers-thesis.md" "gsd, superpowers" "GSD Superpowers тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md" "gsd, opencode" "GSD for OpenCode тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md" "gsd, openspec" "GSD vs OpenSpec тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-AI-code-unsupportable-thesis.md" "ai-code, best-practices" "AI Code Unsupportable тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-LLM-better-than-you-thesis.md" "llm-config, prompt-engineering" "LLM Better Than You тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-polyakov-test-generation-thesis.md" "test-generation, rag" "Polyakov Test Generation тезисы"
add_frontmatter "$DOCS/01-frameworks/2025-vitaly-kharisov-ai-frontend-thesis.md" "ai-code, фронтенд" "Kharisov AI Frontend тезисы"

# 02-mcp
add_frontmatter "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md" "mcp, mcp-tools" "MCP Tools Telegram Watcher тезисы"

# 03-opencode-config
add_frontmatter "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md" "opencode, agents-md, claude-md" "AGENTS CLAUDE howto тезисы"

# 04-best-practices
add_frontmatter "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md" "best-practices, eval-driven" "AI Products Systematic Improvement тезисы"
add_frontmatter "$DOCS/04-best-practices/2025-07-26_Hermes-agent-thesis.md" "best-practices, hermes" "Hermes Agent тезисы"
add_frontmatter "$DOCS/04-best-practices/2025-LLM-testing-guide-thesis.md" "best-practices, llm-testing" "LLM Testing Guide тезисы"
add_frontmatter "$DOCS/04-best-practices/2026-02-12_Context-Engineering-thesis.md" "context-engineering, best-practices" "Context Engineering тезисы"

echo ""
echo "=== Done ==="
