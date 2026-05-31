#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> [--phase <id>]"
  exit 1
}

PROJECT=""
PHASE_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p) PROJECT="$2"; shift 2 ;;
    --phase)      PHASE_ID="$2"; shift 2 ;;
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

if [ ! -f "$PHASES_FILE" ]; then
  echo "Error: $PHASES_FILE not found. Run decompose.sh first."
  exit 1
fi

# Check for claude CLI
if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found. Build Loop headless mode requires Claude Code."
  echo ""
  echo "Alternative: run the Ralph Loop inside an OpenCode session with AGENTS.md from init.sh."
  exit 1
fi

echo "=== Build Loop: Ralph Loop ==="

generate_prompt() {
  local phase_name="$1"
  local goals contracts criteria context

  goals=$(cat "$SPECS_DIR/goals.md" 2>/dev/null || echo "No goals.md")

  contracts=""
  if [ -f "$SPECS_DIR/contracts/api.md" ]; then
    contracts=$(cat "$SPECS_DIR/contracts/api.md")
  fi
  if [ -f "$SPECS_DIR/contracts/data-models.md" ]; then
    models=$(cat "$SPECS_DIR/contracts/data-models.md")
    contracts="$contracts"$'\n\n'"$models"
  fi

  criteria=$(cat "$SPECS_DIR/acceptance-criteria.md" 2>/dev/null || echo "No acceptance-criteria.md")

  cat << PROMPT
You are executing phase "$phase_name" of the project.

### Goals:
$goals

### Contracts:
$contracts

### Acceptance Criteria:
$criteria

### Task:
1. Take acceptance criteria as tests — write them first (TDD)
2. Implement code according to contracts
3. Verify: all acceptance criteria pass

If architecture decisions are needed — use GStack role voting.
PROMPT
}

run_phase() {
  local phase_id="$1"
  local phase_name="$2"
  local prompt

  echo ""
  echo "--- Phase $phase_id: $phase_name ---"

  prompt=$(generate_prompt "$phase_name")

  echo "Delegating to headless session..."
  claude -p "$prompt" --model claude-sonnet-4-20250514 > "$STATE_DIR/phase-${phase_id}-result.txt" 2>&1

  echo "Phase $phase_id complete. Result saved to .build-loop/phase-${phase_id}-result.txt"
}

if [ -n "$PHASE_ID" ]; then
  # Run single phase
  phase_name=$(jq -r ".phases[] | select(.id == $PHASE_ID) | .name" "$PHASES_FILE")
  if [ -z "$phase_name" ] || [ "$phase_name" = "null" ]; then
    echo "Error: phase $PHASE_ID not found in phases.json"
    exit 1
  fi
  run_phase "$PHASE_ID" "$phase_name"
else
  # Run all pending phases in order
  python3 -c "
import json, sys

with open('$PHASES_FILE') as f:
    data = json.load(f)

phases = data.get('phases', [])
pending = [p for p in phases if p.get('status') == 'pending']

if not pending:
    print('No pending phases found')
    sys.exit(0)

print(f'Found {len(pending)} pending phases')

# Check dependencies — simple topological order
completed_ids = {p['id'] for p in phases if p.get('status') == 'completed'}

for phase in pending:
    deps = phase.get('depends_on', [])
    missing = [d for d in deps if d not in completed_ids]
    if missing:
        print(f'  Phase {phase[\"id\"]} ({phase[\"name\"]}) waits for phases {missing}')
        continue

    print(f'  Phase {phase[\"id\"]} ({phase[\"name\"]}) is ready')
" 2>&1 || echo "python3 not available — run phases manually"

  # Iterate
  python3 -c "
import json, subprocess, sys

with open('$PHASES_FILE') as f:
    data = json.load(f)

phases = data.get('phases', [])
completed_ids = {p['id'] for p in phases if p.get('status') == 'completed'}

for phase in phases:
    if phase.get('status') != 'pending':
        continue
    deps = phase.get('depends_on', [])
    missing = [d for d in deps if d not in completed_ids]
    if missing:
        print(f'Skipping phase {phase[\"id\"]} — deps {missing} not met')
        continue

    pid = phase['id']
    pname = phase['name']
    print(f'Running phase {pid}: {pname}')

    prompt_script = subprocess.run(
        ['bash', '$0', '--project', '$PROJECT', '--phase', str(pid), '--generate-prompt-only'],
        capture_output=True, text=True
    )

    result = subprocess.run(
        ['claude', '-p', prompt_script.stdout],
        capture_output=True, text=True
    )

    with open(f'$STATE_DIR/phase-{pid}-result.txt', 'w') as f:
        f.write(result.stdout)
        if result.stderr:
            f.write('\n--- stderr ---\n')
            f.write(result.stderr)

    # Mark completed
    phase['status'] = 'completed'
    completed_ids.add(pid)

    with open('$PHASES_FILE', 'w') as f:
        json.dump(data, f, indent=2)

    print(f'Phase {pid} completed')
"
fi

echo "=== Ralph Loop complete ==="
