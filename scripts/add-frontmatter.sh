#!/bin/bash
# add-frontmatter.sh — Add frontmatter (tags, aliases, date, version, source) to thesis files
set -e

DOCS="scripts/build-loop/docs"

add_frontmatter() {
  local file="$1"
  local tags="$2"
  local aliases="$3"
  local date="$4"
  local version="$5"
  local source="$6"

  # Skip if already has frontmatter
  if head -1 "$file" 2>/dev/null | grep -q '^---$'; then
    echo "  SKIP $file (has frontmatter)"
    return
  fi

  # Prepend frontmatter
  tmp=$(mktemp)
  {
    echo "---"
    echo "tags: [$tags]"
    echo "aliases: [$aliases]"
    [ -n "$date" ] && echo "date: $date"
    [ -n "$version" ] && echo "version: $version"
    [ -n "$source" ] && echo "source: $source"
    echo "---"
    echo ""
    echo "> **Дата:** ${date:-}"
    echo "> **Версия:** ${version:-1.0}"
    echo "> **Источник:** [[${source:-}]]"
    echo "> **Библиография:** [[../bibliography|Библиография]]"
    echo ""
    cat "$file"
  } > "$tmp"
  mv "$tmp" "$file"
  echo "  ADDED frontmatter: $(basename $file)"
}

echo "=== Adding frontmatter to thesis files ==="

# 01-frameworks
add_frontmatter "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md" "gsd, paul" "GSD vs Paul тезисы" "2025-06-07" "1.0" "2025-06-07_GSD-vs-Paul"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_DOTI-thesis.md" "doti" "DOTI тезисы" "2025-07-26" "1.0" "2025-07-26_DOTI"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers-thesis.md" "gsd, superpowers" "GSD Superpowers тезисы" "2025-07-26" "1.0" "2025-07-26_GSD-Superpowers"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md" "gsd, opencode" "GSD for OpenCode тезисы" "2025-07-26" "1.0" "2025-07-26_GSD-for-OpenCode"
add_frontmatter "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md" "gsd, openspec" "GSD vs OpenSpec тезисы" "2025-07-26" "1.0" "2025-07-26_GSD-vs-OpenSpec"

# 02-mcp
add_frontmatter "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md" "mcp, mcp-tools" "MCP Tools Telegram Watcher тезисы" "2025-06-07" "1.0" "2025-06-07_MCP-tools-telegram-watcher"

# 03-opencode-config
add_frontmatter "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md" "opencode, agents-md, claude-md" "AGENTS CLAUDE howto тезисы" "2025-06-07" "1.0" "2025-06-07_AGENTS-CLAUDE-howto"

# 04-best-practices
add_frontmatter "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md" "best-practices, eval-driven" "AI Products Systematic Improvement тезисы" "2025-07-26" "1.0" "2025-07-26_AI-products-systematic-improvement"
add_frontmatter "$DOCS/04-best-practices/2025-07-26_Hermes-agent-thesis.md" "best-practices, hermes" "Hermes Agent тезисы" "2025-07-26" "1.0" "2025-07-26_Hermes-agent"
add_frontmatter "$DOCS/04-best-practices/2025-LLM-testing-guide-thesis.md" "best-practices, llm-testing" "LLM Testing Guide тезисы" "2025-06" "1.0" "2025-LLM-testing-guide"
add_frontmatter "$DOCS/04-best-practices/2026-02-12_Context-Engineering-thesis.md" "context-engineering, best-practices" "Context Engineering тезисы" "2026-02-12" "1.0" "2026-02-12_Context-Engineering"
add_frontmatter "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend-thesis.md" "ai-code, фронтенд" "Kharisov AI Frontend тезисы" "2025" "1.0" "2025-vitaly-kharisov-ai-frontend"
add_frontmatter "$DOCS/04-best-practices/2025-polyakov-test-generation-thesis.md" "test-generation, rag" "Polyakov Test Generation тезисы" "2025" "1.0" "2025-polyakov-test-generation"
add_frontmatter "$DOCS/04-best-practices/2025-LLM-better-than-you-thesis.md" "llm-config, prompt-engineering" "LLM Better Than You тезисы" "2025" "1.0" "2025-LLM-better-than-you"
add_frontmatter "$DOCS/04-best-practices/2025-AI-code-unsupportable-thesis.md" "ai-code, best-practices" "AI Code Unsupportable тезисы" "2025" "1.0" "2025-AI-code-unsupportable"

# 07-articles
add_frontmatter "$DOCS/07-articles/2025-06-07_AI-news-digest-thesis.md" "ai-news, дайджест" "AI News Digest тезисы" "2025-06-07" "1.0" "2025-06-07_AI-news-digest"

# Standalone docs (non-thesis, add basic frontmatter without dot_ai header)
add_frontmatter_basic() {
  local file="$1"
  local tags="$2"
  local aliases="$3"

  if head -1 "$file" 2>/dev/null | grep -q '^---$'; then
    echo "  SKIP $file (has frontmatter)"
    return
  fi

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

add_frontmatter_basic "$DOCS/02-mcp/obsidian-hybrid-search-ohs.md" "mcp, obsidian, search" "Obsidian Hybrid Search OHS"
add_frontmatter_basic "$DOCS/03-opencode-config/AGENTS-md-examples-gist.md" "opencode, agents-md" "AGENTS.md examples gist"
add_frontmatter_basic "$DOCS/03-opencode-config/opencode-project-guide-datatalks.md" "opencode" "OpenCode project guide datatalks"
add_frontmatter_basic "$DOCS/04-best-practices/coding-agent-harness-architecture.md" "architecture, best-practices" "Coding Agent Harness architecture"
add_frontmatter_basic "$DOCS/06-tools/browse-sh.md" "tools, browser" "browse.sh CLI"
add_frontmatter_basic "$DOCS/06-tools/microsoft-skills.md" "tools, microsoft, skills" "Microsoft Skills"
add_frontmatter_basic "$DOCS/06-tools/obsidian-guide.md" "tools, obsidian" "Obsidian Guide"
add_frontmatter_basic "$DOCS/06-tools/tgs-test-generator-suite.md" "tools, testing" "TGS Test Generator Suite"

echo ""
echo "=== Done ==="
