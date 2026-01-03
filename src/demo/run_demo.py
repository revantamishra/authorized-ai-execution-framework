"""Demo runner for the Authorized AI Execution Framework.

Shows a compliant and a violating task under the framework's
static verification and runtime enforcement.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from runtime.enforcer import RuntimeEnforcer
from runtime.mock_ai import MockAISystem
from specification.authorization_spec import AuthorizationSpec
from specification.models import AllowedInput, ExecutionScope, PermittedAction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def _print_section(title: str) -> None:
    """Print a visually distinct section header for demo output."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def _print_result(label: str, result: Dict[str, Any]) -> None:
    """Pretty-print execution result dictionaries."""
    print(f"\n[{label}]")
    if result.get("success"):
        print("  Status: ✓ SUCCESS")
        print(f"  Result: {result.get('result')}")
    else:
        print("  Status: ✗ FAILED")
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
            max_data_size=1_000_000,
            timeout_seconds=60,
            allowed_resources=["database"],
        ),
    )

    enforcer = RuntimeEnforcer()

    _print_section("TEST 1: COMPLIANT TASK (Should Pass)")
    result_ok = enforcer.execute(spec, MockAISystem.compliant_task)
    _print_result("Compliant Task", result_ok)

    _print_section("TEST 2: VIOLATING TASK (Should Fail)")
    result_bad = enforcer.execute(spec, MockAISystem.violating_task)
    _print_result("Violating Task", result_bad)


if __name__ == "__main__":
    main()
