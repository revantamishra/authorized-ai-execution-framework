# Package root: src/

"""Comprehensive test suite for the authorization framework.

Tests cover:
- Each checker's validation logic
- Edge cases and boundary conditions
- Spec compliance and violation detection
"""

import pytest

from specification.authorization_spec import AuthorizationSpec, ForbiddenPattern
from specification.models import AllowedInput, ExecutionScope, PermittedAction
from verification.action_boundary_checker import ActionBoundaryChecker
from verification.completeness_checker import CompletenessChecker
from verification.forbidden_data_checker import ForbiddenDataChecker
from verification.scope_boundedness_checker import ScopeBoundednessChecker
from verification.risk_scorer import RiskScorer
from verification.spec_explainer import SpecExplainer
from verification.verification_orchestrator import VerificationOrchestrator
from runtime.monitored_context import MonitoredContext, RuntimeViolation
from runtime.enforcer import RuntimeEnforcer


class TestCompletenessChecker:
    """Test CompletenessChecker validation."""

    def test_valid_spec_passes(self):
        """Valid spec with all required fields should pass."""
        spec = AuthorizationSpec(
            spec_id="test-1",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = CompletenessChecker()
        result = checker.check(spec)
        assert result.passed is True
        assert len(result.violations) == 0

    def test_missing_allowed_inputs_fails(self):
        """Spec without allowed_inputs should fail."""
        spec = AuthorizationSpec(
            spec_id="test-2",
            version="1.0",
            allowed_inputs=[],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = CompletenessChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("allowed inputs" in v.lower() for v in result.violations)

    def test_missing_forbidden_inputs_fails(self):
        """Spec with None forbidden_inputs should fail."""
        spec = AuthorizationSpec(
            spec_id="test-3",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=None,
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = CompletenessChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("forbidden" in v.lower() for v in result.violations)

    def test_empty_forbidden_inputs_passes(self):
        """Empty forbidden_inputs list (explicit) should pass."""
        spec = AuthorizationSpec(
            spec_id="test-4",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = CompletenessChecker()
        result = checker.check(spec)
        assert result.passed is True


class TestScopeBoundednessChecker:
    """Test ScopeBoundednessChecker validation."""

    def test_valid_bounds_pass(self):
        """Valid positive bounds should pass."""
        scope = ExecutionScope(max_iterations=100, max_data_size=1000, timeout_seconds=60)
        spec = AuthorizationSpec(
            spec_id="test-5",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=scope,
        )
        checker = ScopeBoundednessChecker()
        result = checker.check(spec)
        assert result.passed is True

    def test_zero_iterations_fails(self):
        """max_iterations <= 0 should fail."""
        scope = ExecutionScope(max_iterations=0, max_data_size=1000, timeout_seconds=60)
        spec = AuthorizationSpec(
            spec_id="test-6",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=scope,
        )
        checker = ScopeBoundednessChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("max_iterations" in v.lower() for v in result.violations)

    def test_negative_timeout_fails(self):
        """timeout_seconds < 0 should fail."""
        scope = ExecutionScope(max_iterations=100, max_data_size=1000, timeout_seconds=-1)
        spec = AuthorizationSpec(
            spec_id="test-7",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=scope,
        )
        checker = ScopeBoundednessChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("timeout" in v.lower() for v in result.violations)


class TestForbiddenDataChecker:
    """Test ForbiddenDataChecker overlap detection."""

    def test_no_overlap_passes(self):
        """Non-overlapping forbidden and allowed inputs should pass."""
        spec = AuthorizationSpec(
            spec_id="test-8",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users_table", {})],
            forbidden_inputs=[ForbiddenPattern("exact", "passwords_table", "sensitive")],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = ForbiddenDataChecker()
        result = checker.check(spec)
        assert result.passed is True

    def test_exact_overlap_fails(self):
        """Forbidden pattern exactly matching allowed input should fail."""
        spec = AuthorizationSpec(
            spec_id="test-9",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users_table", {})],
            forbidden_inputs=[ForbiddenPattern("exact", "users_table", "oops")],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = ForbiddenDataChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("overlap" in v.lower() for v in result.violations)

    def test_wildcard_overlap_detection(self):
        """Wildcard patterns should be checked against allowed inputs."""
        spec = AuthorizationSpec(
            spec_id="test-10",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "user_profile", {})],
            forbidden_inputs=[ForbiddenPattern("wildcard", "user_*", "user tables forbidden")],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        checker = ForbiddenDataChecker()
        result = checker.check(spec)
        assert result.passed is False
        assert any("pattern" in v.lower() and "match" in v.lower() for v in result.violations)


class TestRiskScorer:
    """Test risk assessment logic."""

    def test_safe_spec_has_low_risk(self):
        """Conservative spec should have low risk."""
        spec = AuthorizationSpec(
            spec_id="test-11",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100, max_data_size=1024*1024, timeout_seconds=60),
        )
        scorer = RiskScorer()
        assessment = scorer.score_spec(spec)
        assert assessment.overall_risk < 0.3
        assert assessment.severity == "LOW"

    def test_loose_iterations_increases_risk(self):
        """High iteration limits should increase risk score."""
        spec = AuthorizationSpec(
            spec_id="test-12",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100000, max_data_size=1024*1024, timeout_seconds=60),
        )
        scorer = RiskScorer()
        assessment = scorer.score_spec(spec)
        assert assessment.overall_risk > 0.2
        assert any("iteration" in f.lower() for f in assessment.risk_factors)

    def test_large_data_size_increases_risk(self):
        """Large data size limits should increase risk."""
        spec = AuthorizationSpec(
            spec_id="test-13",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100, max_data_size=10*1024*1024*1024, timeout_seconds=60),
        )
        scorer = RiskScorer()
        assessment = scorer.score_spec(spec)
        assert assessment.overall_risk > 0.2
        assert any("data" in f.lower() for f in assessment.risk_factors)


class TestSpecExplainer:
    """Test human-readable spec generation."""

    def test_explain_generates_readable_output(self):
        """Spec should convert to clear English."""
        spec = AuthorizationSpec(
            spec_id="test-14",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users_table", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100, max_data_size=1024*1024, timeout_seconds=60),
        )
        explainer = SpecExplainer()
        text = explainer.explain(spec)
        assert "AUTHORIZATION SPECIFICATION" in text
        assert "users_table" in text
        assert "read" in text.lower()
        assert "100" in text  # iterations

    def test_explain_includes_boundaries(self):
        """Explanation should include execution boundaries."""
        spec = AuthorizationSpec(
            spec_id="test-15",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "data", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("write", "log", {})],
            execution_scope=ExecutionScope(max_iterations=50, max_data_size=512*1024, timeout_seconds=120),
        )
        explainer = SpecExplainer()
        text = explainer.explain(spec)
        assert "50" in text  # iterations
        assert "120" in text  # timeout
        assert "512" in text or "512.0" in text  # data size


class TestMonitoredContextBoundaries:
    """Test runtime enforcement of boundaries."""

    def test_iteration_limit_enforced(self):
        """Exceeding max_iterations should raise RuntimeViolation."""
        spec = AuthorizationSpec(
            spec_id="test-16",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=2, max_data_size=1024*1024, timeout_seconds=60),
        )
        ctx = MonitoredContext(spec)
        ctx.tick()
        ctx.tick()
        with pytest.raises(RuntimeViolation):
            ctx.tick()  # Third tick should fail

    def test_data_size_limit_enforced(self):
        """Exceeding max_data_size should raise RuntimeViolation."""
        spec = AuthorizationSpec(
            spec_id="test-17",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=1000, max_data_size=10, timeout_seconds=60),  # Very small
        )
        ctx = MonitoredContext(spec)
        ctx.tick()
        with pytest.raises(RuntimeViolation):
            # "[DATA from users]" is 27 bytes, exceeds 10 byte limit
            ctx.read_input("db", "users")


