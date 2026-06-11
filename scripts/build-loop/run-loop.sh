#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> [--phase <id>] [--print-prompt] [--mark-complete] [--judge] [--summary <file>]"
  exit 1
}

PROJECT=""
PHASE_ID=""
MODE="status"
SUMMARY_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p)      PROJECT="$2"; shift 2 ;;
    --phase)           PHASE_ID="$2"; shift 2 ;;
    --print-prompt)    MODE="prompt"; shift ;;
    --mark-complete)   MODE="complete"; PHASE_ID="${2:-}"; shift 2; if [ -z "$PHASE_ID" ]; then echo "Error: --mark-complete requires phase id"; usage; fi ;;
    --judge)           MODE="judge"; shift ;;
    --summary)         SUMMARY_FILE="$2"; shift 2 ;;
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
JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"

if [ ! -f "$PHASES_FILE" ]; then
  echo "Error: $PHASES_FILE not found. Run decompose.sh first."
  exit 1
fi

find_spec_file() {
  local dir="$1"
  for f in "$dir"/*.md "$dir"/*.MD; do
    if [ -f "$f" ]; then
      echo "$f"
      return 0
    fi
  done
  echo ""
}

read_phase() {
  local id="$1"
  python3 -c "
import json, sys
with open('$PHASES_FILE') as f:
    data = json.load(f)
for p in data.get('phases', []):
    if str(p.get('id')) == '$id':
        print(json.dumps(p))
        sys.exit(0)
print('NOT_FOUND')
"
}

generate_prompt() {
  local phase_name="$1"
  local spec_content

  spec_content=$(find_spec_file "$SPECS_DIR")
  if [ -n "$spec_content" ]; then
    spec_content=$(cat "$spec_content")
  else
    spec_content="Spec file not found in $SPECS_DIR"
  fi

  cat << PROMPT
You are executing phase "$phase_name" of the project.

### Full Spec:
$spec_content

### Task:
1. Read the full spec above.
2. Understand which part of it corresponds to phase "$phase_name".
3. Implement everything required for this phase.
4. Verify against the acceptance criteria in the spec.

When done:
1. Save a summary of what was done to /tmp/p<phase-id>-summary.txt
2. Return control to orchestrator (do NOT run judge or commit)
PROMPT
}

case "$MODE" in
  prompt)
    if [ -z "$PHASE_ID" ]; then
      echo "Error: --print-prompt requires --phase <id>"
      exit 1
    fi
    phase_data=$(read_phase "$PHASE_ID")
    if [ "$phase_data" = "NOT_FOUND" ]; then
      echo "Error: phase $PHASE_ID not found in phases.json"
      exit 1
    fi
    phase_name=$(echo "$phase_data" | python3 -c "import json,sys; print(json.load(sys.stdin).get('name','Unknown'))")
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Phase $PHASE_ID: $phase_name"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "--- Phase Details ---"
    echo "$phase_data" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for k,v in d.items():
    if k == 'id': continue
    print(f'  {k}: {v}')
"
    echo ""
    echo "--- Phase Prompt ---"
    generate_prompt "$phase_name"
    ;;

  judge)
    if [ -z "$PHASE_ID" ]; then
      echo "Error: --judge requires --phase <id>"
      exit 1
    fi
    if [ -z "$SUMMARY_FILE" ] || [ ! -f "$SUMMARY_FILE" ]; then
      echo "Error: --judge requires --summary <file> (path to sub-agent summary)"
      exit 1
    fi
    if [ ! -f "$JUDGE_SCRIPT" ]; then
      echo "Error: judge script not found at $JUDGE_SCRIPT"
      echo "Install: copy from CodeAI repo or create scripts/judge/llm-judge.py"
      exit 1
    fi

    phase_data=$(read_phase "$PHASE_ID")
    phase_name=$(echo "$phase_data" | python3 -c "import json,sys; print(json.load(sys.stdin).get('name','Unknown'))")
    spec_file=$(find_spec_file "$SPECS_DIR")

    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Judge: Phase $PHASE_ID — $phase_name"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""

    if python3 "$JUDGE_SCRIPT" \
      --question "Phase $PHASE_ID: $phase_name" \
      --response "$(cat "$SUMMARY_FILE")" \
      --context "$(cat "$spec_file")" \
      --phase-id "$PHASE_ID" \
      --phases-path "$PHASES_FILE"; then
      echo ""
      echo "✅ Judge PASSED — phase $PHASE_ID ready for commit"
    else
      echo ""
      echo "❌ Judge FAILED — phase $PHASE_ID needs rework"
      echo "   Fix issues and re-run:"
      echo "   bash $0 --project \"$PROJECT\" --judge --phase $PHASE_ID --summary $SUMMARY_FILE"
    fi
    ;;

  complete)
    phase_data=$(read_phase "$PHASE_ID")
    if [ "$phase_data" = "NOT_FOUND" ]; then
      echo "Error: phase $PHASE_ID not found in phases.json"
      exit 1
    fi
    phase_name=$(echo "$phase_data" | python3 -c "import json,sys; print(json.load(sys.stdin).get('name','Unknown'))")
    python3 -c "
import json
with open('$PHASES_FILE') as f:
    data = json.load(f)
for p in data['phases']:
    if str(p.get('id')) == '$PHASE_ID':
        p['status'] = 'completed'
        break
with open('$PHASES_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    echo "✅ Phase $PHASE_ID \"$phase_name\" marked as completed."
    echo ""
    echo "Check next phase:"
    echo "  bash scripts/build-loop/next-phase.sh --project \"$PROJECT\""
    ;;

  status)
    echo "=== Phases Status ==="
    python3 -c "
import json
with open('$PHASES_FILE') as f:
    data = json.load(f)
phases = data.get('phases', [])
if not phases:
    print('  No phases found. Run decompose.sh first.')
else:
    for p in phases:
        deps = p.get('depends_on', [])
        dep_str = f' (depends on: {deps})' if deps else ''
        status = p.get('status', 'pending')
        icon = '✅' if status == 'completed' else '⏳' if status == 'in_progress' else '⬜'
        print(f'  {icon} Phase {p[\"id\"]}: {p.get(\"name\", \"?\")} [{status}]{dep_str}')
    print()
    print('Next step:')
    print('  bash scripts/build-loop/next-phase.sh --project \"$PROJECT\"')
"
    ;;
esac
