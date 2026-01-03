# Package root: src/

"""Risk scoring system for authorization specifications.

Analyzes a spec and assigns a risk score (0.0 = safe, 1.0 = dangerous).
Helps users understand the relative safety of their specifications.
"""

from dataclasses import dataclass
from typing import List

from specification.authorization_spec import AuthorizationSpec


@dataclass(frozen=True)
class RiskAssessment:
    """Result of risk scoring analysis."""

    overall_risk: float  # 0.0 (safe) to 1.0 (dangerous)
    risk_factors: List[str]  # Human-readable risk factors
    recommendations: List[str]  # How to reduce risk
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

    def __repr__(self) -> str:
        return f"RiskAssessment(severity={self.severity}, risk={self.overall_risk:.2f})"


class RiskScorer:
    """Evaluates the relative safety and reasonableness of a spec."""

    # Conservative heuristic bounds for typical AI workloads (2026)
    SAFE_ITERATIONS = 1000  # Most tasks finish in < 1000 steps
    WARN_ITERATIONS = 10000  # Getting loose
    SAFE_DATA_SIZE = 100 * 1024 * 1024  # 100 MB is reasonable
    WARN_DATA_SIZE = 1024 * 1024 * 1024  # 1 GB is very large
    SAFE_TIMEOUT = 300  # 5 minutes is typical
    WARN_TIMEOUT = 3600  # 1 hour is long

    def score_spec(self, spec: AuthorizationSpec) -> RiskAssessment:
        """
        Analyze a spec and return a risk assessment.

        Factors considered:
        - Iteration limits (high iterations = more opportunity for DoS/loops)
        - Data size limits (large sizes = more data exfiltration potential)
        - Timeout (long timeouts = more time to attack)
        - Number of allowed inputs (more sources = larger attack surface)
        - Number of permitted actions (more actions = more capabilities)

        Args:
            spec: The authorization specification to assess

        Returns:
            RiskAssessment with overall score, factors, and recommendations
        """
        risk = 0.0
        factors = []
        recommendations = []

        scope = spec.execution_scope
        if not scope:
            return RiskAssessment(
                overall_risk=1.0,
                risk_factors=["No execution scope defined"],
                recommendations=["Add an execution_scope to the spec"],
                severity="CRITICAL",
            )

        # Check iteration limits
        if scope.max_iterations > self.WARN_ITERATIONS:
            risk += 0.25
            factors.append(
                f"High iteration limit ({scope.max_iterations:,} > {self.WARN_ITERATIONS:,})"
            )
            recommendations.append(
                f"Reduce max_iterations from {scope.max_iterations} to {self.WARN_ITERATIONS} or lower"
            )
        elif scope.max_iterations > self.SAFE_ITERATIONS:
            risk += 0.10
            factors.append(
                f"Moderate iteration limit ({scope.max_iterations:,} > {self.SAFE_ITERATIONS:,})"
            )

        # Check data size limits
        if scope.max_data_size > self.WARN_DATA_SIZE:
            risk += 0.30
            factors.append(
                f"Large data size limit ({scope.max_data_size / (1024**3):.1f} GB > 1 GB)"
            )
            recommendations.append(
                f"Reduce max_data_size from {scope.max_data_size / (1024**3):.1f} GB to ≤ 100 MB unless justified"
            )
        elif scope.max_data_size > self.SAFE_DATA_SIZE:
            risk += 0.15
            factors.append(
                f"Moderate data size limit ({scope.max_data_size / (1024**2):.1f} MB > 100 MB)"
            )

        # Check timeout
        if scope.timeout_seconds > self.WARN_TIMEOUT:
            risk += 0.20
            factors.append(
                f"Long timeout ({scope.timeout_seconds}s > {self.WARN_TIMEOUT}s)"
            )
            recommendations.append(
                f"Reduce timeout_seconds from {scope.timeout_seconds} to {self.WARN_TIMEOUT} or lower"
            )
        elif scope.timeout_seconds > self.SAFE_TIMEOUT:
            risk += 0.10
            factors.append(
                f"Moderate timeout ({scope.timeout_seconds}s > {self.SAFE_TIMEOUT}s)"
            )

        # Check input surface area
        num_inputs = len(spec.allowed_inputs)
        if num_inputs > 10:
            risk += 0.15
            factors.append(f"Large input surface area ({num_inputs} allowed sources)")
            recommendations.append(
                f"Consider limiting to ≤ 5 input sources unless all are necessary"
            )

        # Check action surface area
        num_actions = len(spec.permitted_actions)
        if num_actions > 20:
            risk += 0.15
            factors.append(
                f"Large action surface area ({num_actions} permitted actions)"
            )
            recommendations.append(
                f"Consider limiting to ≤ 10 actions unless all are necessary"
            )

        # Clamp risk to [0.0, 1.0]
        overall_risk = min(1.0, risk)

        # Determine severity
        if overall_risk >= 0.7:
            severity = "CRITICAL"
        elif overall_risk >= 0.5:
            severity = "HIGH"
        elif overall_risk >= 0.3:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Default recommendation if no risks found
        if not recommendations:
            recommendations.append("No security concerns detected. Spec appears reasonable.")

        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=factors if factors else ["No risk factors detected"],
            recommendations=recommendations,
            severity=severity,
        )
