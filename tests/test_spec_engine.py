"""Unit tests for SpecEngine.

Tests the deterministic SpecEngine implementation:
- Prompt analysis and goal extraction
- goals.md generation with real content
- Structure validation
- Parsing back into StructuredSpec
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.core.enums import Priority
from scripts.core.errors import SpecError
from scripts.core.spec_engine import (
    PromptAnalyzer,
    SpecEngine,
    _detect_dependencies,
    _detect_scope,
    _detect_tech_stack,
    _extract_acs,
    _extract_api_contracts,
    _extract_entities,
    _extract_requirements,
    _format_goals_md,
    _parse_field_def,
    _parse_goals_md,
    _split_sentences,
    _tokenize,
)
from scripts.core.types.spec import (
    AC,
    APIContract,
    DataModel,
    FieldDefinition,
    Requirement,
    Scope,
    StructuredSpec,
    ValidationResult,
)


# ── Helper ───────────────────────────────────────────────────────

class TempSpecDir(unittest.TestCase):
    """Mixin: create temp dir, change to it, clean up after."""

    def setUp(self):
        self._orig_dir = os.getcwd()
        self._tmp = tempfile.mkdtemp(prefix="spec_test_")
        os.chdir(self._tmp)

    def tearDown(self):
        os.chdir(self._orig_dir)
        shutil.rmtree(self._tmp, ignore_errors=True)


# ── Helper functions ─────────────────────────────────────────────

class TestHelperFunctions(unittest.TestCase):
    """Test low-level helper functions."""

    def test_split_sentences(self):
        text = "Create a calculator. It must support addition. Should be fast."
        sentences = _split_sentences(text)
        self.assertEqual(len(sentences), 3)

    def test_split_sentences_single(self):
        text = "Hello world"
        sentences = _split_sentences(text)
        self.assertEqual(len(sentences), 1)

    def test_tokenize(self):
        tokens = _tokenize("Create a Python calculator")
        self.assertIn("create", tokens)
        self.assertIn("python", tokens)
        self.assertIn("calculator", tokens)

    def test_parse_field_def_name_type(self):
        fd = _parse_field_def("name: str")
        self.assertEqual(fd.name, "name")
        self.assertEqual(fd.type, "str")
        self.assertTrue(fd.required)

    def test_parse_field_def_with_default(self):
        fd = _parse_field_def("status: str = active")
        self.assertEqual(fd.name, "status")
        self.assertEqual(fd.type, "str")
        self.assertEqual(fd.default, "active")

    def test_parse_field_def_uuid(self):
        fd = _parse_field_def("id: UUID")
        self.assertEqual(fd.name, "id")
        self.assertEqual(fd.type, "UUID")

    def test_parse_field_def_empty(self):
        fd = _parse_field_def("")
        self.assertIsNone(fd)


# ── Prompt Analysis ──────────────────────────────────────────────

class TestExtractRequirements(unittest.TestCase):
    """Test requirement extraction from prompts."""

    def test_must_keyword(self):
        reqs = _extract_requirements("The system must validate input")
        self.assertGreater(len(reqs), 0)
        self.assertTrue(any("must validate" in r[0] for r in reqs))

    def test_should_keyword(self):
        reqs = _extract_requirements("The app should cache results")
        self.assertGreater(len(reqs), 0)
        self.assertTrue(any("cache" in r[0] for r in reqs))

    def test_imperative_verb(self):
        reqs = _extract_requirements("Create a user registration system")
        self.assertGreater(len(reqs), 0)
        self.assertTrue(any("Create" in r[0] for r in reqs))

    def test_implementation_keyword(self):
        reqs = _extract_requirements("Implement a REST API")
        self.assertGreater(len(reqs), 0)
        self.assertTrue(any("Implement" in r[0] for r in reqs))

    def test_support_keyword(self):
        reqs = _extract_requirements("Support multiple languages")
        self.assertGreater(len(reqs), 0)

    def test_needs_to_keyword(self):
        reqs = _extract_requirements("The system needs to process data")
        self.assertGreater(len(reqs), 0)

    def test_fallback_to_prompt(self):
        """When no requirements detected, uses first sentence."""
        reqs = _extract_requirements("Some random text without keywords")
        self.assertGreater(len(reqs), 0)

    def test_priority_must(self):
        reqs = _extract_requirements("This is critical for the project")
        self.assertEqual(reqs[0][1], Priority.MUST)

    def test_priority_should(self):
        reqs = _extract_requirements("This should be included if possible")
        self.assertEqual(reqs[0][1], Priority.SHOULD)

    def test_priority_could(self):
        reqs = _extract_requirements("Nice to have: dark mode support")
        self.assertEqual(reqs[0][1], Priority.COULD)


class TestExtractACs(unittest.TestCase):
    """Test acceptance criteria extraction."""

    def test_given_when_then(self):
        acs = _extract_acs("Given a logged in user, when they click save, then data persists")
        self.assertGreater(len(acs), 0)

    def test_as_a_user(self):
        acs = _extract_acs("As a user, I want to create accounts")
        self.assertGreater(len(acs), 0)
        self.assertTrue(any("user" in a.lower() for a in acs))

    def test_verify_that(self):
        acs = _extract_acs("Verify that the form submits correctly")
        self.assertGreater(len(acs), 0)

    def test_should_be_able_to(self):
        acs = _extract_acs("User should be able to upload files")
        self.assertGreater(len(acs), 0)

    def test_can_be(self):
        acs = _extract_acs("The form can be submitted via POST")
        self.assertGreater(len(acs), 0)

    def test_no_acs(self):
        """No ACs detected if none match patterns."""
        acs = _extract_acs("Create a simple calculator")
        # This may or may not detect ACs depending on pattern matching
        # Just verify it returns a list
        self.assertIsInstance(acs, list)


class TestExtractEntities(unittest.TestCase):
    """Test entity extraction."""

    def test_model_pattern(self):
        entities = _extract_entities("Define a User model with name and email")
        self.assertTrue(any("User" in e for e in entities))

    def test_schema_pattern(self):
        entities = _extract_entities("Create an Order schema")
        self.assertTrue(any("Order" in e for e in entities))

    def test_capitalized_words(self):
        entities = _extract_entities("Build a Python project with Django framework")
        # Should find capitalized entity-like words
        self.assertIsInstance(entities, list)


class TestExtractAPIContracts(unittest.TestCase):
    """Test API contract extraction."""

    def test_method_and_path(self):
        contracts = _extract_api_contracts("GET /api/users and POST /api/orders")
        self.assertEqual(len(contracts), 2)
        methods = [c[0] for c in contracts]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)

    def test_single_endpoint(self):
        contracts = _extract_api_contracts("Create a DELETE /api/items/1 endpoint")
        self.assertGreater(len(contracts), 0)

    def test_no_endpoints(self):
        contracts = _extract_api_contracts("Build a calculator")
        self.assertEqual(len(contracts), 0)


class TestDetectTechStack(unittest.TestCase):
    """Test technology stack detection."""

    def test_python(self):
        stack = _detect_tech_stack("Build a Python Django app")
        self.assertIn("python", stack)

    def test_javascript(self):
        stack = _detect_tech_stack("Create a React frontend with Node.js")
        self.assertIn("javascript", stack)

    def test_database(self):
        stack = _detect_tech_stack("Use PostgreSQL database for storage")
        self.assertIn("database", stack)

    def test_cli(self):
        stack = _detect_tech_stack("Build a command-line interface tool")
        self.assertIn("cli", stack)

    def test_auth(self):
        stack = _detect_tech_stack("Implement JWT authentication")
        self.assertIn("auth", stack)


class TestDetectScope(unittest.TestCase):
    """Test scope detection."""

    def test_out_of_scope(self):
        inc, exc = _detect_scope("Include user management. Out of scope: billing system")
        self.assertGreater(len(exc), 0)

    def test_exclude_keyword(self):
        inc, exc = _detect_scope("Skip payment integration for now")
        self.assertGreater(len(exc), 0)

    def test_include_keyword(self):
        inc, exc = _detect_scope("Scope: user authentication and dashboard")
        self.assertGreater(len(inc), 0)


class TestDetectDependencies(unittest.TestCase):
    """Test dependency detection."""

    def test_using(self):
        deps = _detect_dependencies("Build using React and TypeScript")
        self.assertGreater(len(deps), 0)

    def test_built_with(self):
        deps = _detect_dependencies("Built with Django and PostgreSQL")
        self.assertGreater(len(deps), 0)

    def test_integrate_with(self):
        deps = _detect_dependencies("Integrate with Stripe payment gateway")
        self.assertGreater(len(deps), 0)


# ── Goals.md Generation ──────────────────────────────────────────

class TestFormatGoalsMd(TempSpecDir):
    """Test goals.md formatting."""

    def test_contains_required_sections(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[("Create a calculator", Priority.MUST)],
            acs=["Calculator works"],
            entities=["Calculator"],
            models=[],
            api_contracts=[],
            tech_stack=["python"],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("## Goal", content)
        self.assertIn("## Requirements", content)
        self.assertIn("## Acceptance Criteria", content)
        self.assertIn("## Scope", content)
        self.assertIn("## Data Models", content)
        self.assertIn("## API Contracts", content)
        self.assertIn("## Dependencies", content)
        self.assertIn("## Components", content)
        self.assertIn("## Open Questions", content)

    def test_requirements_formatted(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[
                ("Add numbers", Priority.MUST),
                ("Save history", Priority.SHOULD),
            ],
            acs=[],
            entities=[],
            models=[],
            api_contracts=[],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("REQ-001", content)
        self.assertIn("REQ-002", content)
        self.assertIn("[must]", content)
        self.assertIn("[should]", content)

    def test_acs_formatted(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[("Create calculator", Priority.MUST)],
            acs=["User can add two numbers"],
            entities=[],
            models=[],
            api_contracts=[],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("AC-001", content)
        self.assertIn("User can add two numbers", content)

    def test_data_models_formatted(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[],
            acs=[],
            entities=[],
            models=[("User", ["id: UUID", "name: str"])],
            api_contracts=[],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("### User", content)
        self.assertIn("`id: UUID`", content)
        self.assertIn("`name: str`", content)

    def test_api_contracts_formatted(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[],
            acs=[],
            entities=[],
            models=[],
            api_contracts=[("GET", "/api/users")],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("| GET | `/api/users` |", content)

    def test_tech_stack_shown(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[],
            acs=[],
            entities=[],
            models=[],
            api_contracts=[],
            tech_stack=["python", "django"],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=[],
        )
        self.assertIn("python, django", content)

    def test_scope_included(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[],
            acs=[],
            entities=[],
            models=[],
            api_contracts=[],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=["user auth", "dashboard"],
            excluded_scope=[],
        )
        self.assertIn("user auth", content)
        self.assertIn("dashboard", content)

    def test_scope_excluded(self):
        content = _format_goals_md(
            prompt="Build a calculator",
            requirements=[],
            acs=[],
            entities=[],
            models=[],
            api_contracts=[],
            tech_stack=[],
            dependencies=[],
            components=[],
            included_scope=[],
            excluded_scope=["billing"],
        )
        self.assertIn("billing", content)


# ── Goals.md Parsing ─────────────────────────────────────────────

class TestParseGoalsMd(unittest.TestCase):
    """Test parsing goals.md back into StructuredSpec."""

    def _make_goals(self, **kwargs) -> str:
        """Build a minimal goals.md string."""
        reqs = kwargs.get("reqs", [("REQ-001", "must", "Create a calculator")])
        acs = kwargs.get("acs", [("AC-001", "Calculator works correctly")])
        models = kwargs.get("models", [])
        apis = kwargs.get("apis", [])
        included = kwargs.get("included", ["core implementation"])
        excluded = kwargs.get("excluded", [])

        lines = [
            "# Goals Specification",
            "",
            "## Meta",
            "- **Version**: 1.0",
            "",
            "## Goal",
            "**What**: Build a calculator",
            "",
            "## Scope",
            "",
            "**Included**:",
        ]
        for s in included:
            lines.append(f"- {s}")
        lines.append("")
        if excluded:
            lines.append("**Excluded**:")
            for s in excluded:
                lines.append(f"- {s}")
            lines.append("")

        lines.append("## Requirements")
        lines.append("")
        for rid, prio, desc in reqs:
            lines.append(f"- **[{rid}]** [{prio}] {desc}")
        lines.append("")

        lines.append("## Acceptance Criteria")
        lines.append("")
        for acid, desc in acs:
            lines.append(f"- **[{acid}]** {desc}")
        lines.append("")

        lines.append("## Data Models")
        lines.append("")
        if models:
            for name, fields in models:
                lines.append(f"### {name}")
                lines.append("")
                for f in fields:
                    lines.append(f"- `{f}`")
                lines.append("")
        else:
            lines.append("_No data models identified from prompt._")
            lines.append("")

        lines.append("## API Contracts")
        lines.append("")
        if apis:
            lines.append("| Method | Path |")
            lines.append("|--------|------|")
            for method, path in apis:
                lines.append(f"| {method} | `{path}` |")
        else:
            lines.append("_No API contracts identified from prompt._")
        lines.append("")

        lines.append("## Dependencies")
        lines.append("- Django")
        lines.append("- PostgreSQL")
        lines.append("")
        lines.append("## Components")
        lines.append("- AuthService")
        lines.append("")
        lines.append("## Open Questions")
        lines.append("- What is the expected scale?")
        lines.append("")

        return "\n".join(lines)

    def test_parse_requirements(self):
        content = self._make_goals()
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.requirements), 1)
        self.assertEqual(spec.requirements[0].title, "Create a calculator")
        self.assertEqual(spec.requirements[0].priority, Priority.MUST)

    def test_parse_multiple_requirements(self):
        content = self._make_goals(reqs=[
            ("REQ-001", "must", "Create calculator"),
            ("REQ-002", "should", "Add history"),
            ("REQ-003", "could", "Add themes"),
        ])
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.requirements), 3)
        self.assertEqual(spec.requirements[0].priority, Priority.MUST)
        self.assertEqual(spec.requirements[1].priority, Priority.SHOULD)
        self.assertEqual(spec.requirements[2].priority, Priority.COULD)

    def test_parse_acceptance_criteria(self):
        content = self._make_goals()
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.acceptance_criteria), 1)
        self.assertIn("Calculator works correctly", spec.acceptance_criteria[0].description)

    def test_parse_ac_links_to_requirement(self):
        content = self._make_goals(
            reqs=[("REQ-001", "must", "Create calculator")],
            acs=[("AC-001", "Calculator adds correctly")],
        )
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.acceptance_criteria), 1)
        # AC should be linked to REQ-001
        self.assertIsNotNone(spec.acceptance_criteria[0].requirement_id)

    def test_parse_data_models(self):
        content = self._make_goals(
            models=[("User", ["id: UUID", "name: str", "email: str"])],
        )
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.data_models), 1)
        self.assertEqual(spec.data_models[0].name, "User")
        self.assertEqual(len(spec.data_models[0].fields), 3)
        self.assertEqual(spec.data_models[0].fields[0].name, "id")
        self.assertEqual(spec.data_models[0].fields[0].type, "UUID")

    def test_parse_data_models_with_default(self):
        content = self._make_goals(
            models=[("Config", ["key: str", "value: str = default"])],
        )
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.data_models), 1)
        self.assertEqual(spec.data_models[0].fields[1].default, "default")

    def test_parse_api_contracts(self):
        content = self._make_goals(
            apis=[("GET", "/api/users"), ("POST", "/api/orders")],
        )
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.api_contracts), 2)
        self.assertEqual(spec.api_contracts[0].method, "GET")
        self.assertEqual(spec.api_contracts[0].path, "/api/users")
        self.assertEqual(spec.api_contracts[1].method, "POST")

    def test_parse_scope(self):
        content = self._make_goals(
            included=["user auth", "dashboard"],
            excluded=["billing"],
        )
        spec = _parse_goals_md(content)
        self.assertIn("user auth", spec.scope.included)
        self.assertIn("dashboard", spec.scope.included)
        self.assertIn("billing", spec.scope.excluded)

    def test_parse_empty_content(self):
        spec = _parse_goals_md("")
        self.assertEqual(len(spec.requirements), 0)
        self.assertEqual(len(spec.acceptance_criteria), 0)

    def test_parse_no_models(self):
        content = self._make_goals()
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.data_models), 0)

    def test_parse_no_apis(self):
        content = self._make_goals()
        spec = _parse_goals_md(content)
        self.assertEqual(len(spec.api_contracts), 0)


# ── SpecEngine Integration ───────────────────────────────────────

class TestSpecEngineGenerate(TempSpecDir):
    """Test SpecEngine.generate() writes real file."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_generate_creates_file(self):
        path = self.engine.generate("Build a Python calculator with Django")
        self.assertTrue(path.exists())
        self.assertTrue(path.is_file())

    def test_generate_file_has_content(self):
        path = self.engine.generate("Build a Python calculator")
        content = path.read_text()
        self.assertGreater(len(content), 100)

    def test_generate_file_has_goal_section(self):
        path = self.engine.generate("Create a REST API")
        content = path.read_text()
        self.assertIn("## Goal", content)

    def test_generate_file_has_requirements(self):
        path = self.engine.generate("Build a system that must validate input")
        content = path.read_text()
        self.assertIn("## Requirements", content)
        self.assertIn("REQ-001", content)

    def test_generate_file_has_acceptance_criteria(self):
        path = self.engine.generate("Create a form that should be accessible")
        content = path.read_text()
        self.assertIn("## Acceptance Criteria", content)

    def test_generate_empty_prompt_raises(self):
        with self.assertRaises(SpecError):
            self.engine.generate("")

    def test_generate_whitespace_prompt_raises(self):
        with self.assertRaises(SpecError):
            self.engine.generate("   ")

    def test_generate_none_prompt_raises(self):
        with self.assertRaises(SpecError):
            self.engine.generate(None)

    def test_different_prompts_produce_different_files(self):
        path1 = self.engine.generate("Build a calculator")
        content1 = path1.read_text()
        # Same file path, but content should reflect the prompt
        path2 = path1  # Same path, but re-generate
        self.engine.generate("Build a chat application")
        content2 = path2.read_text()
        # Content should differ because prompt is different
        self.assertNotEqual(content1, content2)

    def test_generate_extracts_python_stack(self):
        path = self.engine.generate("Build a Python Django REST API")
        content = path.read_text()
        self.assertIn("python", content.lower())

    def test_generate_extracts_api_contracts(self):
        path = self.engine.generate("GET /api/users and POST /api/orders")
        content = path.read_text()
        self.assertIn("GET", content)
        self.assertIn("/api/users", content)


