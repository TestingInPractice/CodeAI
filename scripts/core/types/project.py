"""CodeAI Platform — Project Context (integration point)."""

from dataclasses import dataclass, field

from scripts.core.serialization import Serializable
from scripts.core.types.common import RuntimeContext
from scripts.core.types.judge import Verdict
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.spec import StructuredSpec
from scripts.core.types.workflow import WorkflowState


@dataclass
class ProjectContext(Serializable):
    """Unified project context passed between subsystems.

    Combines:
        - StructuredSpec (from Spec Engine)
        - WorkflowState (from Workflow Engine)
        - RuntimeContext (from runtime)
        - MemoryEntry list (from Memory Layer)
        - Knowledge list (from Knowledge Layer)
        - Verdict (from Judge Engine)
    """
    spec: StructuredSpec = field(default_factory=StructuredSpec)
    workflow: WorkflowState = field(default_factory=WorkflowState)
    memory: list[MemoryEntry] = field(default_factory=list)
    knowledge: list[Knowledge] = field(default_factory=list)
    runtime: RuntimeContext | None = None
    verdict: Verdict | None = None
