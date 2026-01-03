from typing import List

from specification.authorization_spec import AuthorizationSpec
from verification.check_result import CheckResult


class ScopeBoundednessChecker:
    """Validates that execution scope bounds are positive and sensible.

    Ensures execution cannot run indefinitely or consume unbounded resources.
    """

    def check(self, spec: AuthorizationSpec) -> CheckResult:
        violations: List[str] = []

        scope = spec.execution_scope
        if scope is None:
            violations.append("execution_scope is not provided")
            return CheckResult("ScopeBoundednessChecker", False, violations)

        if getattr(scope, "max_iterations", 0) <= 0:
            violations.append(
                f"max_iterations must be > 0 (current: {getattr(scope, 'max_iterations', None)})"
            )

        if getattr(scope, "max_data_size", 0) <= 0:
            violations.append(
                f"max_data_size must be > 0 bytes (current: {getattr(scope, 'max_data_size', None)})"
            )

        if getattr(scope, "timeout_seconds", 0) <= 0:
            violations.append(
                f"timeout_seconds must be > 0 (current: {getattr(scope, 'timeout_seconds', None)})"
            )

        return CheckResult("ScopeBoundednessChecker", len(violations) == 0, violations)