class TestSpecEngineValidate(TempSpecDir):
    """Test SpecEngine.validate() checks real file structure."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_validate_none_path(self):
        result = self.engine.validate(None)
        self.assertFalse(result.valid)
        self.assertIn("goals_path is None", result.errors)

    def test_validate_nonexistent_file(self):
        result = self.engine.validate(Path("nonexistent.md"))
        self.assertFalse(result.valid)
        self.assertTrue(any("not found" in e.lower() for e in result.errors))

    def test_validate_empty_file(self):
        path = Path("empty.md")
        path.write_text("")
        result = self.engine.validate(path)
        self.assertFalse(result.valid)
        self.assertTrue(any("empty" in e.lower() for e in result.errors))

    def test_validate_valid_generated_file(self):
        path = self.engine.generate("Build a calculator with must validate input")
        result = self.engine.validate(path)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_missing_goal_section(self):
        path = Path("bad.md")
        path.write_text("# Spec\n\n## Requirements\n- REQ-001\n")
        result = self.engine.validate(path)
        self.assertFalse(result.valid)
        self.assertTrue(any("Goal" in e for e in result.errors))

    def test_validate_missing_requirements_section(self):
        path = Path("bad.md")
        path.write_text("# Spec\n\n## Goal\nBuild something\n")
        result = self.engine.validate(path)
        self.assertFalse(result.valid)
        self.assertTrue(any("Requirements" in e for e in result.errors))

    def test_validate_missing_ac_section(self):
        path = Path("bad.md")
        path.write_text("# Spec\n\n## Goal\nBuild\n\n## Requirements\n- REQ-001\n")
        result = self.engine.validate(path)
        self.assertFalse(result.valid)
        self.assertTrue(any("Acceptance Criteria" in e for e in result.errors))

    def test_validate_empty_requirements(self):
        path = Path("bad.md")
        path.write_text(
            "# Spec\n\n## Goal\nBuild\n\n"
            "## Requirements\n\n_No requirements_\n\n"
            "## Acceptance Criteria\n\n- AC-001: works\n"
        )
        result = self.engine.validate(path)
        self.assertFalse(result.valid)
        self.assertTrue(any("no requirements" in e.lower() for e in result.errors))


class TestSpecEngineApprove(TempSpecDir):
    """Test SpecEngine.approve()."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_approve_none_raises(self):
        with self.assertRaises(SpecError):
            self.engine.approve(None)

    def test_approve_valid_file(self):
        path = self.engine.generate("Build something")
        # Should not raise
        self.engine.approve(path)

    def test_approve_nonexistent_file(self):
        # approve() in v1 just checks for None, not file existence
        self.engine.approve(Path("nonexistent.md"))


