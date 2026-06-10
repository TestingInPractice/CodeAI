#!/bin/bash
# migrate-docs-dot-ai.sh — Restructure thesis files in dot_ai style
set -e

DOCS="scripts/build-loop/docs"

echo "=== Updating thesis files to dot_ai format ==="

update_thesis() {
  local thesis="$1"
  local date="$2"
  local version="$3"
  local transcript_name="$4"
  local author="$6"

  [ ! -f "$thesis" ] && echo "  SKIP: $thesis not found" && return

  # Derive source basename (without path/extension)
  local src_name="${transcript_name%.md}"
  src_name="${src_name%-transcript}"

  # Read current source title and URL from file
  local source_title
  source_title=$(grep -m1 '^\*\*Источник:\*\*' "$thesis" 2>/dev/null | sed 's/^\*\*Источник:\*\* //' || echo "YouTube")
  local source_url
  source_url=$(grep -m1 '^\*\*Ссылка:\*\*' "$thesis" 2>/dev/null | sed 's/^\*\*Ссылка:\*\* //' || echo "")

  # Build new frontmatter
  # Read existing tags and aliases
  local tags
  tags=$(grep -m1 '^tags:' "$thesis" 2>/dev/null || echo "[]")
  local aliases
  aliases=$(grep -m1 '^aliases:' "$thesis" 2>/dev/null || echo "[]")

  # Build header: frontmatter + dot_ai quote block
  local header
  header=$(cat << HEADER
---
$tags
$aliases
date: $date
version: $version
source: $src_name
---

> **Дата:** $date
> **Версия:** $version
> **Источник:** [[$src_name]] — $source_title
> **Библиография:** [[../bibliography|Библиография]]

HEADER
)

  # Remove old frontmatter and source block from file
  # Strategy: remove everything from start to first '---' after source block
  # Frontmatter: between first --- and second ---
  # Source block: from '**Источник:**' to '---'
  local tmpfile
  tmpfile=$(mktemp)

  # Use awk to strip old frontmatter and source block
  # Print lines after second '---' that marks end of frontmatter,
  # but skip the source block (lines from '**Источник:**' to next '---')
  awk '
  BEGIN { fm_end=0; in_source=0; }
  /^---$/ && fm_end==0 { fm_end++; next; }
  /^---$/ && fm_end==1 { fm_end=2; next; }
  fm_end==2 {
    if (in_source==0 && /^\*\*Источник:\*\*/) { in_source=1; next; }
    if (in_source==0 && /^\*\*Автор:\*\*/) { in_source=1; next; }
    if (in_source==0 && /^\*\*Ссылка:\*\*/) { in_source=1; next; }
    if (in_source==0 && /^\*\*Стенограмма:\*\*/) { in_source=1; next; }
    if (in_source==1 && /^---$/) { in_source=0; next; }
    if (in_source==1) { next; }
    if (in_source==0) { print; }
  }
  ' "$thesis" > "$tmpfile"

  # Combine header + content
  {
    echo "$header"
    cat "$tmpfile"
  } > "$thesis"

  rm "$tmpfile"

  # Fix wikilink: if it had -transcript suffix, update it
  sed -i '' "s/\[\[${src_name}-transcript\]\]/[[${src_name}]]/g" "$thesis" 2>/dev/null || true

  echo "  OK: $thesis → source: $src_name, date: $date"
}

# === 01-frameworks ===
update_thesis "$DOCS/01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md" "2025-06-07" "1.0" "2025-06-07_GSD-vs-Paul.md" "" "Владилен Минин"
update_thesis "$DOCS/01-frameworks/2025-07-26_DOTI-thesis.md" "2025-07-26" "1.0" "2025-07-26_DOTI.md" "" "Владилен Минин"
update_thesis "$DOCS/01-frameworks/2025-07-26_GSD-Superpowers-thesis.md" "2025-07-26" "1.0" "2025-07-26_GSD-Superpowers.md" "" "Владилен Минин"
update_thesis "$DOCS/01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md" "2025-07-26" "1.0" "2025-07-26_GSD-for-OpenCode.md" "" "Tasher"
update_thesis "$DOCS/01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md" "2025-07-26" "1.0" "2025-07-26_GSD-vs-OpenSpec.md" "" "Tasher"

# === 02-mcp ===
update_thesis "$DOCS/02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md" "2025-06-07" "1.0" "2025-06-07_MCP-tools-telegram-watcher.md" "" "Let's Code Drew"

# === 03-opencode-config ===
update_thesis "$DOCS/03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md" "2025-06-07" "1.0" "2025-06-07_AGENTS-CLAUDE-howto.md" "" "Владилен Минин"

