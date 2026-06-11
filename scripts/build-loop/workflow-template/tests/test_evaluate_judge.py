import pytest
import sys, os, json, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import evaluate_judge as ej
from conftest import read_fixture_json, read_root_json, read_root_file, FIXTURES

SPEC = read_root_file("tests/fixtures/spec.md")


class TestAnalystStructural:
    def test_all_f_covered(self):
        rubric = read_root_json("judge-rubrics/analyst.json")
        tasks_dir = os.path.join(FIXTURES, "tasks")
        errors, f_ids, count = ej.structural_check_analyst(SPEC, tasks_dir, rubric)
        assert errors == [], f"errors: {errors}"
        assert len(f_ids) == 3
        assert count == 3

    def test_missing_task(self):
        rubric = read_root_json("judge-rubrics/analyst.json")
        spec_no_f3 = SPEC.replace("F-003", "F-099")
        errors, f_ids, count = ej.structural_check_analyst(spec_no_f3, os.path.join(FIXTURES, "tasks"), rubric)
        assert any("requirements_coverage" in e for e in errors), f"expected coverage error, got {errors}"


class TestDeveloperStructural:
    def test_all_completed(self):
        state = read_fixture_json("state.json")
        state["phase"] = "implement-spec-stage"
        errors = ej.structural_check_developer(SPEC, state)
        assert errors == [], f"errors: {errors}"

    def test_not_all_completed(self):
        state = read_fixture_json("state.json")
        state["phase"] = "implement-spec-stage"
        state["implement_spec_stage"]["tasks"][0]["status"] = "pending"
        errors = ej.structural_check_developer(SPEC, state)
        assert any("tasks_not_all_completed" in e for e in errors), f"expected tasks_not_all_completed, got {errors}"

    def test_missing_verdict(self):
        state = read_fixture_json("state.json")
        state["phase"] = "implement-spec-stage"
        state["implement_spec_stage"]["tasks"][0]["judge_verdict"] = None
        errors = ej.structural_check_developer(SPEC, state)
        assert any("task_no_verdict" in e for e in errors), f"expected task_no_verdict, got {errors}"


class TestTesterStructural:
    def test_all_ac_covered(self):
        state = read_fixture_json("state.json")
        errors = ej.structural_check_tester(SPEC, state)
        assert errors == [], f"errors: {errors}"

    def test_missing_coverage(self):
        state = read_fixture_json("state.json")
        state["write_tests"]["test_cases"] = []
        errors = ej.structural_check_tester(SPEC, state)
        assert len(errors) > 0, "expected coverage errors"


class TestAIPrompt:
    def test_build_prompt_exists(self):
        rubric = read_root_json("judge-rubrics/analyst.json")
        prompt = ej.build_ai_prompt("analyst", rubric, ["F-001", "F-002"], 2, [])
        assert "VERDICT" in prompt
        assert "IEEE 29148" in prompt
        assert "F-XXX найдено в spec: 2" in prompt
        assert "Necessary" in prompt

    def test_build_prompt_with_errors(self):
        rubric = read_root_json("judge-rubrics/analyst.json")
        prompt = ej.build_ai_prompt("analyst", rubric, ["F-001"], 1, ["requirements_coverage: missing"])
        assert "requirements_coverage" in prompt


class TestCLIPrepare:
    def test_prepare_analyst(self):
        rubric = os.path.join(ej.__file__ and ".", "..", "judge-rubrics", "analyst.json")
        # Use the full real path
        rubric = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "judge-rubrics", "analyst.json"))
        spec = os.path.join(FIXTURES, "spec.md")
        tasks_dir = os.path.join(FIXTURES, "tasks")

        import argparse
        args = argparse.Namespace(
            mode="prepare",
            rubric=rubric,
            spec=spec,
            tasks_dir=tasks_dir,
            state=""
        )
        rc = ej.cmd_prepare(args)
        assert rc == 0  # structural OK

    def test_prepare_developer(self):
        rubric = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "judge-rubrics", "developer.json"))
        spec = os.path.join(FIXTURES, "spec.md")
        state_path = os.path.join(FIXTURES, "state.json")

        import argparse
        args = argparse.Namespace(
            mode="prepare",
            rubric=rubric,
            spec=spec,
            tasks_dir="",
            state=state_path
        )
        rc = ej.cmd_prepare(args)
        assert rc == 0