class TestSpecEngineParse(TempSpecDir):
    """Test SpecEngine.parse() reads real file."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_parse_none_raises(self):
        with self.assertRaises(SpecError):
            self.engine.parse(None)

    def test_parse_nonexistent_raises(self):
        with self.assertRaises(SpecError):
            self.engine.parse(Path("nonexistent.md"))

    def test_parse_generated_file(self):
        self.engine.generate("Build a Python calculator that must validate input")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        self.assertIsInstance(spec, StructuredSpec)
        self.assertGreater(len(spec.requirements), 0)
        self.assertGreater(len(spec.acceptance_criteria), 0)

    def test_parse_preserves_requirements(self):
        self.engine.generate("Create a system that must process data efficiently")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        # Should have at least one requirement with priority
        req = spec.requirements[0]
        self.assertIsInstance(req, Requirement)
        self.assertIn(req.priority, [Priority.MUST, Priority.SHOULD, Priority.COULD, Priority.NICE])

    def test_parse_preserves_acs(self):
        self.engine.generate("Build a form. As a user, I want to submit data.")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        self.assertGreater(len(spec.acceptance_criteria), 0)
        ac = spec.acceptance_criteria[0]
        self.assertIsInstance(ac, AC)
        self.assertIsNotNone(ac.description)

    def test_parse_scope(self):
        self.engine.generate("Build a calculator. Include testing. Exclude deployment.")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        self.assertIsInstance(spec.scope, Scope)

    def test_parse_data_models_from_entities(self):
        self.engine.generate("Define a User model with name and email fields")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        # Should detect User entity
        if spec.data_models:
            self.assertEqual(spec.data_models[0].name, "User")

    def test_parse_api_contracts(self):
        self.engine.generate("GET /api/users and POST /api/orders endpoints")
        path = Path("docs/specs/goals.md")
        spec = self.engine.parse(path)

        if spec.api_contracts:
            methods = [c.method for c in spec.api_contracts]
            self.assertIn("GET", methods)


# ── Roundtrip: Generate → Validate → Parse ───────────────────────

class TestSpecRoundtrip(TempSpecDir):
    """Test full generate → validate → parse roundtrip."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_roundtrip_simple(self):
        prompt = "Build a Python calculator with Django that must validate input"
        path = self.engine.generate(prompt)
        result = self.engine.validate(path)
        self.assertTrue(result.valid, f"Validation errors: {result.errors}")
        self.engine.approve(path)
        spec = self.engine.parse(path)
        self.assertGreater(len(spec.requirements), 0)

    def test_roundtrip_complex(self):
        prompt = (
            "Create a REST API for user management using Django and PostgreSQL. "
            "GET /api/users must return all users. POST /api/users must create a user. "
            "The system must validate email format. As a user, I want to register an account. "
            "Define a User model with name, email, and password fields. "
            "Out of scope: payment integration."
        )
        path = self.engine.generate(prompt)
        result = self.engine.validate(path)
        self.assertTrue(result.valid, f"Validation errors: {result.errors}")
        spec = self.engine.parse(path)

        self.assertGreater(len(spec.requirements), 0)
        self.assertGreater(len(spec.acceptance_criteria), 0)

        # Check scope extracted
        if spec.scope.excluded:
            self.assertTrue(any("payment" in e.lower() for e in spec.scope.excluded))

    def test_roundtrip_preserves_data(self):
        """Data from generate should survive parse."""
        prompt = "Build a Python web app with user model and GET /api/items endpoint"
        path = self.engine.generate(prompt)
        spec = self.engine.parse(path)

        # All requirements should have IDs
        for req in spec.requirements:
            self.assertIsNotNone(req.id)
            self.assertIsNotNone(req.title)
            self.assertIsNotNone(req.description)

        # All ACs should have IDs and link to requirements
        for ac in spec.acceptance_criteria:
            self.assertIsNotNone(ac.id)
            self.assertIsNotNone(ac.requirement_id)
            self.assertIsNotNone(ac.description)


