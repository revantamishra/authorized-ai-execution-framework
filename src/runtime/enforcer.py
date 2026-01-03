import logging
from typing import Any, Callable, Dict

from runtime.monitored_context import MonitoredContext, RuntimeViolation
from specification.authorization_spec import AuthorizationSpec
from verification.verification_orchestrator import VerificationOrchestrator

logger = logging.getLogger(__name__)


class RuntimeEnforcer:
    """
    Enforces authorization at runtime.

    Execution flow:
    1. Static verification of the authorization spec
    2. Creation of monitored execution context
    3. Execution of the task within the monitored context
    4. Capture of any runtime violations
    """

    def __init__(self):
        """Initialize the enforcer with a verification orchestrator."""
        self.verifier = VerificationOrchestrator()

    def execute(
        self,
        spec: AuthorizationSpec,
        task: Callable[[MonitoredContext], Any],
    ) -> Dict[str, Any]:
        """
        Execute a task under the constraints of an authorization specification.

        Two-phase execution:
        - Phase 1: Static verification of spec
        - Phase 2: Runtime enforcement during task execution

        Args:
            spec: The authorization specification
            task: The function to execute (must accept MonitoredContext as parameter)

        Returns:
            Dict with execution result:
            {
                "success": bool,
                "result": Any (if success),
                "error": str (if failure),
                "details": str (if failure)
            }
        """
        logger.info(f"Enforcer: Beginning execution for spec {spec.spec_id}")

        # Phase 1: Static Verification
        logger.debug("Enforcer: Phase 1 - Static Verification")
        verification = self.verifier.verify(spec)

        if not verification.passed:
            logger.error(
                f"Enforcer: Static verification failed: {verification.failure_reason}"
            )
            return {
                "success": False,
                "error": "Static verification failed",
                "details": verification.failure_reason,
            }

        logger.info("Enforcer: Static verification passed - proceeding to runtime")

        # Phase 2: Runtime Enforcement
        logger.debug("Enforcer: Phase 2 - Runtime Enforcement")
        ctx = MonitoredContext(spec)

        try:
            logger.debug(f"Enforcer: Executing task with monitored context")
            result = task(ctx)
            logger.info(f"Enforcer: Task completed successfully")
            return {"success": True, "result": result}

        except RuntimeViolation as e:
            logger.error(f"Enforcer: Runtime violation detected: {str(e)}")
            return {
                "success": False,
                "error": "Runtime violation",
                "details": str(e),
            }

        except Exception as e:
            logger.error(f"Enforcer: Unexpected error during execution: {str(e)}")
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e),
            }
