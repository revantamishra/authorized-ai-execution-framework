# Package root: src/

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from specification.authorization_spec import AuthorizationSpec
from verification.action_boundary_checker import ActionBoundaryChecker
from verification.check_result import CheckResult
from verification.completeness_checker import CompletenessChecker
from verification.forbidden_data_checker import ForbiddenDataChecker
from verification.risk_scorer import RiskScorer, RiskAssessment
from verification.scope_boundedness_checker import ScopeBoundednessChecker

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerificationReport:
    """Auditable verification report from static verification."""

    passed: bool
    checker_results: List[CheckResult] = field(default_factory=list)
    failure_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    audit_hash: str = ""  # SHA256 of spec_id + results + timestamp
    risk_assessment: Optional[RiskAssessment] = None

    def __repr__(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        risk_str = f", risk={self.risk_assessment.severity}" if self.risk_assessment else ""
        return f"VerificationReport(status={status}, checks={len(self.checker_results)}, timestamp={self.timestamp.isoformat()}{risk_str})"

    def to_audit_json(self) -> str:
        """Export report as JSON for regulatory/compliance review."""
        return json.dumps(
            {
                "passed": self.passed,
                "timestamp": self.timestamp.isoformat(),
                "audit_hash": self.audit_hash,
                "checker_results": [
                    {
                        "checker_name": r.checker_name,
                        "passed": r.passed,
                        "violations": r.violations,
                    }
                    for r in self.checker_results
                ],
                "failure_reason": self.failure_reason,
                "risk_assessment": {
                    "overall_risk": self.risk_assessment.overall_risk,
                    "severity": self.risk_assessment.severity,
                    "risk_factors": self.risk_assessment.risk_factors,
                    "recommendations": self.risk_assessment.recommendations,
                }
                if self.risk_assessment
                else None,
            },
            indent=2,
        )



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
        self.risk_scorer = RiskScorer()

    def verify(self, spec: AuthorizationSpec) -> VerificationReport:
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

        # Compute audit hash
        now = datetime.now()
        audit_data = f"{spec.spec_id}|{now.isoformat()}|{len(results)}|{passed}"
        audit_hash = hashlib.sha256(audit_data.encode()).hexdigest()

        # Score risk
        risk_assessment = self.risk_scorer.score_spec(spec)
        logger.info(f"Risk assessment: {risk_assessment.severity} (score: {risk_assessment.overall_risk:.2f})")
        for factor in risk_assessment.risk_factors:
            logger.warning(f"  Risk factor: {factor}")

        if passed:
            logger.info(
                f"✓ Verification PASSED for spec: {spec.spec_id} ({len(self.checkers)} checks passed)"
            )
        else:
            logger.warning(
                f"✗ Verification FAILED for spec: {spec.spec_id} with {len(violations)} violation(s)"
            )
            logger.warning(f"  Reason: {reason}")

        return VerificationReport(
            passed=passed,
            checker_results=results,
            failure_reason=reason,
            timestamp=now,
            audit_hash=audit_hash,
            risk_assessment=risk_assessment,
        )