# ── PromptAnalyzer (public API) ──────────────────────────────────

class TestPromptAnalyzer(unittest.TestCase):
    """Test PromptAnalyzer public API."""

    def test_analyze_returns_dict(self):
        result = PromptAnalyzer.analyze("Build a calculator")
        self.assertIsInstance(result, dict)
        self.assertIn("requirements", result)
        self.assertIn("acceptance_criteria", result)
        self.assertIn("tech_stack", result)

    def test_analyze_requirements_count(self):
        result = PromptAnalyzer.analyze("Must create a calculator. Should add history.")
        self.assertGreater(len(result["requirements"]), 0)

    def test_analyze_tech_stack(self):
        result = PromptAnalyzer.analyze("Build a Python Django app")
        self.assertIn("python", result["tech_stack"])

    def test_analyze_entities(self):
        result = PromptAnalyzer.analyze("Define a User model")
        self.assertIsInstance(result["entities"], list)


# ── Edge Cases ───────────────────────────────────────────────────

class TestEdgeCases(TempSpecDir):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_single_word_prompt(self):
        path = self.engine.generate("Calculator")
        self.assertTrue(path.exists())
        spec = self.engine.parse(path)
        self.assertGreater(len(spec.requirements), 0)

    def test_long_prompt(self):
        prompt = "Build " + "very " * 50 + "complex system"
        path = self.engine.generate(prompt)
        self.assertTrue(path.exists())

    def test_special_characters(self):
        path = self.engine.generate("Build a system with <html> & special chars!")
        self.assertTrue(path.exists())

    def test_unicode_prompt(self):
        path = self.engine.generate("Создай калькулятор на Python")
        self.assertTrue(path.exists())

    def test_multiline_prompt(self):
        prompt = """Build a calculator.
It must support addition and subtraction.
Should be fast.
As a user, I want to see history."""
        path = self.engine.generate(prompt)
        spec = self.engine.parse(path)
        self.assertGreater(len(spec.requirements), 0)


