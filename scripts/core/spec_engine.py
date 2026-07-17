"""CodeAI Platform — Spec Engine.

Deterministic implementation. No LLM.
Analyzes prompt, generates goals.md, validates structure, parses into StructuredSpec.
"""

import re
import uuid
from pathlib import Path

from scripts.core.enums import Priority
from scripts.core.errors import SpecError
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

# ── Deterministic Prompt Analysis ────────────────────────────────

# Patterns for requirement detection (sentences containing these are requirements)
_REQ_PATTERNS = [
    r"\bmust\b",
    r"\bshould\b",
    r"\bneed(?:s|ed)?\s+to\b",
    r"\bhave(?:s)?\s+to\b",
    r"\bshall\b",
    r"\bimplement\b",
    r"\bcreate\b",
    r"\bsupport\b",
    r"\bprovide\b",
    r"\benable\b",
    r"\bensure\b",
    r"\brequire\b",
]

# Patterns for acceptance criteria detection
_AC_PATTERNS = [
    r"\bas\s+(?:a|an)\s+\w+\s*,?\s*I\s+(?:want|can|should|need)",
    r"\bgiven\b.*?\bwhen\b.*?\bthen\b",
    r"\bverify\s+that\b",
    r"\bshould\s+be\s+able\s+to\b",
    r"\bmust\s+be\s+(?:able\s+to|valid|required|supported)",
    r"\bcan\s+(?:be|access|view|create|update|delete)",
    r"\bwhen\s+(?:a|an|the|I)\b",
    r"\bif\s+.*?\bthen\b",
    r"\bAC[\s:-]+",
]

# Patterns for data model / entity detection
_ENTITY_PATTERNS = [
    r"\b(\w+)\s+model\b",
    r"\b(\w+)\s+schema\b",
    r"\b(\w+)\s+table\b",
    r"\b(\w+)\s+entity\b",
    r"\b(\w+)\s+record\b",
    r"\b(\w+)\s+object\b",
    r"\bstore\s+(?:a|an|the)\s+(\w+)",
    r"\b(\w+)\s+(?:data|information)\s+",
]

# Patterns for API endpoint detection
_API_PATTERNS = [
    r"(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/{}\-]+)",
    r"\b(?:endpoint|route|api)\s*[:=]\s*\w+\s+(/[\w/{}\-]+)",
    r"\b(?:endpoint|route|api)\s+[/]+([\w/{}\-]+)",
    r"\b(\w+)\s+endpoint\b",
    r"\bREST\b",
    r"\bCRUD\b",
]

# Tech stack detection
_TECH_PATTERNS = {
    "python": r"\b(?:python|django|flask|fastapi|uvicorn|pip|pytest)\b",
    "javascript": r"\b(?:javascript|node|npm|react|vue|angular|express|next\.?js|deno|bun)\b",
    "typescript": r"\b(?:typescript|ts)\b",
    "database": r"\b(?:database|postgres|mysql|sqlite|mongo|redis|sql|db)\b",
    "api": r"\b(?:api|rest|graphql|grpc|endpoint|route)\b",
    "cli": r"\b(?:cli|command[\s-]line|terminal|shell)\b",
    "web": r"\b(?:web|html|css|browser|frontend|backend)\b",
    "mobile": r"\b(?:mobile|ios|android|flutter|react[\s-]native)\b",
    "auth": r"\b(?:auth|login|signup|password|jwt|oauth|token)\b",
    "test": r"\b(?:test|testing|unittest|pytest|jest|mocha|coverage)\b",
}

# Scope keywords
_SCOPE_EXCLUDE_PATTERNS = [
    (r"\b(?:out\s+of\s+scope|not\s+include|no\s+need)\s*:?\s*(.+?)(?:\.|$)", "exclude"),
    (r"\b(?:exclud|skip|omit|without)\b\s+(.+?)(?:\.|$)", "exclude"),
]

