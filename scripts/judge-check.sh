#!/bin/bash
# judge-check.sh — Graph Quality Judge
# Usage: bash scripts/judge-check.sh
# Exit code: 0 = Level 2 passed, 1 = failed
set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DOCS="$ROOT/scripts/build-loop/docs"
PASS=0
FAIL=0
LEVEL=1

check() {
  local desc="$1"
  shift
  if eval "$@" 2>/dev/null; then
    echo "  ✅ $desc"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $desc"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Judge Check: Graph Level 1 (Searchable) ==="

# Level 1 — Searchable
NONMD=$(find "$DOCS" -type f \( -not -name "*.md" -and -not -name "*.sh" \) -not -path "*/.git/*" 2>/dev/null | wc -l)
check "No non-md artifacts" test "$NONMD" -eq 0

EMPTY=$(find "$DOCS" -name "*.md" -empty 2>/dev/null | wc -l)
check "No empty .md files" test "$EMPTY" -eq 0

TOTAL=$(find "$DOCS" -name "*.md" | wc -l)
check "Has indexed notes (> 0)" test "$TOTAL" -gt 0

OHS_DB=$(find "$ROOT" -maxdepth 1 -name ".obsidian-hybrid-search.db" 2>/dev/null | wc -l)
check "OHS index available" test "$OHS_DB" -gt 0

# Level 2 — Navigable
echo ""
echo "=== Judge Check: Level 2 (Navigable) ==="

# Count wikilinks
WIKILINKS=$(grep -rn '\[\[.*\]\]' "$DOCS" --include="*.md" 2>/dev/null | wc -l)
check "Total wikilinks > 0" test "$WIKILINKS" -gt 0

# Count orphan notes (no links either direction)
ORPHANS=0
LINKS_BY_FILE=$(mktemp)
grep -rln '\[\[.*\]\]' "$DOCS" --include="*.md" 2>/dev/null > "$LINKS_BY_FILE" || true
for f in $(find "$DOCS" -name "*.md"); do
  if ! grep -qF "$f" "$LINKS_BY_FILE"; then
    basename_f=$(basename "$f" .md)
    if ! grep -rn "\[\[$basename_f\]\]" "$DOCS" --include="*.md" 2>/dev/null | grep -qvF "$f"; then
      ORPHANS=$((ORPHANS + 1))
    fi
  fi
done
rm -f "$LINKS_BY_FILE"
ORPHAN_PCT=$((ORPHANS * 100 / TOTAL))
check "Orphan ratio < 50% ($ORPHAN_PCT%)" test "$ORPHAN_PCT" -lt 50

# Broken wikilinks
BROKEN=0
for raw in $(grep -roh '\[\[[^]]*\]\]' "$DOCS" --include="*.md" 2>/dev/null | sed 's/\[\[//;s/\]\]//' | sed 's/|.*//' | sort -u); do
  resolved=$(find "$DOCS" -name "$(basename "$raw").md" 2>/dev/null | head -1)
  if [ -z "$resolved" ]; then
    # Try as relative path
    resolved=$(find "$DOCS" -path "*/${raw}.md" 2>/dev/null | head -1)
  fi
  if [ -z "$resolved" ] && [ "$raw" != "INDEX" ]; then
    BROKEN=$((BROKEN + 1))
    echo "     broken: [[$raw]]" >&2
  fi
done
check "Broken wikilinks = 0 ($BROKEN)" test "$BROKEN" -eq 0

# MOC per category
MOC_COUNT=0
for dir in 01-frameworks 02-mcp 03-opencode-config 04-best-practices 06-tools 07-articles 08-build-loop references/dot-ai references/hands-on-ai-engineering; do
  if [ -f "$DOCS/$dir/README.md" ]; then
    MOC_COUNT=$((MOC_COUNT + 1))
  fi
done
check "MOC notes (categories with README)" test "$MOC_COUNT" -ge 3

# Frontmatter with tags
FM_TAGS=$(grep -r '^tags:' "$DOCS" --include="*.md" 2>/dev/null | wc -l)
check "Files with tags: frontmatter" test "$FM_TAGS" -gt 0

# Dot AI reference structure
DOTAI_BP=$(find "$DOCS/references/dot-ai/best_practice" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
DOTAI_RS=$(find "$DOCS/references/dot-ai/researches" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
check "dot_ai refs: best_practice ($DOTAI_BP files) and researches ($DOTAI_RS files)" test "$DOTAI_BP" -ge 9 -a "$DOTAI_RS" -ge 5

# Claims tables in thesis files
CLAIMS_FILES=$(grep -rl '^|.*Утверждение.*Источник.*Уровень' "$DOCS" --include="*.md" 2>/dev/null | wc -l)
check "Files with Claims table (≥ 3)" test "$CLAIMS_FILES" -ge 3

# CLAIMS.md exists in build-loop
check "CLAIMS.md in 08-build-loop" test -f "$DOCS/08-build-loop/CLAIMS.md"

# Transcript ↔ thesis pairs linked
PAIRS=0
for thesis in $(find "$DOCS" -name "*-thesis.md"); do
  base=$(basename "$thesis" "-thesis.md")
  has_link=$(grep -c '\[\[.*'"$base"'.*\]\]' "$thesis" 2>/dev/null || true)
  if [ "$has_link" -gt 0 ]; then
    PAIRS=$((PAIRS + 1))
  fi
done
check "Thesis → transcript links" test "$PAIRS" -gt 0

echo ""
echo "=== Результат ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Level: $LEVEL (Level 2: $([ $FAIL -le 1 ] && echo '✅' || echo '❌'))"
echo ""

if [ "$FAIL" -gt 1 ]; then
  echo "❌ Level 2 не пройден. Нужно доработать."
  exit 1
else
  echo "✅ Level 2 пройден. Граф готов для навигации агентом."
  exit 0
fi
