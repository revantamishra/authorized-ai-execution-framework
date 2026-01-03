from typing import List

from specification.authorization_spec import AuthorizationSpec
from verification.check_result import CheckResult


class ForbiddenDataChecker:
    """
    Verifies that no forbidden data patterns overlap with allowed inputs.

    This ensures explicit control over what data can be accessed.
    Any overlap between forbidden patterns and allowed inputs is a violation.
    """

    def check(self, spec: AuthorizationSpec) -> CheckResult:
        """
        Check for overlaps between forbidden and allowed inputs.

        Args:
            spec: The authorization specification to validate

        Returns:
            CheckResult with pass/fail status and violation details
        """
        violations: List[str] = []

        # If forbidden_inputs is empty list, that's explicit and allowed.
        # If it's None, CompletenessChecker will flag the omission.
        if spec.forbidden_inputs:
            for forbidden in spec.forbidden_inputs:
                for allowed in spec.allowed_inputs:
                    # Exact match on the source id is considered an overlap.
                    if forbidden.pattern_value == allowed.source_id:
                        violations.append(
                            (
                                f"Forbidden pattern '{forbidden.pattern_value}' "
                                f"overlaps with allowed input '{allowed.source_id}': {forbidden.reason}"
                            )
                        )

        return CheckResult("ForbiddenDataChecker", len(violations) == 0, violations)
