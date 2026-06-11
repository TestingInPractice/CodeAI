#!/usr/bin/env bash
# run-task.sh — Per-task cycle: analyst → judge → dev → judge → tester → judge
# Usage:
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --print-prompt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --judge --summary /tmp/p1-analyst.txt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --print-prompt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --judge --summary /tmp/p1-dev.txt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step tester --print-prompt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step tester --judge --summary /tmp/p1-tester.txt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --complete
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> --phase <id> --step <analyst|dev|tester> [--print-prompt|--judge --summary <file>]"
  echo "       $0 --project <path> --phase <id> --complete"
  exit 1
}

PROJECT=""
PHASE_ID=""
STEP=""
MODE=""
SUMMARY_FILE=""
WORKFLOW_DIR="$(cd "$(dirname "$0")/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p)   PROJECT="$2"; shift 2 ;;
    --phase)        PHASE_ID="$2"; shift 2 ;;
    --step)         STEP="$2"; shift 2 ;;
    --print-prompt) MODE="prompt"; shift ;;
    --judge)        MODE="judge"; shift ;;
    --summary)      SUMMARY_FILE="$2"; shift 2 ;;
    --complete)     MODE="complete"; shift ;;
    *) usage ;;
  esac
done

[ -z "$PROJECT" ] && usage
[ -z "$PHASE_ID" ] && usage
SPECS_DIR="$PROJECT/docs/specs"
PHASES_FILE="$PROJECT/.build-loop/phases.json"

[ ! -f "$PHASES_FILE" ] && echo "Error: $PHASES_FILE not found" && exit 1

read_phase() {
  python3 -c "
import json, sys
with open('$PHASES_FILE') as f:
    data = json.load(f)
for p in data.get('phases', []):
    if str(p.get('id')) == '$PHASE_ID':
        print(json.dumps(p))
        sys.exit(0)
print('NOT_FOUND')
"
}

phase_data=$(read_phase)
[ "$phase_data" = "NOT_FOUND" ] && echo "Error: phase $PHASE_ID not found" && exit 1

phase_name=$(echo "$phase_data" | python3 -c "import json,sys; print(json.load(sys.stdin).get('name','?'))")
ac=$(echo "$phase_data" | python3 -c "import json,sys; ac=json.load(sys.stdin).get('acceptance_criteria',[]); print('\n'.join(ac) if ac else '')")
spec_content=""
for f in "$SPECS_DIR"/*.md; do
  [ -f "$f" ] && spec_content="$spec_content"$'\n---'"$(cat "$f")"
done

generate_analyst_prompt() {
  cat << PROMPT
You are an ANALYST for phase "$PHASE_ID: $phase_name".

Project spec:
$spec_content

Acceptance criteria for this phase:
$ac

Your task:
1. Review the spec and acceptance criteria for this phase
2. Design architecture decisions, data models, and API contracts needed
3. Identify risks, edge cases, and open questions

Output format — write to /tmp/p${PHASE_ID}-analyst-summary.txt:
## Architecture Decisions
...

## Data Models
...

## API Contracts
...

## Risks & Edge Cases
...
PROMPT
}

generate_dev_prompt() {
  cat << PROMPT
You are a DEVELOPER for phase "$PHASE_ID: $phase_name".

Project spec:
$spec_content

Acceptance criteria for this phase:
$ac

Your task:
1. Implement everything required for this phase
2. Verify against acceptance criteria in the spec
3. Follow project architecture and code style

When done, save summary to /tmp/p${PHASE_ID}-dev-summary.txt:
## Files created/modified
- file1.js
- file2.css

## What was implemented
...

## Acceptance criteria met
- AC-001: done
PROMPT
}

generate_tester_prompt() {
  cat << PROMPT
You are a TESTER for phase "$PHASE_ID: $phase_name".

Project spec:
$spec_content

Acceptance criteria for this phase:
$ac

Your task:
1. Write unit tests and/or integration tests for the code in this phase
2. Cover positive cases, edge cases, and error conditions
3. Verify each acceptance criterion has a corresponding test

When done, save summary to /tmp/p${PHASE_ID}-tester-summary.txt:
## Test files created
- tests/test_foo.py

## Test coverage
- AC-001: test_foo_success, test_foo_error
PROMPT
}

case "$MODE" in
  prompt)
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Phase $PHASE_ID — $phase_name [$STEP]"
    echo "╚═══════════════════════════════════════════════╝"
    case "$STEP" in
      analyst) generate_analyst_prompt ;;
      dev|developer) generate_dev_prompt ;;
      tester) generate_tester_prompt ;;
      *) echo "Error: unknown step '$STEP' (analyst|dev|tester)" && exit 1 ;;
    esac
    ;;
  judge)
    [ -z "$SUMMARY_FILE" ] && echo "Error: --judge requires --summary <file>" && exit 1
    [ ! -f "$SUMMARY_FILE" ] && echo "Error: summary file not found: $SUMMARY_FILE" && exit 1
    JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"

    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Judge: Phase $PHASE_ID — $phase_name [$STEP]"
    echo "╚═══════════════════════════════════════════════╝"

    spec_file=""
    for f in "$SPECS_DIR"/*.md; do [ -f "$f" ] && spec_file="$f" && break; done

    if [ "$STEP" = "analyst" ]; then
      python3 "$JUDGE_SCRIPT" \
        --question "Phase $PHASE_ID: $phase_name (analyst: architecture, data models, contracts)" \
        --response "$(cat "$SUMMARY_FILE")" \
        --context "$(cat "$spec_file")" \
        --phase-id "$PHASE_ID" \
        --phases-path "$PHASES_FILE" && echo "✅ Analyst judge PASSED" || echo "❌ Analyst judge FAILED"
    elif [ "$STEP" = "dev" ] || [ "$STEP" = "developer" ]; then
      python3 "$JUDGE_SCRIPT" \
        --question "Phase $PHASE_ID: $phase_name (developer: implementation)" \
        --response "$(cat "$SUMMARY_FILE")" \
        --context "$(cat "$spec_file")" \
        --phase-id "$PHASE_ID" \
        --phases-path "$PHASES_FILE" && echo "✅ Dev judge PASSED" || echo "❌ Dev judge FAILED"
    elif [ "$STEP" = "tester" ]; then
      python3 "$JUDGE_SCRIPT" \
        --question "Phase $PHASE_ID: $phase_name (tester: test coverage)" \
        --response "$(cat "$SUMMARY_FILE")" \
        --context "$(cat "$spec_file")" \
        --phase-id "$PHASE_ID" \
        --phases-path "$PHASES_FILE" && echo "✅ Tester judge PASSED" || echo "❌ Tester judge FAILED"
    else
      echo "Error: unknown step '$STEP'"
      exit 1
    fi
    ;;
  complete)
    echo "✅ Phase $PHASE_ID \"$phase_name\" — all steps passed"
    echo "Ready for: git add && git commit && run-loop.sh --mark-complete $PHASE_ID"
    ;;
  *)
    usage
    ;;
esac
