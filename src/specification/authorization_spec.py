from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from sympy import public


@dataclass(frozen=True)
class InputDeclaration:
    source_type: str
    source_id: str
    data_schema: Dict[str, Any]
    access_mode: str


@dataclass(frozen=True)
class ForbiddenPattern:
    pattern_type: str
    pattern_value: str
    reason: str


@dataclass(frozen=True)
class ActionDeclaration:
    action_type: str
    target_type: str
    parameters_schema: Dict[str, Any]
    preconditions: List[str]


@dataclass(frozen=True)
class ScopeDeclaration:
    max_iterations: int
    max_data_size: int
    timeout_seconds: int
    allowed_resources: List[str]


@dataclass(frozen=True)
 
class AuthorizationSpec:
    spec_id: str
    version: str

    allowed_inputs: List[InputDeclaration]
    forbidden_inputs: List[ForbiddenPattern]
    permitted_actions: List[ActionDeclaration]
    execution_scope: ScopeDeclaration

    metadata: Optional[Dict[str, Any]] = None
