# Package root: src/

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AllowedInput:
    """Description of an allowed data input source.

    Attributes:
        source_type: High-level type of the source (e.g. 'database', 'file').
        source_id: Unique identifier for the specific source (e.g. table name).
        data_schema: Schema or metadata describing the allowed data shape.
    """

    source_type: str
    source_id: str
    data_schema: Dict[str, Any]


@dataclass(frozen=True)
class PermittedAction:
    """Represents an explicitly permitted action an AI may perform.

    Attributes:
        action_type: The action verb (e.g. 'read', 'write', 'call').
        target_type: The target category of the action (e.g. 'summary', 'file').
        parameters_schema: Expected parameters for the action (may be empty dict).
    """

    action_type: str
    target_type: str
    parameters_schema: Dict[str, Any]


@dataclass(frozen=True)
class ExecutionScope:
    """Defines strict bounds for an execution instance.

    All bounds must be explicitly set and positive integers. Defaults are
    conservative but explicit declaration is recommended in higher-level specs.
    """

    max_iterations: int
    max_data_size: int = 1000000  # 1 MB default
    timeout_seconds: int = 300  # 5 minutes default
    allowed_resources: Optional[List[str]] = None

    def __post_init__(self) -> None:
        # Normalize optional list to an empty list for consistent usage
        if self.allowed_resources is None:
            object.__setattr__(self, "allowed_resources", [])

        # Validate bounds are positive
        if self.max_iterations <= 0:
            raise ValueError("ExecutionScope.max_iterations must be > 0")
        if self.max_data_size <= 0:
            raise ValueError("ExecutionScope.max_data_size must be > 0")
        if self.timeout_seconds <= 0:
            raise ValueError("ExecutionScope.timeout_seconds must be > 0")
