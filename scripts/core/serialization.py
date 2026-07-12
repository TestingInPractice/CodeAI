"""CodeAI Platform — Serialization helpers.

Provides Serializable mixin and conversion functions for JSON-safe types.
No external dependencies — uses only stdlib.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import fields
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Union, get_type_hints
from uuid import UUID

__all__ = [
    "Serializable",
    "to_json_value",
    "from_json_value",
]


def _is_optional(tp: Any) -> bool:
    """Check if type is Optional[X] (Union[X, None])."""
    origin = getattr(tp, "__origin__", None)
    if origin is Union:
        args = getattr(tp, "__args__", ())
        return type(None) in args
    return False


def _unwrap_optional(tp: Any) -> Any:
    """Extract X from Optional[X]."""
    args = getattr(tp, "__args__", ())
    return next(a for a in args if a is not type(None))


def _is_union(tp: Any) -> bool:
    """Check if type is a Union."""
    return getattr(tp, "__origin__", None) is Union


def to_json_value(value: Any) -> Any:
    """Convert a single value to JSON-safe type."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: to_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(v) for v in value]
    if isinstance(value, Serializable):
        return value.to_dict()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def from_json_value(value: Any, target_type: Any) -> Any:
    """Convert a JSON value back to the target type."""
    if value is None:
        return None

    # Handle Optional[X]
    if _is_optional(target_type):
        inner = _unwrap_optional(target_type)
        return from_json_value(value, inner)

    # Handle Union types (non-Optional)
    if _is_union(target_type):
        for arg in target_type.__args__:
            if arg is type(None):
                continue
            try:
                return from_json_value(value, arg)
            except (ValueError, KeyError):
                continue
        return value

    # Handle Serializable subclasses
    if isinstance(target_type, type) and issubclass(target_type, Serializable):
        if isinstance(value, dict):
            return target_type.from_dict(value)

    # Handle UUID
    if target_type is UUID:
        return UUID(value) if isinstance(value, str) else value

    # Handle datetime
    if target_type is datetime:
        return datetime.fromisoformat(value) if isinstance(value, str) else value

    # Handle Path
    if isinstance(target_type, type) and issubclass(target_type, Path):
        return target_type(value) if isinstance(value, str) else value

    # Handle Enum
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        return target_type(value)

    # Handle list[X]
    origin = getattr(target_type, "__origin__", None)
    if origin is list:
        args = getattr(target_type, "__args__", (str,))
        item_type = args[0] if args else str
        return [from_json_value(v, item_type) for v in value]

    # Handle dict[K, V]
    if origin is dict:
        return value

    return value


class Serializable:
    """Mixin for dataclasses to support JSON serialization.

    Provides to_dict() and from_dict() for all dataclasses.
    Handles UUID, datetime, Path, Enum, nested dataclasses, Optional, list, dict.
    """

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-safe dict."""
        result = {}
        for f in fields(self):
            value = getattr(self, f.name)
            result[f.name] = to_json_value(value)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any], strict: bool = False) -> Serializable:
        """Deserialize from dict.

        Args:
            data: Dictionary to deserialize from.
            strict: If True, raise on unknown fields. If False, warn and ignore.

        Returns:
            Reconstructed instance.
        """
        if not data:
            return cls()
        hints = get_type_hints(cls)
        known_fields = {f.name for f in fields(cls)}

        # Check for unknown fields
        unknown = set(data.keys()) - known_fields
        if unknown:
            msg = f"Unknown fields in {cls.__name__}.from_dict(): {unknown}"
            if strict:
                raise ValueError(msg)
            warnings.warn(msg, stacklevel=2)

        kwargs = {}
        for f in fields(cls):
            if f.name not in data:
                continue
            raw = data[f.name]
            tp = hints.get(f.name, Any)
            kwargs[f.name] = from_json_value(raw, tp)
        return cls(**kwargs)

    def to_json(self, **kwargs: Any) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, text: str, strict: bool = False) -> Serializable:
        """Deserialize from JSON string.

        Args:
            text: JSON string to deserialize.
            strict: If True, raise on unknown fields.
        """
        return cls.from_dict(json.loads(text), strict=strict)