_SCOPE_INCLUDE_PATTERNS = [
    (r"\b(?:scope|include|covering|includes)\s*:?\s*(.+?)(?:\.|$)", "include"),
]

# Dependency keywords
_DEP_PATTERNS = [
    r"\busing\s+(\w[\w\s,]+)",
    r"\bbased\s+on\s+(\w[\w\s,]+)",
    r"\bbuilt\s+(?:with|on|using)\s+(\w[\w\s,]+)",
    r"\bdepend(?:s|ency)\s+on\s+(\w[\w\s,]+)",
    r"\brequire(?:s)?\s+(\w[\w\s,]+)",
    r"\bintegrate(?:s)?\s+(?:with\s+)?(\w[\w\s,]+)",
    r"\b(\w+)\s+(?:as\s+)?(?:a\s+)?dependency\b",
]

# Component keywords
_COMP_PATTERNS = [
    r"\b(\w+)\s+(?:service|component|module|layer|engine|handler|manager|controller)\b",
    r"\b(?:service|component|module|layer|engine|handler|manager|controller)\s+(\w+)\b",
    r"\b(\w+)\s+(?:microservice|worker|daemon|server)\b",
]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences. Handles common abbreviations."""
    # Split on sentence-ending punctuation, but not inside common abbreviations
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)
    sentences = []
    for s in raw:
        s = s.strip()
        if s:
            sentences.append(s)
    return sentences


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    return re.findall(r"[a-z_][\w-]*", text.lower())


def _detect_priority(text: str) -> Priority:
    """Detect requirement priority from text context."""
    lower = text.lower()
    if re.search(r"\b(?:critical|must\s+have|essential|vital|required)\b", lower):
        return Priority.MUST
    if re.search(r"\b(?:should|important|preferred|desirable)\b", lower):
        return Priority.SHOULD
    if re.search(r"\b(?:could|nice[\s-]to[\s-]have|optional|bonus)\b", lower):
        return Priority.COULD
    return Priority.MUST


def _extract_requirements(prompt: str) -> list[tuple[str, str, Priority]]:
    """Extract requirements from prompt. Returns [(id, description, priority)]."""
    sentences = _split_sentences(prompt)
    requirements = []
    seen = set()

    for i, sent in enumerate(sentences):
        is_req = any(re.search(p, sent, re.IGNORECASE) for p in _REQ_PATTERNS)
        # Also treat imperative verbs at start as requirements
        if not is_req:
            first_word = sent.split()[0].lower() if sent.split() else ""
            if first_word in {
                "create", "implement", "add", "build", "develop", "support",
                "provide", "enable", "ensure", "set", "make", "configure",
                "design", "build", "write", "define", "establish",
            }:
                is_req = True

        if is_req:
            key = sent.strip().lower()
            if key not in seen:
                seen.add(key)
                priority = _detect_priority(sent)
                requirements.append((sent.strip(), priority))

    # Fallback: if no requirements found, treat the whole prompt as one
    if not requirements:
        clean = prompt.strip().split("\n")[0][:200]
        requirements.append((clean, Priority.MUST))

    return requirements


def _extract_acs(prompt: str) -> list[str]:
    """Extract acceptance criteria from prompt."""
    sentences = _split_sentences(prompt)
    acs = []
    seen = set()

    for sent in sentences:
        is_ac = any(re.search(p, sent, re.IGNORECASE) for p in _AC_PATTERNS)
        if is_ac:
            key = sent.strip().lower()
            if key not in seen:
                seen.add(key)
                acs.append(sent.strip())

    return acs


def _extract_entities(prompt: str) -> list[str]:
    """Extract entity/model names from prompt."""
    entities = []
    seen = set()

    for pat in _ENTITY_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            name = m.group(1) if m.lastindex else m.group(0)
            name = name.strip().title()
            if name and name.lower() not in seen and len(name) > 2:
                seen.add(name.lower())
                entities.append(name)

    # Also look for capitalized words that look like entity names
    for m in re.finditer(r"\b([A-Z][a-z]{2,})\b", prompt):
        name = m.group(1)
        # Skip common English words
        if name.lower() not in {
            "the", "and", "for", "with", "from", "that", "this", "which",
            "when", "where", "have", "been", "will", "can", "are", "was",
            "not", "but", "what", "all", "its", "may", "use", "than",
            "also", "each", "just", "into", "over", "such", "after",
            "most", "any", "new", "some", "only", "our", "out", "get",
            "set", "make", "how",
        }:
            if name.lower() not in seen:
                seen.add(name.lower())
                entities.append(name)

    return entities[:10]


def _extract_api_contracts(prompt: str) -> list[tuple[str, str]]:
    """Extract API methods and paths. Returns [(method, path)]."""
    contracts = []
    seen = set()

    for pat in _API_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            groups = m.groups()
            if len(groups) >= 2:
                method = groups[0].upper()
                path = groups[1]
                if method in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                    key = f"{method} {path}"
                    if key not in seen:
                        seen.add(key)
                        contracts.append((method, path))

    return contracts


def _detect_tech_stack(prompt: str) -> list[str]:
    """Detect mentioned technologies."""
    stack = []
    lower = prompt.lower()
    for tech, pat in _TECH_PATTERNS.items():
        if re.search(pat, lower):
            stack.append(tech)
    return stack


def _detect_dependencies(prompt: str) -> list[str]:
    """Extract dependencies from prompt."""
    deps = []
    seen = set()

    for pat in _DEP_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            raw = m.group(1) if m.lastindex else m.group(0)
            # Split comma-separated deps
            for d in re.split(r",\s*|\s+and\s+", raw):
                d = d.strip().title()
                if d and len(d) > 1 and d.lower() not in seen:
                    seen.add(d.lower())
                    deps.append(d)

    return deps[:10]


def _detect_components(prompt: str) -> list[str]:
    """Extract component names from prompt."""
    comps = []
    seen = set()

    for pat in _COMP_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            name = m.group(1).title() if m.lastindex else m.group(0).title()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                comps.append(name)

    return comps[:10]


def _detect_scope(prompt: str) -> tuple[list[str], list[str]]:
    """Extract included/excluded scope from prompt."""
    included = []
    excluded = []

    for pat, kind in _SCOPE_EXCLUDE_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            text = m.group(1).strip()
            if text:
                excluded.append(text)

    for pat, kind in _SCOPE_INCLUDE_PATTERNS:
        for m in re.finditer(pat, prompt, re.IGNORECASE):
            text = m.group(1).strip()
            if text:
                included.append(text)

    return included, excluded


def _extract_entities_for_models(prompt: str) -> list[tuple[str, list[str]]]:
    """Extract entity names and their likely fields. Returns [(entity_name, [fields])]."""
    entities = _extract_entities(prompt)
    result = []

    # Field inference patterns
    field_hints = {
        "user": ["id: UUID", "name: str", "email: str", "created_at: datetime"],
        "item": ["id: UUID", "name: str", "description: str"],
        "task": ["id: UUID", "title: str", "status: str", "created_at: datetime"],
        "project": ["id: UUID", "name: str", "description: str", "created_at: datetime"],
        "order": ["id: UUID", "user_id: UUID", "status: str", "total: float", "created_at: datetime"],
        "product": ["id: UUID", "name: str", "price: float", "description: str"],
        "message": ["id: UUID", "sender_id: UUID", "content: str", "timestamp: datetime"],
        "comment": ["id: UUID", "author_id: UUID", "text: str", "created_at: datetime"],
        "post": ["id: UUID", "title: str", "content: str", "author_id: UUID", "created_at: datetime"],
        "file": ["id: UUID", "name: str", "path: str", "size: int"],
        "config": ["key: str", "value: str", "updated_at: datetime"],
        "event": ["id: UUID", "type: str", "timestamp: datetime", "data: dict"],
    }

    for entity in entities:
        key = entity.lower()
        if key in field_hints:
            result.append((entity, field_hints[key]))
        else:
            result.append((entity, ["id: UUID", "name: str"]))

    return result


def _format_goals_md(
    prompt: str,
    requirements: list[tuple[str, str, Priority]],
    acs: list[str],
    entities: list[str],
    models: list[tuple[str, list[str]]],
    api_contracts: list[tuple[str, str]],
    tech_stack: list[str],
    dependencies: list[str],
    components: list[str],
    included_scope: list[str],
    excluded_scope: list[str],
) -> str:
    """Format analyzed data into goals.md markdown."""
    lines = []

    lines.append("# Goals Specification")
    lines.append("")
    lines.append("## Meta")
    lines.append(f"- **Version**: 1.0")
    lines.append(f"- **Status**: draft")
    lines.append(f"- **Generated**: deterministic (no LLM)")
    lines.append("")

    # Goal
    first_sentence = _split_sentences(prompt)[0] if _split_sentences(prompt) else prompt
    lines.append("## Goal")
    lines.append("")
    lines.append(f"**What**: {first_sentence}")
    lines.append("")
    if tech_stack:
        lines.append(f"**Tech stack**: {', '.join(tech_stack)}")
        lines.append("")

    # Scope
    lines.append("## Scope")
    lines.append("")
    if included_scope:
        lines.append("**Included**:")
        for s in included_scope:
            lines.append(f"- {s}")
    else:
        lines.append("**Included**:")
        lines.append("- Core implementation")
    lines.append("")
    if excluded_scope:
        lines.append("**Excluded**:")
        for s in excluded_scope:
            lines.append(f"- {s}")
    lines.append("")

    # Requirements
    lines.append("## Requirements")
    lines.append("")
    for i, (desc, priority) in enumerate(requirements, 1):
        rid = f"REQ-{i:03d}"
        lines.append(f"- **[{rid}]** [{priority.value}] {desc}")
    lines.append("")

    # Acceptance Criteria
    lines.append("## Acceptance Criteria")
    lines.append("")
    if acs:
        for i, ac in enumerate(acs, 1):
            ac_id = f"AC-{i:03d}"
            # Try to link to a requirement
            lines.append(f"- **[{ac_id}]** {ac}")
    else:
        lines.append("- **[AC-001]** All requirements implemented and working")
        lines.append("- **[AC-002]** No regressions in existing functionality")
    lines.append("")

    # Data Models
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

    # API Contracts
    lines.append("## API Contracts")
    lines.append("")
    if api_contracts:
        lines.append("| Method | Path |")
        lines.append("|--------|------|")
        for method, path in api_contracts:
            lines.append(f"| {method} | `{path}` |")
    else:
        lines.append("_No API contracts identified from prompt._")
    lines.append("")

    # Dependencies
    lines.append("## Dependencies")
    lines.append("")
    if dependencies:
        for dep in dependencies:
            lines.append(f"- {dep}")
    else:
        lines.append("_No explicit dependencies detected._")
    lines.append("")

    # Components
    lines.append("## Components")
    lines.append("")
    if components:
        for comp in components:
            lines.append(f"- {comp}")
    else:
        lines.append("_No explicit components detected._")
    lines.append("")

    # Open Questions
    lines.append("## Open Questions")
    lines.append("")
    lines.append("- What are the performance requirements?")
    lines.append("- What is the expected scale/traffic?")
    lines.append("- Are there security or compliance constraints?")
    lines.append("")

    return "\n".join(lines)


# ── Goals.md Parser ──────────────────────────────────────────────

def _parse_goals_md(content: str) -> StructuredSpec:
    """Parse goals.md content into StructuredSpec."""
    requirements = []
    acceptance_criteria = []
    data_models = []
    api_contracts = []
    scope = Scope()
    dependencies = []

    sections = _split_sections(content)

    # Parse Requirements
    req_id_map: dict[str, uuid.UUID] = {}
    if "Requirements" in sections:
        for line in sections["Requirements"].split("\n"):
            line = line.strip()
            m = re.match(r"^-\s+\*\*\[(\w+-\d+)\]\*\*\s+\[(\w+)\]\s+(.+)$", line)
            if m:
                rid_str = m.group(1)
                priority_str = m.group(2)
                desc = m.group(3).strip()
                req_id = uuid.uuid4()
                req_id_map[rid_str] = req_id
                try:
                    priority = Priority(priority_str)
                except ValueError:
                    priority = Priority.MUST
                requirements.append(Requirement(
                    id=req_id,
                    title=desc[:80],
                    description=desc,
                    priority=priority,
                ))

    # Parse Acceptance Criteria
    if "Acceptance Criteria" in sections:
        for line in sections["Acceptance Criteria"].split("\n"):
            line = line.strip()
            m = re.match(r"^-\s+\*\*\[(\w+-\d+)\]\*\*\s+(.+)$", line)
            if m:
                ac_id_str = m.group(1)
                desc = m.group(2).strip()
                # Try to link to requirement by number
                req_num = re.search(r"(\d+)", ac_id_str)
                linked_req = None
                if req_num:
                    target_rid = f"REQ-{req_num.group(1)}"
                    linked_req = req_id_map.get(target_rid)
                if linked_req is None and requirements:
                    linked_req = requirements[0].id
                acceptance_criteria.append(AC(
                    id=uuid.uuid4(),
                    requirement_id=linked_req or uuid.uuid4(),
                    description=desc,
                ))

    # Parse Data Models
    if "Data Models" in sections:
        current_model = None
        current_fields: list[FieldDefinition] = []
        for line in sections["Data Models"].split("\n"):
            line = line.strip()
            if line.startswith("### "):
                if current_model and current_fields:
                    data_models.append(DataModel(name=current_model, fields=current_fields))
                current_model = line[4:].strip()
                current_fields = []
            elif line.startswith("- `"):
                field_str = line[3:-1].strip()  # remove "- \`" and trailing "`"
                field_def = _parse_field_def(field_str)
                if field_def:
                    current_fields.append(field_def)
        if current_model and current_fields:
            data_models.append(DataModel(name=current_model, fields=current_fields))

    # Parse API Contracts
    if "API Contracts" in sections:
        for line in sections["API Contracts"].split("\n"):
            line = line.strip()
            m = re.match(r"^\|\s*(\w+)\s*\|\s*`([^`]+)`\s*\|$", line)
            if m:
                api_contracts.append(APIContract(
                    method=m.group(1),
                    path=m.group(2),
                ))

    # Parse Scope
    if "Scope" in sections:
        included = []
        excluded = []
        current_list = None
        for line in sections["Scope"].split("\n"):
            line = line.strip()
            if line.startswith("**Included**"):
                current_list = included
            elif line.startswith("**Excluded**"):
                current_list = excluded
            elif line.startswith("- ") and current_list is not None:
                current_list.append(line[2:].strip())
        scope = Scope(included=included, excluded=excluded)

    # Parse Dependencies
    if "Dependencies" in sections:
        for line in sections["Dependencies"].split("\n"):
            line = line.strip()
            if line.startswith("- ") and not line.startswith("- _No"):
                dependencies.append(line[2:].strip())

    return StructuredSpec(
        requirements=requirements,
        acceptance_criteria=acceptance_criteria,
        data_models=data_models,
        api_contracts=api_contracts,
        scope=scope,
    )


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown into sections by ## headings."""
    sections: dict[str, str] = {}
    current_name = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines)
            current_name = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_name is not None:
        sections[current_name] = "\n".join(current_lines)

    return sections


