import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import validate_state as vs
import json
from conftest import read_fixture_json, read_root_json


class TestValidateState:
    def test_schema_valid(self):
        state = read_fixture_json("state.json")
        schema = read_root_json("schemas/state.schema.json")
        ok, err = vs.validate_state(state, schema)
        assert ok, f"schema error: {err}"
        assert err is None

    def test_schema_invalid_phase(self):
        state = read_fixture_json("state.json")
        state["phase"] = "invalid-phase"
        schema = read_root_json("schemas/state.schema.json")
        ok, err = vs.validate_state(state, schema)
        assert not ok
        assert err is not None

    def test_schema_missing_required(self):
        state = read_fixture_json("state.json")
        del state["plan_release"]
        schema = read_root_json("schemas/state.schema.json")
        ok, err = vs.validate_state(state, schema)
        assert not ok

    def test_invariants_clean(self):
        state = read_fixture_json("state.json")
        phases = read_fixture_json("phases.json")
        errs = vs.check_invariants(state, phases)
        assert errs == [], f"unexpected invariants: {errs}"

    def test_invariants_sequential_order(self):
        state = read_fixture_json("state.json")
        state["phase"] = "write-tests"
        phases = read_fixture_json("phases.json")
        # Mark implement-spec-stage as not all completed
        phases["phases"][1]["tasks"][0]["status"] = "pending"
        errs = vs.check_invariants(state, phases)
        assert any("INV2" in e for e in errs), f"expected INV2, got {errs}"

    def test_entry_gates_pass(self):
        state = read_fixture_json("state.json")
        state["phase"] = "implement-spec-stage"
        state["implement_spec_stage"]["judge_verdict"] = "passed"
        config = {
            "phases": [
                {"id": "implement-spec-stage", "entry": ["judge: passed"]}
            ]
        }
        errs = vs.check_entry_gates(state, config)
        assert errs == [], f"errors: {errs}"

    def test_entry_gates_blocked(self):
        state = read_fixture_json("state.json")
        state["phase"] = "implement-spec-stage"
        state["implement_spec_stage"]["judge_verdict"] = "failed"
        config = {
            "phases": [
                {"id": "implement-spec-stage", "entry": ["judge: passed"]}
            ]
        }
        errs = vs.check_entry_gates(state, config)
        assert len(errs) > 0, f"expected blocked, got empty"

    def test_exit_gates_pass(self):
        state = read_fixture_json("state.json")
        state["status"] = "completed"
        state["plan_release"]["judge_verdict"] = "passed"
        config = {
            "phases": [
                {"id": "plan-release", "exit": ["judge: passed", "tasks: all_completed"]}
            ]
        }
        errs = vs.check_exit_gates(state, config)
        assert errs == [], f"errors: {errs}"

    def test_exit_gates_not_all_completed(self):
        state = read_fixture_json("state.json")
        state["status"] = "completed"
        state["plan_release"]["tasks"][0]["status"] = "pending"
        config = {
            "phases": [
                {"id": "plan-release", "exit": ["tasks: all_completed"]}
            ]
        }
        errs = vs.check_exit_gates(state, config)
        assert len(errs) > 0, f"expected blocked"

    def test_section_key(self):
        cases = {
            "plan-release": "plan_release",
            "implement-spec-stage": "implement_spec_stage",
            "write-tests": "write_tests",
            "integrate-release": "integrate_release",
            "deploy-release": "deploy_release",
        }
        for k, v in cases.items():
            assert vs._section_key(k) == v, f"{k} -> {v}"
