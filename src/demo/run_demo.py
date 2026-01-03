# Package root: src/

"""Demo runner for the Authorized AI Execution Framework.

Shows a compliant and a violating task under the framework's
static verification and runtime enforcement.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from runtime.enforcer import RuntimeEnforcer
from runtime.mock_ai import MockAISystem
from specification.authorization_spec import AuthorizationSpec
from specification.models import AllowedInput, ExecutionScope, PermittedAction
from verification.spec_explainer import SpecExplainer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def _print_section(title: str) -> None:
    """Print a visually distinct section header for demo output."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def _print_risk_assessment(report: Any) -> None:
    """Pretty-print risk assessment from VerificationReport."""
    if not hasattr(report, 'risk_assessment') or not report.risk_assessment:
        return
    
    ra = report.risk_assessment
    print(f"\n[RISK ASSESSMENT]")
    print(f"  Severity: {ra.severity}")
    print(f"  Overall Risk Score: {ra.overall_risk:.2f} / 1.00")
    if ra.risk_factors:
        print(f"  Risk Factors:")
        for factor in ra.risk_factors:
            print(f"    - {factor}")
    if ra.recommendations:
        print(f"  Recommendations:")
        for rec in ra.recommendations:
            print(f"    - {rec}")


def _print_audit_trail(report: Any) -> None:
    """Print audit hash for compliance."""
    if hasattr(report, 'audit_hash') and report.audit_hash:
        print(f"\n[AUDIT TRAIL]")
        print(f"  Hash: {report.audit_hash[:16]}... (SHA256)")
        print(f"  Full: {report.audit_hash}")


def _export_audit_json(report: Any, filename: str) -> None:
    """Export audit report to JSON file."""
    if hasattr(report, 'to_audit_json'):
        with open(filename, 'w') as f:
            f.write(report.to_audit_json())
        print(f"\n[AUDIT EXPORT] Saved to {filename}")


def _print_result(label: str, result: Dict[str, Any]) -> None:
    """Pretty-print execution result dictionaries."""
    print(f"\n[{label}]")
    if result.get("success"):
        print("  Status: [PASS] SUCCESS")
        print(f"  Result: {result.get('result')}")
    else:
        print("  Status: [FAIL] FAILED")
        print(f"  Error: {result.get('error')}")
        print(f"  Details: {result.get('details')}")


def main() -> None:
    """Build a minimal AuthorizationSpec and run the compliant/violating demos."""
    _print_section("AUTHORIZED AI EXECUTION DEMO")

    spec = AuthorizationSpec(
        spec_id="demo-spec-001",
        version="1.0",
        allowed_inputs=[
            AllowedInput(
                source_type="database",
                source_id="users_table",
                data_schema={"columns": ["id", "name"]},
            )
        ],
        forbidden_inputs=[],  # Explicitly declared as empty
        permitted_actions=[
            PermittedAction(
                action_type="read", target_type="summary", parameters_schema={}
            )
        ],
        execution_scope=ExecutionScope(
            max_iterations=3,
            max_data_size=1_000,  # 1 KB for demo purposes
            timeout_seconds=60,
            allowed_resources=["database"],
        ),
    )

    # Show human-readable explanation
    _print_section("SPECIFICATION EXPLANATION")
    explainer = SpecExplainer()
    print(explainer.explain(spec))

    enforcer = RuntimeEnforcer()

    _print_section("TEST 1: COMPLIANT TASK (Should Pass)")
    result_ok = enforcer.execute(spec, MockAISystem.compliant_task)
    _print_result("Compliant Task", result_ok)

    _print_section("TEST 2: UNAUTHORIZED ACCESS TASK (Should Fail)")
    result_bad = enforcer.execute(spec, MockAISystem.violating_task)
    _print_result("Unauthorized Access Task", result_bad)

    _print_section("TEST 3: ADVERSARIAL ITERATION TASK (Passes static, fails at runtime)")
    print("This task appears compliant during static verification but violates")
    print("iteration limits at runtime. This demonstrates that static checks alone")
    print("are insufficient - runtime enforcement is critical.\n")
    result_adv_iter = enforcer.execute(spec, MockAISystem.adversarial_iteration_task)
    _print_result("Adversarial Iteration Task", result_adv_iter)

    _print_section("TEST 4: ADVERSARIAL DATA SIZE TASK (Passes static, fails at runtime)")
    print("This task shows data exfiltration prevention: it accumulates data")
    print("across multiple read operations until it exceeds the declared limit.\n")
    result_adv_data = enforcer.execute(spec, MockAISystem.adversarial_data_size_task)
    _print_result("Adversarial Data Size Task", result_adv_data)

    # Show risk assessment and audit trail from a fresh verification
    _print_section("SECURITY ASSESSMENT & COMPLIANCE")
    from verification.verification_orchestrator import VerificationOrchestrator
    orchestrator = VerificationOrchestrator()
    report = orchestrator.verify(spec)
    _print_risk_assessment(report)
    _print_audit_trail(report)
    _export_audit_json(report, "audit_report.json")


if __name__ == "__main__":
    main()
