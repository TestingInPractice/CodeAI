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

STATE_DIR="$PROJECT/.build-loop"
PHASES_FILE="$STATE_DIR/phases.json"

if [ ! -f "$PHASES_FILE" ]; then
  echo "Error: $PHASES_FILE not found. Run decompose.sh first."
  exit 1
fi

python3 -c "
import json, sys

with open('$PHASES_FILE') as f:
    data = json.load(f)

phases = data.get('phases', [])
completed_ids = {p['id'] for p in phases if p.get('status') == 'completed'}
pending = [p for p in phases if p.get('status') == 'pending']

if not pending:
    print('=== All phases completed! 🎉 ===')
    sys.exit(0)

# Find first ready phase (dependencies met)
ready = None
for p in pending:
    deps = p.get('depends_on', [])
    missing = [d for d in deps if d not in completed_ids]
    if not missing:
        ready = p
        break

if not ready:
    print('=== No ready phases — dependencies not met ===')
    for p in pending:
        deps = p.get('depends_on', [])
        missing = [d for d in deps if d not in completed_ids]
        print(f'  ⏳ Phase {p[\"id\"]}: {p.get(\"name\", \"?\")} — waiting for phases {missing}')
    sys.exit(1)

pid = ready['id']
pname = ready.get('name', '?')
desc = ready.get('description', ready.get('summary', ''))
ac = ready.get('acceptance_criteria', ready.get('ac', []))

print('=== Next Phase ===')
print(f'  ID:     {pid}')
print(f'  Name:   {pname}')
if desc:
    print(f'  Desc:   {desc}')
print()
print(f'Pending phases:  {len(pending)}')
print(f'Completed:       {len(completed_ids)}')
print(f'Total:           {len(phases)}')
print()
print('To get the full prompt for this phase:')
print(f'  bash scripts/build-loop/run-loop.sh --project \"$PROJECT\" --phase {pid} --print-prompt')
print()
print('After implementing, mark complete:')
print(f'  bash scripts/build-loop/run-loop.sh --project \"$PROJECT\" --mark-complete {pid}')
"
