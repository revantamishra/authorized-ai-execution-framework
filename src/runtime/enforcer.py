from .monitored_context import MonitoredContext, RuntimeViolation
from ..verification.verification_orchestrator import VerificationOrchestrator
from ..specification.authorization_spec import AuthorizationSpec



class RuntimeEnforcer:
    """
    Executes AI tasks strictly within verified authorization boundaries.
    """

    def __init__(self):
        self.verifier = VerificationOrchestrator()

    def execute(self, spec: AuthorizationSpec, task):
        verification = self.verifier.verify(spec)

        if not verification.passed:
            return {
                "success": False,
                "error": "Static verification failed",
                "details": verification.failure_reason,
            }

        ctx = MonitoredContext(spec)

        try:
            result = task(ctx)
            return {
                "success": True,
                "result": result,
            }
        except RuntimeViolation as e:
            return {
                "success": False,
                "runtime_violation": str(e),
            }
