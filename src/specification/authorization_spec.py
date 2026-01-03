# Package root: src/

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from specification.models import AllowedInput, ExecutionScope, PermittedAction


@dataclass(frozen=True)
class ForbiddenPattern:
    pattern_type: str
    pattern_value: str
    reason: str


@dataclass(frozen=True)
class AuthorizationSpec:
    spec_id: str
    version: str

    allowed_inputs: List[AllowedInput]
    forbidden_inputs: List[ForbiddenPattern]
    permitted_actions: List[PermittedAction]
    execution_scope: ExecutionScope

    metadata: Optional[Dict[str, Any]] = None
