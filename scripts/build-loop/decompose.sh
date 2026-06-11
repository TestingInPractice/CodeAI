#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path>"
  exit 1
}

PROJECT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p) PROJECT="$2"; shift 2 ;;
    *) usage ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "Error: --project is required"
  usage
fi

SPECS_DIR="$PROJECT/docs/specs"
STATE_DIR="$PROJECT/.build-loop"
PHASES_FILE="$STATE_DIR/phases.json"

if [ ! -d "$SPECS_DIR" ]; then
  echo "Error: $SPECS_DIR does not exist. Run init.sh first."
  exit 1
fi

if [ -f "$PHASES_FILE" ]; then
  phase_count=$(python3 -c "
import json
try:
  with open('$PHASES_FILE') as f:
    data = json.load(f)
    print(len(data.get('phases', [])))
except:
  print('0')
" 2>/dev/null || echo "0")
  if [ "$phase_count" -gt 0 ]; then
    echo "=== Build Loop: phases.json already exists with $phase_count phase(s) ==="
    echo "To re-decompose, delete $PHASES_FILE and re-run this script."
    echo ""
    echo "Next:"
    echo "  bash $(cd "$(dirname "$0")" && pwd)/next-phase.sh --project \"$PROJECT\""
    exit 0
  fi
fi

echo "=== Build Loop: Decompose $PROJECT ==="
echo ""

spec_files=$(find "$SPECS_DIR" -type f \( -name "*.md" -o -name "*.MD" \) | sort || true)

if [ -z "$spec_files" ]; then
  echo "Error: no .md files found in $SPECS_DIR"
  echo "Fill docs/specs/ with your project description, then re-run."
  exit 1
fi

echo "Spec files found:"
echo "$spec_files" | sed "s|$PROJECT/|  ./|"
echo ""
echo "---"
echo ""

# ============================================================
# AI Decomposition Task
# ============================================================
# The text below is read by the AI orchestrator (this script's stdout).
# The AI must analyze docs/specs/ semantically and create phases.json.
# ============================================================

cat << "TASK" | sed "s|PROJECT_ROOT|$PROJECT|g"
No phases.json found — creating decomposition prompt for AI orchestrator.

## Your task

Read all files in `docs/specs/`, then:

1. **Analyze** the project goals, acceptance criteria, API contracts, and data models
2. **Split** the work into phases — each phase must be:
   - Small enough to fit in a single AI session (under ~50% context window)
   - Semantically cohesive (one logical unit of work)
   - Independently verifiable against its acceptance criteria
3. **Identify dependencies** between phases (e.g., auth must exist before users)
4. **Create `.build-loop/phases.json`** with this exact structure:

```json
{
  "phases": [
    {
      "id": "p1",
      "name": "Short Phase Name",
      "description": "Brief scope description (one line)",
      "status": "pending",
      "depends_on": [],
      "acceptance_criteria": [
        "Criterion that maps to docs/specs/acceptance-criteria.md"
      ]
    },
    {
      "id": "p2",
      "name": "Next Phase",
      "description": "...",
      "status": "pending",
      "depends_on": ["p1"],
      "acceptance_criteria": ["..."]
    }
  ]
}
```

Rules:
- IDs: `p1`, `p2`, `p3`, ...
- `depends_on`: list of phase IDs that must be completed first
- `acceptance_criteria`: copy directly from `acceptance-criteria.md`
- Status: always `"pending"` for new phases
- 5-7 phases max — no micro-phases
- First phase (`p1`) should depend on nothing (project setup / foundation)

5. After creating `.build-loop/phases.json`, run:
   ```
   bash scripts/build-loop/next-phase.sh --project "PROJECT_ROOT"
   ```

6. If you are unsure about phase boundaries, keep phases larger rather than smaller.
   You can always split a phase later with `GSD Split Phase`.
TASK

echo ""
echo "=== Decompose complete ==="
