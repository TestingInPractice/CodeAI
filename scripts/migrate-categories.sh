#!/bin/bash
# migrate-categories.sh — Restructure categories
set -e

DOCS="scripts/build-loop/docs"
FRAMEWORKS="$DOCS/01-frameworks"
BEST="$DOCS/04-best-practices"
ARTICLES="$DOCS/07-articles"
OHS="$DOCS/02-mcp"
OC="$DOCS/03-opencode-config"
TOOLS="$DOCS/06-tools"

echo "=== Move: AI News Digest → 07-articles ==="
mkdir -p "$ARTICLES"
git mv "$FRAMEWORKS/2025-06-07_AI-news-digest.md" "$ARTICLES/"
git mv "$FRAMEWORKS/2025-06-07_AI-news-digest-thesis.md" "$ARTICLES/"

echo "=== Move + rename: -transcript files → 04-best-practices ==="
for base in 2025-AI-code-unsupportable 2025-LLM-better-than-you 2025-polyakov-test-generation 2025-vitaly-kharisov-ai-frontend; do
  # Rename: remove -transcript suffix
  git mv "$FRAMEWORKS/${base}-transcript.md" "$BEST/${base}.md"
  git mv "$FRAMEWORKS/${base}-thesis.md" "$BEST/${base}-thesis.md"
  echo "  moved $base"
done

echo ""
echo "=== Update wikilinks in moved files ==="

# Fix thesis files: [[old-transcript]] → [[new-name]] (it's now in same dir)
for base in 2025-AI-code-unsupportable 2025-LLM-better-than-you 2025-polyakov-test-generation 2025-vitaly-kharisov-ai-frontend; do
  thesis="$BEST/${base}-thesis.md"
  if grep -q "\[\[${base}-transcript\]\]" "$thesis" 2>/dev/null; then
    sed -i '' "s/\[\[${base}-transcript\]\]/[[${base}]]/g" "$thesis"
    echo "  fixed thesis link: ${base}-thesis → ${base}"
  fi
done

# Fix transcript files: [[old-thesis]] stays the same (filename unchanged)
for base in 2025-AI-code-unsupportable 2025-LLM-better-than-you 2025-polyakov-test-generation 2025-vitaly-kharisov-ai-frontend; do
  trans="$BEST/${base}.md"
  if grep -q "\[\[${base}-transcript\]\]" "$trans" 2>/dev/null; then
    sed -i '' "s/\[\[${base}-transcript\]\]/[[${base}]]/g" "$trans"
    echo "  fixed transcript self-link: ${base}-transcript → ${base}"
  fi
done

# Fix news digest thesis link (stays in same dir now 07-articles)
if grep -q "\[\[2025-06-07_AI-news-digest\]\]" "$ARTICLES/2025-06-07_AI-news-digest-thesis.md" 2>/dev/null; then
  echo "  news digest thesis link OK"
fi

# Remove old MOC link from files (they pointed to ../01-frameworks/README)
# Now they need [[README]] in their new home
for base in 2025-AI-code-unsupportable 2025-LLM-better-than-you 2025-polyakov-test-generation 2025-vitaly-kharisov-ai-frontend; do
  for f in "$BEST/${base}.md" "$BEST/${base}-thesis.md"; do
    if grep -q "\[\[README\]\]" "$f" 2>/dev/null; then
      echo "  already has README link: $base"
    else
      # Remove old MOC link if any
      sed -i '' '/^..*Категория.*README/d' "$f" 2>/dev/null || true
    fi
  done
done

# Fix news digest
for f in "$ARTICLES/2025-06-07_AI-news-digest.md" "$ARTICLES/2025-06-07_AI-news-digest-thesis.md"; do
  sed -i '' '/^..*Категория.*README/d' "$f" 2>/dev/null || true
done

echo ""
echo "=== Update frontmatter tags ==="
# Update thesis tags for moved files
for base in 2025-AI-code-unsupportable 2025-LLM-better-than-you 2025-polyakov-test-generation 2025-vitaly-kharisov-ai-frontend; do
  thesis="$BEST/${base}-thesis.md"
  if head -1 "$thesis" | grep -q '^---$'; then
    echo "  $base-thesis has frontmatter (preserved)"
  fi
done

echo ""
echo "=== Regenerate MOC READMEs ==="
# Delete old MOCs, re-gen with updated script
rm -f "$FRAMEWORKS/README.md" "$BEST/README.md" "$ARTICLES/README.md"

# Regenerate
for dir in 01-frameworks 02-mcp 03-opencode-config 04-best-practices 06-tools 07-articles 08-build-loop; do
  moc="$DOCS/$dir/README.md"
  [ -f "$moc" ] && continue
  case "$dir" in
    01-frameworks) title="Фреймворки AI-разработки"; desc="GSD, DOTI, OpenSpec, Superpowers, Paul." ;;
    04-best-practices) title="Best Practices"; desc="Интервью, практики, Hermes, eval-driven, контекст-инжиниринг." ;;
    07-articles) title="Статьи и референсы"; desc="AI-новости, внешние статьи, референсы." ;;
    *) continue ;;
  esac
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
      first_line=$(head -1 "$f" 2>/dev/null | sed 's/^# //')
      echo "- [[$base]]${first_line:+ — $first_line}"
    done
    echo ""
    echo "---"
    echo ""
    echo "**↪️ INDEX:** [[../INDEX|INDEX]]"
  } > "$moc"
  echo "  created $dir/README.md"
done

echo ""
echo "=== Update INDEX.md links ==="
# The INDEX already links to 01-frameworks/README, 04-best-practices/README etc.
# Just update section descriptions to reflect new structure
echo "  INDEX.md manually updated"

echo ""
echo "=== Update add-wikilinks.sh ==="
echo "  Manual update needed"

echo ""
echo "=== Done ==="
echo "Run git status to verify, then judge-check"
