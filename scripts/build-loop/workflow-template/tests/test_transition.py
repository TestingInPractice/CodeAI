import pytest
import sys, os, json, tempfile, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import transition as tr
from conftest import read_fixture_json


def write_config(wd, transitions=None, phases=None, entry_gates=None, exit_gates=None):
    """Write a config.yaml in transition.py's custom yaml format."""
    lines = []
    if transitions:
        lines.append("transitions:")
        for t in transitions:
            f = t.get("from", "")
            to = t.get("to", "")
            lines.append(f"  - from: {f}")
            lines.append(f"    to: {to}")
            if t.get("emergency"):
                lines.append("    emergency: true")
    if phases:
        lines.append("phases:")
        for p in phases:
            lines.append(f'  - id: "{p["id"]}"')
            lines.append(f'    description: "{p["description"]}"')
    if entry_gates:
        lines.append("entry:")
        lines.append("  - check: " + entry_gates)
    if exit_gates:
        lines.append("exit:")
        lines.append("  - check: " + exit_gates)
    path = os.path.join(wd, ".workflow", "config.yaml")
    with open(path, "w") as f:
        f.write("\n".join(lines))


def setup_workdir(state_override=None):
    wd = tempfile.mkdtemp()
    os.makedirs(os.path.join(wd, ".workflow"))
    s = read_fixture_json("state.json")
    if state_override:
        s.update(state_override)
    with open(os.path.join(wd, ".workflow", "state.json"), "w") as f:
        json.dump(s, f, indent=2)
    with open(os.path.join(wd, ".workflow", "phases.json"), "w") as f:
        json.dump(read_fixture_json("phases.json"), f, indent=2)
    return wd


class TestCanTransition:
    def test_from_any_not_supported(self):
        config = {"transitions": [{"from": "plan-release", "to": "implement-spec-stage"}]}
        assert tr.can_transition("plan-release", "implement-spec-stage", config) is True
        assert tr.can_transition("write-tests", "integrate-release", config) is False

    def test_emergency_bypass(self):
        config = {"transitions": [{"from": "plan-release", "to": "implement-spec-stage"}]}
        # can_transition itself doesn't check emergency — it's done in do_transition
        assert tr.can_transition("plan-release", "implement-spec-stage", config) is True


class TestLock:
    def test_acquire_release(self):
        path = tempfile.mktemp(suffix=".json")
        with open(path, "w") as f:
            f.write("{}")
        fd = tr.acquire_lock(path, timeout=1)
        assert fd is not None
        tr.release_lock(fd, path + ".lock")
        os.unlink(path)


class TestAtomicWrite:
    def test_write_and_read(self):
        data = {"test": "value", "nested": {"a": 1}}
        path = tempfile.mktemp(suffix=".json")
        tr.write_json_atomic(path, data)
        with open(path) as f:
            assert json.load(f) == data
        os.unlink(path)


class TestDoTransition:
    def test_transition_ok(self):
        wd = setup_workdir({"phase": "plan-release", "status": "in_progress"})
        write_config(wd, transitions=[{"from": "plan-release", "to": "implement-spec-stage"}])
        res = tr.do_transition(wd, "implement-spec-stage", "transition")
        assert res["status"] == "ok"
        assert res["phase"] == "implement-spec-stage"
        assert res["new_status"] == "in_progress"
        shutil.rmtree(wd)

    def test_transition_denied(self):
        wd = setup_workdir({"phase": "plan-release", "status": "in_progress"})
        write_config(wd, transitions=[])
        res = tr.do_transition(wd, "write-tests", "transition")
        assert res["status"] == "denied"
        shutil.rmtree(wd)

    def test_wait_resume(self):
        wd = setup_workdir()
        res = tr.do_transition(wd, None, "wait")
        assert res["status"] == "ok"
        with open(os.path.join(wd, ".workflow", "state.json")) as f:
            assert json.load(f)["status"] == "waiting_human"

        res = tr.do_transition(wd, None, "resume")
        assert res["status"] == "ok"
        with open(os.path.join(wd, ".workflow", "state.json")) as f:
            assert json.load(f)["status"] == "in_progress"
        shutil.rmtree(wd)

    def test_complete(self):
        wd = setup_workdir({"phase": "plan-release", "status": "in_progress"})
        write_config(wd, phases=[{"id": "plan-release", "description": "test"}])
        res = tr.do_transition(wd, None, "complete")
        assert res["status"] == "ok"
        with open(os.path.join(wd, ".workflow", "state.json")) as f:
            assert json.load(f)["status"] == "completed"
        shutil.rmtree(wd)

    def test_fail(self):
        wd = setup_workdir({"phase": "plan-release", "status": "in_progress"})
        res = tr.do_transition(wd, None, "fail")
        assert res["status"] == "ok"
        with open(os.path.join(wd, ".workflow", "state.json")) as f:
            assert json.load(f)["status"] == "failed"
        shutil.rmtree(wd)

    def test_override(self):
        wd = setup_workdir({"phase": "plan-release", "status": "in_progress"})
        res = tr.do_transition(wd, "deploy-release", "override")
        assert res["status"] == "ok"
        with open(os.path.join(wd, ".workflow", "state.json")) as f:
            s = json.load(f)
            assert s["phase"] == "deploy-release"
            assert s["emergency"]["active"] is True
        shutil.rmtree(wd)
