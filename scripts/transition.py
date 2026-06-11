#!/usr/bin/env python3
"""
transition.py — управление состоянием Build Loop Mode C.

Состояния:
  setup → spec → human_gate → decompose → task_cycle → complete

Статусы:
  pending | in_progress | waiting_human | completed | failed

Usage:
  python3 scripts/transition.py --project . --action start --phase spec
  python3 scripts/transition.py --project . --action transition
  python3 scripts/transition.py --project . --action approve
  python3 scripts/transition.py --project . --action fail --reason "..."
  python3 scripts/transition.py --project . --status
"""

import json, os, sys, argparse

WORKFLOW_DIR = ".workflow"
STATE_FILE = "state.json"

PHASE_ORDER = ["setup", "spec", "human_gate", "decompose", "task_cycle", "complete"]


def get_state_path(project):
    return os.path.join(project, WORKFLOW_DIR, STATE_FILE)


def load_state(project):
    path = get_state_path(project)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"phase": "setup", "status": "pending", "current_task": "", "questions": [], "judge_verdict": "", "version": "1.0"}


def save_state(project, state):
    path = get_state_path(project)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def cmd_start(args):
    state = load_state(args.project)
    state["phase"] = args.phase
    state["status"] = "in_progress"
    state["judge_verdict"] = ""
    save_state(args.project, state)
    print(json.dumps(state, indent=2))
    return 0


def cmd_transition(args):
    state = load_state(args.project)
    if state["status"] == "waiting_human":
        print(f"Error: phase '{state['phase']}' is waiting_human — use --action approve first")
        return 1
    current = state["phase"]
    if current not in PHASE_ORDER:
        print(f"Error: unknown phase '{current}'")
        return 1
    idx = PHASE_ORDER.index(current)
    if idx >= len(PHASE_ORDER) - 1:
        print("All phases completed")
        state["status"] = "completed"
        save_state(args.project, state)
        return 0
    next_phase = PHASE_ORDER[idx + 1]
    state["phase"] = next_phase
    state["status"] = "pending"
    state["judge_verdict"] = ""
    save_state(args.project, state)
    print(json.dumps(state, indent=2))
    return 0


def cmd_approve(args):
    state = load_state(args.project)
    if state["status"] != "waiting_human":
        print("Error: phase is not waiting_human")
        return 1
    state["status"] = "completed"
    save_state(args.project, state)
    print(json.dumps(state, indent=2))
    return 0


def cmd_fail(args):
    state = load_state(args.project)
    state["status"] = "failed"
    if args.reason:
        state["fail_reason"] = args.reason
    save_state(args.project, state)
    print(json.dumps(state, indent=2))
    return 0


def cmd_judge(args):
    state = load_state(args.project)
    state["judge_verdict"] = args.verdict
    state["judge_report"] = args.report or {}
    save_state(args.project, state)
    print(json.dumps({"judge_verdict": args.verdict}))
    return 0


def cmd_set(args):
    state = load_state(args.project)
    key, val = args.key, args.value
    state[key] = val
    save_state(args.project, state)
    print(json.dumps({key: val}))
    return 0


def cmd_status(args):
    state = load_state(args.project)
    print(json.dumps(state, indent=2))
    return 0


def cmd_human_gate(args):
    state = load_state(args.project)
    state["status"] = "waiting_human"
    if args.questions:
        state["questions"] = json.loads(args.questions)
    save_state(args.project, state)
    print(f"  Status: waiting_human")
    print(f"  Questions: {len(state['questions'])}")
    for q in state["questions"]:
        print(f"    - {q}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Build Loop Mode C — state machine")
    p.add_argument("--project", "-p", required=True)
    sub = p.add_subparsers(dest="action", required=True)

    s = sub.add_parser("start", help="Начать фазу")
    s.add_argument("--phase", required=True)

    t = sub.add_parser("transition", help="Перейти к следующей фазе")

    a = sub.add_parser("approve", help="Утвердить (выйти из waiting_human)")

    f = sub.add_parser("fail", help="Отметить как failed")
    f.add_argument("--reason", default="")

    j = sub.add_parser("judge", help="Записать verdict судьи")
    j.add_argument("--verdict", required=True)
    j.add_argument("--report", default="{}")

    setp = sub.add_parser("set", help="Установить произвольное поле")
    setp.add_argument("--key", required=True)
    setp.add_argument("--value", required=True)

    st = sub.add_parser("status", help="Показать текущее состояние")

    hg = sub.add_parser("human-gate", help="Поставить waiting_human")
    hg.add_argument("--questions", default="[]")

    args = p.parse_args()
    cmds = {
        "start": cmd_start,
        "transition": cmd_transition,
        "approve": cmd_approve,
        "fail": cmd_fail,
        "judge": cmd_judge,
        "set": cmd_set,
        "status": cmd_status,
        "human-gate": cmd_human_gate,
    }
    sys.exit(cmds[args.action](args))
