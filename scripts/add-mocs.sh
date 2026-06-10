#!/bin/bash
# add-mocs.sh — Create MOC (README.md) for each category
set -e

DOCS="scripts/build-loop/docs"

create_moc() {
  local dir="$1"
  local title="$2"
  local desc="$3"
  local moc="$DOCS/$dir/README.md"

  if [ -f "$moc" ]; then
    echo "SKIP $dir (already exists)"
    return
  fi

  {
    echo "# $title"
    echo ""
    echo "$desc"
    echo ""
    echo "## Содержание"
    echo ""

    for f in "$DOCS/$dir"/*.md; do
      base=$(basename "$f" .md)
      [ "$base" = "README" ] && continue
      # Get first line as description
      first_line=$(head -1 "$f" 2>/dev/null | sed 's/^# //')
      echo "- [[$base]]${first_line:+ — $first_line}"
    done

    echo ""
    echo "---"
    echo ""
    echo "**↪️ INDEX:** [[../INDEX|INDEX]]"
  } > "$moc"
  echo "  CREATED $moc"
}

echo "=== Creating MOC notes ==="

create_moc "01-frameworks" "Фреймворки AI-разработки" "GSD, DOTI, OpenSpec, Superpowers, Paul и другие методологии spec-driven AI-разработки."
create_moc "02-mcp" "MCP (Model Context Protocol)" "MCP-серверы, инструменты и протоколы для подключения внешних данных к AI-агентам."
create_moc "03-opencode-config" "OpenCode & Agent Configuration" "AGENTS.md, System.md, настройка агентов, Cursor Rules."
create_moc "04-best-practices" "Best Practices" "Контекст-инжиниринг, Hermes, eval-driven development, coding agent harness."
create_moc "06-tools" "Инструменты" "CLI-утилиты, browse.sh, Obsidian, TGS, microsoft/skills."
create_moc "07-articles" "Статьи и референсы" "Внешние статьи, референсы и источники."
create_moc "08-build-loop" "Build Loop" "Shell-скрипты и метрики Build Loop."

echo ""
echo "=== Linking standalone docs to MOCs ==="

# Link standalone docs to their MOC
add_moc_link() {
  local file="$1"
  local moc_link="$2"
  if ! grep -q "\[\[$moc_link\]\]" "$file" 2>/dev/null; then
    echo "" >> "$file"
    echo "---" >> "$file"
    echo "" >> "$file"
    echo "**↪️ Категория:** [[$moc_link]]" >> "$file"
    echo "  linked $file → $moc_link"
  fi
}

add_moc_link "$DOCS/02-mcp/obsidian-hybrid-search-ohs.md" "../02-mcp/README"
add_moc_link "$DOCS/03-opencode-config/AGENTS-md-examples-gist.md" "../03-opencode-config/README"
add_moc_link "$DOCS/03-opencode-config/opencode-project-guide-datatalks.md" "../03-opencode-config/README"
add_moc_link "$DOCS/04-best-practices/2026-02-12_Context-Engineering-thesis.md" "../04-best-practices/README"
add_moc_link "$DOCS/04-best-practices/coding-agent-harness-architecture.md" "../04-best-practices/README"
add_moc_link "$DOCS/06-tools/browse-sh.md" "../06-tools/README"
add_moc_link "$DOCS/06-tools/microsoft-skills.md" "../06-tools/README"
add_moc_link "$DOCS/06-tools/obsidian-guide.md" "../06-tools/README"
add_moc_link "$DOCS/06-tools/tgs-test-generator-suite.md" "../06-tools/README"

echo ""
echo "=== Done ==="