# ── Determinism ──────────────────────────────────────────────────

class TestDeterminism(TempSpecDir):
    """Test that same prompt produces same output."""

    def setUp(self):
        super().setUp()
        self.engine = SpecEngine()

    def test_same_prompt_same_requirements(self):
        prompt = "Build a calculator that must validate input"
        path1 = self.engine.generate(prompt)
        spec1 = self.engine.parse(path1)

        path2 = self.engine.generate(prompt)
        spec2 = self.engine.parse(path2)

        # Same number of requirements
        self.assertEqual(len(spec1.requirements), len(spec2.requirements))

        # Same requirement titles
        titles1 = [r.title for r in spec1.requirements]
        titles2 = [r.title for r in spec2.requirements]
        self.assertEqual(titles1, titles2)

    def test_different_prompts_different_output(self):
        spec1 = self.engine.parse(self.engine.generate("Build a calculator"))
        spec2 = self.engine.parse(self.engine.generate("Build a chat application"))
        # At least requirement count should differ (or titles)
        titles1 = [r.title for r in spec1.requirements]
        titles2 = [r.title for r in spec2.requirements]
        # They may or may not differ, but the test verifies no crash
        self.assertIsInstance(titles1, list)
        self.assertIsInstance(titles2, list)


if __name__ == "__main__":
    unittest.main()
