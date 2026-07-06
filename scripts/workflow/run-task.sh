#!/usr/bin/env bash
# run-task.sh — Per-task cycle: analyst → judge → dev → judge → tester → judge
# Usage:
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --run
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --run
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --print-prompt  [deprecated]
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --judge
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --judge
#   bash scripts/workflow/run-task.sh --project . --phase p1 --step tester --judge --summary /tmp/p1-tester.txt
#   bash scripts/workflow/run-task.sh --project . --phase p1 --complete
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> --phase <id> --step <analyst|dev|tester> [--run|--print-prompt|--judge]"
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
    --run)          MODE="run"; shift ;;
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

Read $TASKS_DIR/architecture.md (the architecture analysis).

Your task:
1. Write unit tests and/or integration tests for the code in this phase
2. Cover positive cases, edge cases, and error conditions
3. Verify each acceptance criterion has a corresponding test

When done, save summary to $TASKS_DIR/tester-summary.md:
## Test files created
- tests/test_foo.py

## Test coverage
- AC-001: test_foo_success, test_foo_error
PROMPT
}

# ──────────────────────────────────────────────────
# Shared judge runner
# ──────────────────────────────────────────────────

run_judge() {
  local label="$1"
  if python3 "$JUDGE_SCRIPT" \
    --question "Phase $PHASE_ID: $phase_name ($label)" \
    --response "$(cat "$SUMMARY_FILE")" \
    --context "$all_specs" \
    --phase-id "$PHASE_ID" \
    --phases-path "$PHASES_FILE"; then
    echo "✅ $label judge PASSED"
    # Only tester's PASS sets judge_passed (final verification gate)
    label_lc="$(echo "$label" | tr '[:upper:]' '[:lower:]')"
    if [ "$label_lc" = "tester" ]; then
      python3 -c "
import json
with open('$PHASES_FILE') as f:
    data = json.load(f)
for p in data['phases']:
    if str(p.get('id')) == '$PHASE_ID':
        p['judge_passed'] = True
        break
with open('$PHASES_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    fi
  else
    echo "❌ $label judge FAILED"
    python3 -c "
import json
with open('$PHASES_FILE') as f:
    data = json.load(f)
for p in data['phases']:
    if str(p.get('id')) == '$PHASE_ID' and 'judge_passed' in p:
        del p['judge_passed']
        break
with open('$PHASES_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
  fi
}

# ──────────────────────────────────────────────────
# OODA orchestration (--run mode)
# ──────────────────────────────────────────────────

TASKS_DIR="$PROJECT/.opencode/tasks/phase-$PHASE_ID"

ensure_opencode() {
  if ! command -v opencode &>/dev/null; then
    echo "❌ opencode CLI not found. Install it or use --print-prompt fallback."
    exit 1
  fi
}

generate_tester_decide_prompt() {
  cat << PROMPT
You are a TEST PLAN designer for phase "$PHASE_ID: $phase_name".

Project spec:
$spec_content

Acceptance criteria for this phase:
$ac

Read $TASKS_DIR/architecture.md (the architecture analysis).

Your task:
1. Design a test plan covering all ACs, edge cases, and error conditions
2. Use the standard plan template below

Output format — write to $TASKS_DIR/test-plan.md with EXACTLY this structure:

## Files
- path/file: reason for test

## Changes
1. file: what test to write, why

## Risks
- what might be hard to test, how to mitigate

## Tests
- AC mapping: which test covers which AC
- test scenarios with inputs and expected outputs

## Rollback
- how to revert test files

Do NOT write any implementation code.
Do NOT redesign — test what exists.
PROMPT
}

run_tester() {
  ensure_opencode
  mkdir -p "$TASKS_DIR"
  local plan_file="$TASKS_DIR/test-plan.md"
  local tester_summary="$TASKS_DIR/tester-summary.md"

  echo "📋 [DECIDE] Creating test plan..."
  opencode run --agent decide --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Read $TASKS_DIR/architecture.md.
Write a test plan to $plan_file.
Use template: Files, Changes, Risks, Tests, Rollback." > /dev/null 2>&1

  # Validate plan structure
  if [ -f "$plan_file" ]; then
    local missing=""
    for section in "Files" "Changes" "Risks" "Tests" "Rollback"; do
      if ! grep -q "^## $section" "$plan_file" 2>/dev/null; then
        missing="$missing $section"
      fi
    done
    if [ -n "$missing" ]; then
      echo "❌ [VALIDATE] Test plan missing sections:$missing"
      exit 1
    fi
    echo "✅ [VALIDATE] Test plan structure valid"
  else
    echo "❌ [VALIDATE] test-plan.md not created"
    exit 1
  fi

  echo "🔧 [ACT] Writing tests..."
  opencode run --agent act --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Read $plan_file. Write tests step by step.
MUST follow plan. Do NOT redesign.
Install test dependencies if needed (pip install pytest, etc.).
Run the tests and verify they pass.
If any test fails — fix the test, not the production code.
If impossible — STOP.
When done, write summary to $tester_summary" > "$tester_summary" 2>/dev/null

  echo "⚖️  [JUDGE] Evaluating tester output..."
  SUMMARY_FILE="$tester_summary"
  JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"
  all_specs="$(cat "$SPECS_DIR"/*.md 2>/dev/null || echo '')"
  run_judge "Tester"
}

run_analyst() {
  ensure_opencode
  mkdir -p "$TASKS_DIR"
  local observe_file="$TASKS_DIR/observe-summary.md"
  local arch_file="$TASKS_DIR/architecture.md"

  echo "🔍 [OBSERVE] Collecting facts..."
  opencode run --agent observe --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Find all files relevant to this phase. Read them. Record ONLY facts.
Output your findings. Do NOT write any files." > "$observe_file" 2>/dev/null

  echo "🧭 [ORIENT] Analyzing architecture..."
  opencode run --agent orient --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Read the observe findings above. Analyze the architecture.
Design decisions, risks, and file list.
Output your analysis. Do NOT write any files." > "$arch_file" 2>/dev/null

  echo "⚖️  [JUDGE] Evaluating analyst output..."
  SUMMARY_FILE="$arch_file"
  JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"
  all_specs="$(cat "$SPECS_DIR"/*.md 2>/dev/null || echo '')"
  run_judge "Analyst"
}

run_dev() {
  ensure_opencode
  mkdir -p "$TASKS_DIR"
  local arch_file="$TASKS_DIR/architecture.md"
  local plan_file="$TASKS_DIR/plan.md"
  local dev_summary="$TASKS_DIR/dev-summary.md"

  echo "📋 [DECIDE] Creating plan..."
  opencode run --agent decide --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Read $arch_file. Write a step-by-step plan to $plan_file.
Use template: Files, Changes, Risks, Tests, Rollback." > /dev/null 2>&1

  # Validate plan structure
  if [ -f "$plan_file" ]; then
    local missing=""
    for section in "Files" "Changes" "Risks" "Tests" "Rollback"; do
      if ! grep -q "^## $section" "$plan_file" 2>/dev/null; then
        missing="$missing $section"
      fi
    done
    if [ -n "$missing" ]; then
      echo "❌ [VALIDATE] Plan missing sections:$missing"
      exit 1
    fi
    echo "✅ [VALIDATE] Plan structure valid"
  else
    echo "❌ [VALIDATE] plan.md not created"
    exit 1
  fi

  echo "🔧 [ACT] Implementing plan..."
  opencode run --agent act --auto --dir "$PROJECT" \
    "Phase $PHASE_ID: $phase_name

Spec:
$spec_content

Acceptance criteria:
$ac

Read $plan_file. Implement step by step.
MUST follow plan. Do NOT redesign.
If impossible — STOP.
When done, write summary to $dev_summary" > "$dev_summary" 2>/dev/null

  echo "⚖️  [JUDGE] Evaluating developer output..."
  SUMMARY_FILE="$dev_summary"
  JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"
  all_specs="$(cat "$SPECS_DIR"/*.md 2>/dev/null || echo '')"
  run_judge "Dev"
}

case "$MODE" in
  prompt)
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Phase $PHASE_ID — $phase_name [$STEP]      ║"
    echo "║  ⚠️  Deprecated: use --run instead           ║"
    echo "╚═══════════════════════════════════════════════╝"
    case "$STEP" in
      analyst) generate_analyst_prompt ;;
      dev|developer) generate_dev_prompt ;;
      tester) generate_tester_prompt ;;
      *) echo "Error: unknown step '$STEP' (analyst|dev|tester)" && exit 1 ;;
    esac
    ;;
  run)
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  OODA Run: Phase $PHASE_ID — $phase_name [$STEP]"
    echo "╚═══════════════════════════════════════════════╝"
    case "$STEP" in
      analyst) run_analyst ;;
      dev|developer) run_dev ;;
      tester) run_tester ;;
      *) echo "Error: unknown step '$STEP' (analyst|dev|tester)" && exit 1 ;;
    esac
    ;;
  judge)
    # Default paths for artifacts if --summary not given
    if [ -z "$SUMMARY_FILE" ]; then
      TASKS_DIR="$PROJECT/.opencode/tasks/phase-$PHASE_ID"
      case "$STEP" in
        analyst) SUMMARY_FILE="$TASKS_DIR/architecture.md" ;;
        dev|developer) SUMMARY_FILE="$TASKS_DIR/dev-summary.md" ;;
        tester) SUMMARY_FILE="$TASKS_DIR/tester-summary.md" ;;
      esac
    fi
    [ ! -f "$SUMMARY_FILE" ] && echo "Error: summary file not found: $SUMMARY_FILE" && exit 1
    JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"

    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Judge: Phase $PHASE_ID — $phase_name [$STEP]"
    echo "╚═══════════════════════════════════════════════╝"

    # Read all spec files for complete context
    all_specs=""
    while IFS= read -r f; do
      all_specs+="--- $(basename "$f") ---"$'\n'
      all_specs+=$(cat "$f")
      all_specs+=$'\n\n'
    done < <(find "$SPECS_DIR" -type f \( -name "*.md" -o -name "*.MD" \) | sort 2>/dev/null)
    if [ -z "$all_specs" ]; then
      all_specs="Spec files not found in $SPECS_DIR"
    fi

    if [ "$STEP" = "analyst" ]; then
      run_judge "Analyst"
    elif [ "$STEP" = "dev" ] || [ "$STEP" = "developer" ]; then
      run_judge "Dev"
    elif [ "$STEP" = "tester" ]; then
      run_judge "Tester"
    else
      echo "Error: unknown step '$STEP'"
      exit 1
    fi
    ;;
  complete)
    RUN_LOOP="$WORKFLOW_DIR/build-loop/run-loop.sh"
    if [ ! -f "$RUN_LOOP" ]; then
      echo "Error: $RUN_LOOP not found" && exit 1
    fi
    echo "✅ Phase $PHASE_ID \"$phase_name\" — all steps passed"
    echo "---"
    bash "$RUN_LOOP" --project "$PROJECT" --mark-complete "$PHASE_ID"
    ;;
  *)
    usage
    ;;
esac
