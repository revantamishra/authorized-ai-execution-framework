# Package root: src/

from typing import List

from specification.authorization_spec import AuthorizationSpec
from verification.check_result import CheckResult


class ActionBoundaryChecker:
    """Ensures every permitted action is fully and explicitly declared.

    No wildcard or implicit actions are allowed. Each action must include:
    - `action_type` (string)
    - `target_type` (string)
    - `parameters_schema` (dict, may be empty)
    """

    def check(self, spec: AuthorizationSpec) -> CheckResult:
        violations: List[str] = []

        if not spec.permitted_actions:
            violations.append(
                "No permitted actions defined - must explicitly declare allowed actions"
            )
            return CheckResult("ActionBoundaryChecker", False, violations)

        for i, action in enumerate(spec.permitted_actions):
            if not getattr(action, "action_type", None):
                violations.append(f"Action {i}: action_type is missing or empty")

            if not getattr(action, "target_type", None):
                violations.append(f"Action {i}: target_type is missing or empty")

            if getattr(action, "parameters_schema", None) is None:
                violations.append(
                    f"Action {i} ({getattr(action, 'action_type', '<unknown>')}): "
                    "parameters_schema is None (must be dict, even if empty)"
                )

        return CheckResult("ActionBoundaryChecker", len(violations) == 0, violations)