def _parse_field_def(field_str: str) -> FieldDefinition | None:
    """Parse 'name: type' or 'name: type = default' into FieldDefinition."""
    field_str = field_str.strip()
    if not field_str:
        return None

    # Handle "name: type = default"
    m = re.match(r"^(\w+):\s*(\w+)\s*=\s*(.+)$", field_str)
    if m:
        return FieldDefinition(
            name=m.group(1),
            type=m.group(2),
            default=m.group(3).strip(),
        )

    # Handle "name: type"
    m = re.match(r"^(\w+):\s*(\w+)$", field_str)
    if m:
        return FieldDefinition(name=m.group(1), type=m.group(2))

    # Fallback: treat whole string as name with type "str"
    return FieldDefinition(name=field_str.split(":")[0].strip(), type="str")


# ── SpecEngine ───────────────────────────────────────────────────

class SpecEngine:
    """Spec Engine — lifecycle of specifications.

    Responsibilities:
        - Generate goals.md from user prompt
        - Validate goals.md structure
        - Human gate: approve spec
        - Parse goals.md into StructuredSpec

    v1: Deterministic prompt analysis, no LLM.
    """

    def generate(self, prompt: str) -> Path:
        """Generate goals.md from user prompt.

        Analyzes the prompt deterministically and writes a goals.md file
        with requirements, acceptance criteria, data models, API contracts,
        scope, dependencies, and components derived from the prompt.

        Args:
            prompt: User's project description.

        Returns:
            Path to generated goals.md.
        """
        if not prompt or not prompt.strip():
            raise SpecError(
                "Cannot generate spec from empty prompt",
                code="SPEC_EMPTY_PROMPT",
                recoverable=False,
            )

        prompt = prompt.strip()

        # Analyze prompt
        requirements = _extract_requirements(prompt)
        acs = _extract_acs(prompt)
        entities = _extract_entities(prompt)
        models = _extract_entities_for_models(prompt)
        api_contracts = _extract_api_contracts(prompt)
        tech_stack = _detect_tech_stack(prompt)
        dependencies = _detect_dependencies(prompt)
        components = _detect_components(prompt)
        included_scope, excluded_scope = _detect_scope(prompt)

        # Format goals.md
        content = _format_goals_md(
            prompt=prompt,
            requirements=requirements,
            acs=acs,
            entities=entities,
            models=models,
            api_contracts=api_contracts,
            tech_stack=tech_stack,
            dependencies=dependencies,
            components=components,
            included_scope=included_scope,
            excluded_scope=excluded_scope,
        )

        # Write to filesystem
        goals_path = Path("docs/specs/goals.md")
        goals_path.parent.mkdir(parents=True, exist_ok=True)
        goals_path.write_text(content, encoding="utf-8")

        return goals_path

    def validate(self, goals_path: Path) -> ValidationResult:
        """Validate goals.md structure.

        Checks:
            - Path is not None
            - File exists
            - File is not empty
            - Contains required sections: ## Goal, ## Requirements,
              ## Acceptance Criteria
            - Requirements section has at least one requirement
            - Acceptance Criteria section has at least one criterion

        Args:
            goals_path: Path to goals.md.

        Returns:
            ValidationResult with valid=True/False and errors/warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if goals_path is None:
            return ValidationResult(
                valid=False,
                errors=["goals_path is None"],
            )

        if not goals_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"File not found: {goals_path}"],
            )

        try:
            content = goals_path.read_text(encoding="utf-8")
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Cannot read file: {e}"],
            )

        if not content.strip():
            return ValidationResult(
                valid=False,
                errors=["File is empty"],
            )

        sections = _split_sections(content)

        # Required sections
        for section_name in ["Goal", "Requirements", "Acceptance Criteria"]:
            if section_name not in sections:
                errors.append(f"Missing section: ## {section_name}")

        # Validate requirements count
        if "Requirements" in sections:
            req_count = sum(
                1 for line in sections["Requirements"].split("\n")
                if re.match(r"^-\s+\*\*\[", line.strip())
            )
            if req_count == 0:
                errors.append("Requirements section has no requirements")

        # Validate AC count
        if "Acceptance Criteria" in sections:
            ac_count = sum(
                1 for line in sections["Acceptance Criteria"].split("\n")
                if re.match(r"^-\s+\*\*\[", line.strip())
            )
            if ac_count == 0:
                warnings.append("Acceptance Criteria section has no criteria")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def approve(self, goals_path: Path) -> None:
        """Human gate: approve spec.

        Writes ``- **Approved**: true`` into the ``## Meta`` section of
        goals.md so downstream phases can gate on this field.

        Args:
            goals_path: Path to goals.md.

        Raises:
            SpecError: If path is None or file does not exist.
        """
        if goals_path is None:
            raise SpecError(
                "Cannot approve null spec",
                code="SPEC_NULL_PATH",
                recoverable=False,
            )

        if not goals_path.exists():
            raise SpecError(
                f"Cannot approve non-existent spec: {goals_path}",
                code="SPEC_NOT_FOUND",
                recoverable=False,
            )

        content = goals_path.read_text(encoding="utf-8")

        # Inject Approved line after - **Status**: ... in ## Meta
        if "- **Approved**:" in content:
            content = re.sub(
                r"(\- \*\*Approved\*\*:)\s*\w+",
                r"\1 true",
                content,
            )
        else:
            content = re.sub(
                r"(\- \*\*Status\*\*:.*\n)",
                r"\1- **Approved**: true\n",
                content,
                count=1,
            )

        goals_path.write_text(content, encoding="utf-8")

    def parse(self, goals_path: Path) -> StructuredSpec:
        """Parse goals.md into StructuredSpec.

        Reads the goals.md file, parses its sections, and returns a
        StructuredSpec with requirements, acceptance criteria, data models,
        API contracts, and scope.

        Args:
            goals_path: Path to goals.md.

        Returns:
            StructuredSpec with requirements, ACs, data models, etc.
        """
        if goals_path is None:
            raise SpecError(
                "Cannot parse null spec",
                code="SPEC_NULL_PATH",
                recoverable=False,
            )

        if not goals_path.exists():
            raise SpecError(
                f"Cannot parse non-existent spec: {goals_path}",
                code="SPEC_NOT_FOUND",
                recoverable=False,
            )

        content = goals_path.read_text(encoding="utf-8")
        return _parse_goals_md(content)


# ── PromptAnalyzer (public facade) ───────────────────────────────

class PromptAnalyzer:
    """Deterministic prompt analysis facade.

    Provides a single analyze() method that returns structured data
    extracted from a user prompt without LLM.
    """

    @staticmethod
    def analyze(prompt: str) -> dict:
        """Analyze prompt and return extracted data.

        Returns:
            dict with keys: requirements, acceptance_criteria, entities,
            models, api_contracts, tech_stack, dependencies, components,
            scope_included, scope_excluded.
        """
        requirements = _extract_requirements(prompt)
        acs = _extract_acs(prompt)
        entities = _extract_entities(prompt)
        models = _extract_entities_for_models(prompt)
        api_contracts = _extract_api_contracts(prompt)
        tech_stack = _detect_tech_stack(prompt)
        dependencies = _detect_dependencies(prompt)
        components = _detect_components(prompt)
        included_scope, excluded_scope = _detect_scope(prompt)

        return {
            "requirements": requirements,
            "acceptance_criteria": acs,
            "entities": entities,
            "models": models,
            "api_contracts": api_contracts,
            "tech_stack": tech_stack,
            "dependencies": dependencies,
            "components": components,
            "scope_included": included_scope,
            "scope_excluded": excluded_scope,
        }
