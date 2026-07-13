"""Integration Test: Architecture Validation.

Automatically validates:
- Dependency Rule (no upward imports, no circular imports)
- Frozen API (public methods match CORE_RUNTIME.md)
- Type contracts (frozen dataclasses, invariants)
- ADR compliance
"""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

CORE = Path(__file__).parent.parent.parent / "scripts" / "core"


def _read_source(module_path: Path) -> str:
    return module_path.read_text(encoding="utf-8")


def _find_imports(source: str) -> set[str]:
    """Extract all import module names from source."""
    tree = ast.parse(source)
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
    return modules


class TestDependencyRule(unittest.TestCase):
    """Verify no upward or circular imports."""

    def test_types_do_not_import_engines(self):
        """types/ must not import from engine modules."""
        forbidden = {
            "scripts.core.workflow_engine",
            "scripts.core.judge_engine",
            "scripts.core.ooda_runtime",
            "scripts.core.knowledge_layer",
            "scripts.core.memory_layer",
            "scripts.core.event_bus",
        }
        types_dir = CORE / "types"
        for py in types_dir.glob("*.py"):
            imports = _find_imports(_read_source(py))
            violations = imports & forbidden
            self.assertEqual(
                violations, set(),
                f"{py.name} imports engines: {violations}",
            )

    def test_engines_do_not_import_each_other(self):
        """Engine modules must not import other engines directly."""
        engines = {
            "workflow_engine.py": {
                "scripts.core.judge_engine",
                "scripts.core.ooda_runtime",
                "scripts.core.knowledge_layer",
                "scripts.core.memory_layer",
            },
            "judge_engine.py": {
                "scripts.core.workflow_engine",
                "scripts.core.ooda_runtime",
                "scripts.core.knowledge_layer",
                "scripts.core.memory_layer",
            },
            "ooda_runtime.py": {
                "scripts.core.workflow_engine",
                "scripts.core.judge_engine",
            },
            "knowledge_layer.py": {
                "scripts.core.workflow_engine",
                "scripts.core.judge_engine",
                "scripts.core.ooda_runtime",
                "scripts.core.memory_layer",
            },
            "memory_layer.py": {
                "scripts.core.workflow_engine",
                "scripts.core.judge_engine",
                "scripts.core.ooda_runtime",
                "scripts.core.knowledge_layer",
            },
        }
        for filename, forbidden in engines.items():
            filepath = CORE / filename
            if not filepath.exists():
                continue
            imports = _find_imports(_read_source(filepath))
            violations = imports & forbidden
            self.assertEqual(
                violations, set(),
                f"{filename} imports other engines: {violations}",
            )

    def test_ooda_steps_do_not_import_judge(self):
        """OODA steps must not import Judge Engine."""
        ooda_dir = CORE / "ooda"
        for py in ooda_dir.glob("*.py"):
            imports = _find_imports(_read_source(py))
            self.assertNotIn(
                "scripts.core.judge_engine",
                imports,
                f"ooda/{py.name} imports judge_engine",
            )

    def test_knowledge_independent_of_memory(self):
        """Knowledge Layer must not import Memory Layer."""
        kl = CORE / "knowledge_layer.py"
        imports = _find_imports(_read_source(kl))
        self.assertNotIn("scripts.core.memory_layer", imports)

    def test_memory_independent_of_knowledge(self):
        """Memory Layer must not import Knowledge Layer."""
        ml = CORE / "memory_layer.py"
        imports = _find_imports(_read_source(ml))
        self.assertNotIn("scripts.core.knowledge_layer", imports)