class TestVerificationOrchestrator:
    """Test end-to-end verification."""

    def test_full_verification_pipeline(self):
        """Complete spec should pass all checkers."""
        spec = AuthorizationSpec(
            spec_id="test-18",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "users", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100, max_data_size=1024*1024, timeout_seconds=60),
        )
        orchestrator = VerificationOrchestrator()
        report = orchestrator.verify(spec)
        assert report.passed is True
        assert len(report.checker_results) == 4
        assert all(r.passed for r in report.checker_results)
        assert report.audit_hash  # Should be computed
        assert report.risk_assessment is not None

    def test_audit_hash_is_computed(self):
        """Verification report should include audit hash."""
        spec = AuthorizationSpec(
            spec_id="test-19",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "data", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        orchestrator = VerificationOrchestrator()
        report = orchestrator.verify(spec)
        assert len(report.audit_hash) == 64  # SHA256 hex is 64 chars
        assert report.audit_hash.isalnum()

    def test_risk_assessment_included(self):
        """Report should include risk assessment."""
        spec = AuthorizationSpec(
            spec_id="test-20",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "data", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        orchestrator = VerificationOrchestrator()
        report = orchestrator.verify(spec)
        assert report.risk_assessment is not None
        assert report.risk_assessment.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert 0.0 <= report.risk_assessment.overall_risk <= 1.0

    def test_audit_json_export(self):
        """Report should export to JSON for compliance."""
        spec = AuthorizationSpec(
            spec_id="test-21",
            version="1.0",
            allowed_inputs=[AllowedInput("db", "data", {})],
            forbidden_inputs=[],
            permitted_actions=[PermittedAction("read", "summary", {})],
            execution_scope=ExecutionScope(max_iterations=100),
        )
        orchestrator = VerificationOrchestrator()
        report = orchestrator.verify(spec)
        json_export = report.to_audit_json()
        assert "passed" in json_export
        assert "audit_hash" in json_export
        assert "risk_assessment" in json_export
        assert "checker_results" in json_export


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
