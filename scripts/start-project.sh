#!/usr/bin/env bash
# start-project.sh — точка входа для нового проекта (Mode C)
#
# Вызывается AI-оркестратором когда пользователь говорит:
# "сделай проект X, используй наш workflow https://github.com/TestingInPractice/CodeAI"
#
# Usage:
#   bash scripts/start-project.sh \
#     --project /path/to/new-project \
#     --prompt "Сделай todo-приложение на React" \
#     --workflow-repo "https://github.com/TestingInPractice/CodeAI" \
#     --repo-token "ghp_..."
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path> --prompt <string> [--workflow-repo <url>] [--repo-token <token>]"
  exit 1
}

PROJECT=""
PROMPT=""
WORKFLOW_REPO="https://github.com/TestingInPractice/CodeAI"
REPO_TOKEN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p)       PROJECT="$2"; shift 2 ;;
    --prompt)           PROMPT="$2"; shift 2 ;;
    --workflow-repo)    WORKFLOW_REPO="$2"; shift 2 ;;
    --repo-token)       REPO_TOKEN="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[ -z "$PROJECT" ] && usage
[ -z "$PROMPT" ] && usage

WORKFLOW_DIR="/tmp/codeai-workflow"
PROMPT_FILE="/tmp/project-prompt.txt"

echo "╔═══════════════════════════════════════════════╗"
echo "║  Build Loop Mode C — Start Project            ║"
echo "╚═══════════════════════════════════════════════╝"
echo "Project: $PROJECT"
echo "Workflow repo: $WORKFLOW_REPO"
echo ""

# Step 1: Save prompt
echo "$PROMPT" > "$PROMPT_FILE"
echo "Prompt saved to $PROMPT_FILE"

# Step 2: Clone workflow repo (if not already present)
if [ ! -d "$WORKFLOW_DIR/.git" ]; then
  echo ""
  echo "--- Cloning workflow repo ---"
  if [ -n "$REPO_TOKEN" ]; then
    AUTH_REPO=$(echo "$WORKFLOW_REPO" | sed "s|https://|https://x-access-token:${REPO_TOKEN}@|")
    git clone --single-branch --depth 1 "$AUTH_REPO" "$WORKFLOW_DIR"
  else
    git clone --single-branch --depth 1 "$WORKFLOW_REPO" "$WORKFLOW_DIR"
  fi
  echo "  Cloned to $WORKFLOW_DIR"
else
  echo "  Workflow repo already at $WORKFLOW_DIR"
fi

# Step 3: Create project directory
mkdir -p "$PROJECT"

# Step 4: Run setup (installs GStack, GSD, Superpowers)
echo ""
echo "--- Running setup ---"
bash "$WORKFLOW_DIR/scripts/build-loop/setup.sh"

# Step 5: Run init (creates docs/specs/ skeleton, copies judge)
echo ""
echo "--- Initializing project ---"
bash "$WORKFLOW_DIR/scripts/build-loop/init.sh" --project "$PROJECT"

# Step 6: Set initial workflow state
echo ""
echo "--- Setting initial state ---"
python3 "$WORKFLOW_DIR/scripts/transition.py" --project "$PROJECT" start --phase setup --value ""
python3 "$WORKFLOW_DIR/scripts/transition.py" --project "$PROJECT" set --key "prompt" --value "$PROMPT"
python3 "$WORKFLOW_DIR/scripts/transition.py" --project "$PROJECT" set --key "workflow_repo" --value "$WORKFLOW_REPO"

# Step 7: Copy the full spec template from workflow-template
echo ""
echo "--- Setting up spec template ---"
TEMPLATE="$WORKFLOW_DIR/scripts/build-loop/workflow-template/templates/specs/requirements.md"
if [ -f "$TEMPLATE" ]; then
  cp "$TEMPLATE" "$PROJECT/docs/specs/goals.md"
  echo "  Copied requirements.md template → docs/specs/goals.md"
fi

# Step 8: Transition to spec phase
python3 "$WORKFLOW_DIR/scripts/transition.py" --project "$PROJECT" start --phase spec

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  Project initialized. Ready for spec phase.   ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Next: The orchestrator reads the prompt and generates the spec"
echo "  via GStack or direct AI prompt. Then judge checks the spec"
echo "  and hands over to human for review."
echo ""
echo "State file: $PROJECT/.workflow/state.json"
echo "Workflow:   $WORKFLOW_DIR"