class TestFrozenAPI(unittest.TestCase):
    """Verify public API matches CORE_RUNTIME.md."""

    def test_workflow_engine_methods(self):
        from scripts.core.workflow_engine import WorkflowEngine
        methods = {"start", "next", "complete", "rollback", "state"}
        actual = {m for m in dir(WorkflowEngine) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")

    def test_ooda_runtime_methods(self):
        from scripts.core.ooda_runtime import OODARuntime
        methods = {"execute", "resume", "interrupt"}
        actual = {m for m in dir(OODARuntime) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")

    def test_knowledge_layer_methods(self):
        from scripts.core.knowledge_layer import KnowledgeLayer
        methods = {"search", "retrieve", "index", "index_all"}
        actual = {m for m in dir(KnowledgeLayer) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")

    def test_memory_layer_methods(self):
        from scripts.core.memory_layer import MemoryLayer
        methods = {"store", "load", "summarize"}
        actual = {m for m in dir(MemoryLayer) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")

    def test_judge_engine_methods(self):
        from scripts.core.judge_engine import JudgeEngine
        methods = {"evaluate", "score", "route"}
        actual = {m for m in dir(JudgeEngine) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")

    def test_event_bus_methods(self):
        from scripts.core.event_bus import EventBus
        methods = {"subscribe", "unsubscribe", "publish", "publish_raw"}
        actual = {m for m in dir(EventBus) if not m.startswith("_")}
        self.assertTrue(methods.issubset(actual), f"Missing: {methods - actual}")


class TestTypeContracts(unittest.TestCase):
    """Verify type invariants."""

    def test_knowledge_is_frozen(self):
        from scripts.core.types.knowledge import Knowledge
        self.assertTrue(Knowledge.__dataclass_params__.frozen)

    def test_verdict_is_frozen(self):
        from scripts.core.types.judge import Verdict
        self.assertTrue(Verdict.__dataclass_params__.frozen)

    def test_score_is_frozen(self):
        from scripts.core.types.judge import Score
        self.assertTrue(Score.__dataclass_params__.frozen)

    def test_route_action_is_frozen(self):
        from scripts.core.types.judge import RouteAction
        self.assertTrue(RouteAction.__dataclass_params__.frozen)

    def test_rubric_is_frozen(self):
        from scripts.core.types.judge import Rubric
        self.assertTrue(Rubric.__dataclass_params__.frozen)

    def test_rubric_criterion_is_frozen(self):
        from scripts.core.types.judge import RubricCriterion
        self.assertTrue(RubricCriterion.__dataclass_params__.frozen)

    def test_event_has_event_id(self):
        from scripts.core.types.common import Event
        from uuid import UUID
        e = Event(name="test", source="test")
        self.assertIsInstance(e.event_id, UUID)

    def test_event_has_correlation_id(self):
        from scripts.core.types.common import Event
        e = Event(name="test", source="test")
        self.assertIsNone(e.correlation_id)

    def test_memory_entry_has_content_hash(self):
        from scripts.core.types.memory import MemoryEntry
        from uuid import uuid4
        from scripts.core.enums import MemoryType
        e = MemoryEntry(id=uuid4(), type=MemoryType.DECISIONS, content="test")
        self.assertEqual(e.content_hash, "")

    def test_memory_entry_has_version(self):
        from scripts.core.types.memory import MemoryEntry
        from uuid import uuid4
        from scripts.core.enums import MemoryType
        e = MemoryEntry(id=uuid4(), type=MemoryType.DECISIONS, content="test")
        self.assertEqual(e.version, 1)


class TestADRArchitecture(unittest.TestCase):
    """Verify ADR compliance."""

    def test_adr_0001_exists(self):
        adr_path = Path(__file__).parent.parent.parent / "docs" / "architecture" / "adr"
        files = list(adr_path.glob("ADR-0001*"))
        self.assertTrue(len(files) > 0, "ADR-0001 not found")

    def test_architecture_freeze_exists(self):
        freeze_path = Path(__file__).parent.parent.parent / "docs" / "architecture" / "ARCHITECTURE_FREEZE.md"
        self.assertTrue(freeze_path.exists())

    def test_core_runtime_exists(self):
        cr_path = Path(__file__).parent.parent.parent / "docs" / "architecture" / "CORE_RUNTIME.md"
        self.assertTrue(cr_path.exists())

    def test_all_subsystems_have_implementation(self):
        """All 6 subsystems + Event Bus have implementations."""
        required = [
            "workflow_engine.py",
            "judge_engine.py",
            "ooda_runtime.py",
            "knowledge_layer.py",
            "memory_layer.py",
            "event_bus.py",
        ]
        for name in required:
            path = CORE / name
            self.assertTrue(path.exists(), f"Missing: {name}")

    def test_error_hierarchy_exists(self):
        from scripts.core.errors import (
            CodeAIError,
            SpecError,
            WorkflowError,
            OODAError,
            KnowledgeError,
            MemoryError,
            JudgeError,
        )
        self.assertTrue(issubclass(WorkflowError, CodeAIError))
        self.assertTrue(issubclass(OODAError, CodeAIError))
        self.assertTrue(issubclass(KnowledgeError, CodeAIError))
        self.assertTrue(issubclass(MemoryError, CodeAIError))
        self.assertTrue(issubclass(JudgeError, CodeAIError))


if __name__ == "__main__":
    unittest.main()
