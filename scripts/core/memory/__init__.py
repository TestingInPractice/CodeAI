"""CodeAI Platform — Memory Layer package.

Provides memory repository abstraction and JSON-based persistence.
"""

from scripts.core.memory.json_repository import JsonMemoryRepository
from scripts.core.memory.repository import MemoryRepository

__all__ = [
    "MemoryRepository",
    "JsonMemoryRepository",
]