# === 04-best-practices ===
update_thesis "$DOCS/04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md" "2025-07-26" "1.0" "2025-07-26_AI-products-systematic-improvement.md" "" "Владилен Минин"
update_thesis "$DOCS/04-best-practices/2025-07-26_Hermes-agent-thesis.md" "2025-07-26" "1.0" "2025-07-26_Hermes-agent.md" "" ""
update_thesis "$DOCS/04-best-practices/2025-LLM-testing-guide-thesis.md" "2025-06" "1.0" "2025-LLM-testing-guide-transcript.md" "" ""
update_thesis "$DOCS/04-best-practices/2025-vitaly-kharisov-ai-frontend-thesis.md" "2025" "1.0" "2025-vitaly-kharisov-ai-frontend.md" "" "Виталий Харисов"
update_thesis "$DOCS/04-best-practices/2025-polyakov-test-generation-thesis.md" "2025" "1.0" "2025-polyakov-test-generation.md" "" "Александр Поляков"
update_thesis "$DOCS/04-best-practices/2025-LLM-better-than-you-thesis.md" "2025" "1.0" "2025-LLM-better-than-you.md" "" ""
update_thesis "$DOCS/04-best-practices/2025-AI-code-unsupportable-thesis.md" "2025" "1.0" "2025-AI-code-unsupportable.md" "" ""

# === 07-articles ===
update_thesis "$DOCS/07-articles/2025-06-07_AI-news-digest-thesis.md" "2025-06-07" "1.0" "2025-06-07_AI-news-digest.md" "" ""

echo ""
echo "=== Creating bibliography.md ==="
cat > "$DOCS/bibliography.md" << 'BIBEOF'
# Библиография

> Централизованный список всех источников. Каждый thesis-файл ссылается сюда через `[[../bibliography|Библиография]]`.

---

## 🎥 YouTube

| # | Источник | Ссылка | Категория | Дата |
|---|----------|--------|-----------|------|
| 1 | Владилен Минин — "GSD & Superpowers. Vibe coding мёртв" | [YouTube](https://www.youtube.com/watch?v=SOm_F7UtJno) | 01-frameworks | 2025-07-26 |
| 2 | Владилен Минин — "GSD vs Paul — 7 Critical Problems" | [YouTube](https://www.youtube.com/watch?v=MppKHh_MfFc) | 01-frameworks | 2025-06-07 |
| 3 | Tasher — "GSD for OpenCode" | YouTube | 01-frameworks | 2025-07-26 |
| 4 | Tasher — "GSD vs OpenSpec" | YouTube | 01-frameworks | 2025-07-26 |
| 5 | Владилен Минин — "DOTI: AI-агенты без хаоса" | YouTube | 01-frameworks | 2025-07-26 |
| 6 | Let's Code Drew — "MCP Tools: Telegram Watcher" | [YouTube](https://www.youtube.com/watch?v=mBA9Vk1jXDE) | 02-mcp | 2025-06-07 |
| 7 | Владилен Минин — "AGENTS.md и CLAUDE.md: как готовить?" | YouTube | 03-opencode-config | 2025-06-07 |
| 8 | Владилен Минин — "Системное улучшение AI-продуктов" | YouTube | 04-best-practices | 2025-07-26 |
| 9 | "Hermes agent. Как ставить задачи агенту?" | [YouTube](https://youtu.be/nBSd9-wxCVQ) | 04-best-practices | 2025-07-26 |
| 10 | "Тестирование AI и LLM систем — полный гайд" | YouTube | 04-best-practices | 2025-06 |
| 11 | Виталий Харисов — "Я 99.99% кода пишу нейронкой" | YouTube | 04-best-practices | 2025 |
| 12 | Александр Поляков — "Автогенерация тестов в IDE" | YouTube | 04-best-practices | 2025 |
| 13 | "LLM пишет код лучше тебя" | YouTube | 04-best-practices | 2025 |
| 14 | "Почему ИИ-код становится неподдерживаемым" | [YouTube](https://www.youtube.com/watch?v=MdKFWhYZzcs) | 04-best-practices | 2025 |
| 15 | AI-дайджест: Google, Anthropic Claude 4.8, Vertex AI | YouTube | 07-articles | 2025-06-07 |

---

## 📄 Статьи и документация

| # | Источник | Ссылка | Категория |
|---|----------|--------|-----------|
| 1 | Context Engineering — data teams как контекст для AI | — | 04-best-practices |
| 2 | Coding Agent Harness — 6 компонентов (Raschka) | — | 04-best-practices |
| 3 | OHS MCP — Obsidian Hybrid Search | — | 02-mcp |
| 4 | AGENTS.md examples — Boris Cherny patterns | — | 03-opencode-config |
| 5 | microsoft/skills — 174 Azure skills | [GitHub](https://github.com/microsoft/skills) | 06-tools |
| 6 | TGS — Test Generator Suite (FastAPI LLM) | — | 06-tools |
| 7 | browse.sh — Browser CLI + skill catalog | [browse.sh](https://browse.sh/) | 06-tools |
| 8 | Obsidian Guide — CLI, Headless Sync, AGENTS.md | — | 06-tools |
| 9 | datatalks.ru OpenCode Guide | [datatalks](https://datatalks.ru/opencode) | 03-opencode-config |

---

**↪️ INDEX:** [[INDEX|INDEX]]
BIBEOF
echo "  created bibliography.md"

echo ""
echo "=== Done ==="
echo "Run git diff to verify changes"
