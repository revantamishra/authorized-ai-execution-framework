import logging
from typing import List, Optional

from specification.authorization_spec import AuthorizationSpec
from verification.action_boundary_checker import ActionBoundaryChecker
from verification.check_result import CheckResult
from verification.completeness_checker import CompletenessChecker
from verification.forbidden_data_checker import ForbiddenDataChecker
from verification.scope_boundedness_checker import ScopeBoundednessChecker

logger = logging.getLogger(__name__)


class VerificationResult:
    def __init__(
        self,
        passed: bool,
        results: List[CheckResult],
        failure_reason: Optional[str],
    ):
        self.passed = passed
        self.results = results
        self.failure_reason = failure_reason

    def __repr__(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        return f"VerificationResult(status={status}, checks={len(self.results)})"


class VerificationOrchestrator:
    """
    Runs all static verification checks.
    Execution is allowed iff all checks pass.
    """

    def __init__(self) -> None:
        self.checkers = [
            CompletenessChecker(),
            ForbiddenDataChecker(),
            ActionBoundaryChecker(),
            ScopeBoundednessChecker(),
        ]

    def verify(self, spec: AuthorizationSpec) -> VerificationResult:
        results: List[CheckResult] = []
        violations: List[str] = []
        logger.info(f"Starting static verification for spec: {spec.spec_id}")
        logger.debug(f"Specification version: {spec.version}")

        # Execute each checker in sequence and log results
        for checker in self.checkers:
            result = checker.check(spec)
            results.append(result)

            status = "✓ PASS" if result.passed else "✗ FAIL"
            logger.info(f"  [{status}] {result.checker_name}")

            if not result.passed:
                violations.extend(result.violations)
                for v in result.violations:
                    logger.debug(f"    - {v}")

        passed = len(violations) == 0
        reason = None if not violations else "; ".join(violations)

        if passed:
            logger.info(
                f"✓ Verification PASSED for spec: {spec.spec_id} ({len(self.checkers)} checks passed)"
            )
        else:
            logger.warning(
                f"✗ Verification FAILED for spec: {spec.spec_id} with {len(violations)} violation(s)"
            )
            logger.warning(f"  Reason: {reason}")

        return VerificationResult(passed=passed, results=results, failure_reason=reason)
