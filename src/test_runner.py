# Package root: src/

"""Simple test runner that doesn't require pytest."""

import sys
import traceback

# Core tests that don't require pytest decorators
def test_completeness_checker_valid_spec():
    """Valid spec with all required fields should pass."""
    from specification.authorization_spec import AuthorizationSpec, ForbiddenPattern
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.completeness_checker import CompletenessChecker

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
    print("✓ test_completeness_checker_valid_spec")


def test_risk_scorer_safe_spec():
    """Conservative spec should have low risk."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.risk_scorer import RiskScorer

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
    print("✓ test_risk_scorer_safe_spec")


def test_spec_explainer_generates_output():
    """Spec should convert to clear English."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.spec_explainer import SpecExplainer

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
    print("✓ test_spec_explainer_generates_output")


def test_verification_report_audit_hash():
    """Verification report should include audit hash."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.verification_orchestrator import VerificationOrchestrator

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
    print("✓ test_verification_report_audit_hash")


def test_verification_report_risk_assessment():
    """Report should include risk assessment."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.verification_orchestrator import VerificationOrchestrator

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
    print("✓ test_verification_report_risk_assessment")


def test_audit_json_export():
    """Report should export to JSON for compliance."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.verification_orchestrator import VerificationOrchestrator

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
    print("✓ test_audit_json_export")


def test_monitored_context_iteration_limit():
    """Exceeding max_iterations should raise RuntimeViolation."""
    from specification.authorization_spec import AuthorizationSpec
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from runtime.monitored_context import MonitoredContext, RuntimeViolation

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
    try:
        ctx.tick()  # Third tick should fail
        assert False, "Expected RuntimeViolation"
    except RuntimeViolation:
        print("✓ test_monitored_context_iteration_limit")


def test_forbidden_data_wildcard_overlap():
    """Wildcard patterns should be checked against allowed inputs."""
    from specification.authorization_spec import AuthorizationSpec, ForbiddenPattern
    from specification.models import AllowedInput, ExecutionScope, PermittedAction
    from verification.forbidden_data_checker import ForbiddenDataChecker

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
    print("✓ test_forbidden_data_wildcard_overlap")


if __name__ == "__main__":
    tests = [
        test_completeness_checker_valid_spec,
        test_risk_scorer_safe_spec,
        test_spec_explainer_generates_output,
        test_verification_report_audit_hash,
        test_verification_report_risk_assessment,
        test_audit_json_export,
        test_monitored_context_iteration_limit,
        test_forbidden_data_wildcard_overlap,
    ]

    passed = 0
    failed = 0

    print("\n" + "=" * 70)
    print("  RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 70 + "\n")

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__}: {e}")
            traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70 + "\n")

    sys.exit(0 if failed == 0 else 1)
