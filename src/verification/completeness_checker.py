# Package root: src/

from typing import List

from specification.authorization_spec import AuthorizationSpec
from verification.check_result import CheckResult


class CompletenessChecker:
    """Verifies that an AuthorizationSpec includes all mandatory fields.

    The framework enforces the "no implicit behavior" principle: fields that
    are relevant to authorization decisions must be present and explicit.
    """

    def check(self, spec: AuthorizationSpec) -> CheckResult:
        """Return a CheckResult indicating missing or malformed required fields.

        Rules:
        - `allowed_inputs` must be a non-empty list (explicitly declare data sources)
        - `permitted_actions` must be a non-empty list (explicitly declare actions)
        - `execution_scope` must be provided
        - `forbidden_inputs` must be an explicit list (empty if none)
        """
        violations: List[str] = []

        if not spec.allowed_inputs:
            violations.append(
                "No allowed inputs defined - must explicitly declare allowed data sources"
            )

        if not spec.permitted_actions:
            violations.append(
                "No permitted actions defined - must explicitly declare allowed actions"
            )

        if spec.execution_scope is None:
            violations.append(
                "Execution scope missing - must define bounds for iterations, data size, and timeout"
            )

        # `forbidden_inputs` must be explicitly declared; `None` is considered omission
        if spec.forbidden_inputs is None:
            violations.append(
                "Forbidden inputs not declared - must be an explicit list (empty if none apply)"
            )

        return CheckResult("CompletenessChecker", len(violations) == 0, violations)
