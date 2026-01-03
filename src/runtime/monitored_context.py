import logging
from typing import Any

from specification.authorization_spec import AuthorizationSpec

logger = logging.getLogger(__name__)


class RuntimeViolation(Exception):
    """Exception raised when runtime execution violates authorization boundaries."""

    pass


class MonitoredContext:
    """
    Provides a constrained execution environment for AI system tasks.

    The context enforces authorization at runtime by:
    - Validating all data access against allowed inputs
    - Validating all actions against permitted actions
    - Tracking iteration count and enforcing max_iterations

    Any unauthorized access or action raises RuntimeViolation.
    """

    def __init__(self, spec: AuthorizationSpec):
        """
        Initialize the monitored context with authorization boundaries.

        Args:
            spec: The authorization specification defining allowed operations
        """
        self.spec = spec
        self.iterations = 0
        logger.debug(f"MonitoredContext initialized for spec {spec.spec_id}")

    def read_input(self, source_type: str, source_id: str) -> Any:
        """
        Read input data from an authorized source.

        Args:
            source_type: The type of data source (e.g., 'database', 'file')
            source_id: The identifier of the specific source

        Returns:
            Simulated data from the authorized source

        Raises:
            RuntimeViolation: If the source is not in allowed_inputs
        """
        # Check if the requested input is in allowed_inputs
        for allowed in self.spec.allowed_inputs:
            if allowed.source_type == source_type and allowed.source_id == source_id:
                logger.debug(f"✓ Authorized read: {source_type}:{source_id}")
                return f"[DATA from {source_id}]"

        # Source not authorized
        logger.error(f"✗ Unauthorized read attempt: {source_type}:{source_id}")
        raise RuntimeViolation(
            f"Unauthorized input access: {source_type}:{source_id} "
            f"(not in allowed_inputs)"
        )

    def perform_action(self, action_type: str, target_type: str) -> None:
        """
        Perform an authorized action.

        Args:
            action_type: The type of action to perform (e.g., 'read', 'write')
            target_type: The type of target being acted upon (e.g., 'summary', 'file')

        Raises:
            RuntimeViolation: If the action is not in permitted_actions
        """
        # Check if the requested action is in permitted_actions
        for action in self.spec.permitted_actions:
            if action.action_type == action_type and action.target_type == target_type:
                logger.debug(f"✓ Authorized action: {action_type} on {target_type}")
                return

        # Action not authorized
        logger.error(f"✗ Unauthorized action attempt: {action_type} on {target_type}")
        raise RuntimeViolation(
            f"Unauthorized action: {action_type} on {target_type} "
            f"(not in permitted_actions)"
        )

    def tick(self) -> None:
        """
        Increment iteration counter and check if max_iterations exceeded.

        Call this once per main loop iteration.

        Raises:
            RuntimeViolation: If iterations exceed max_iterations
        """
        self.iterations += 1
        max_iter = self.spec.execution_scope.max_iterations

        if self.iterations > max_iter:
            logger.error(f"✗ Iteration limit exceeded: {self.iterations} > {max_iter}")
            raise RuntimeViolation(
                f"Execution scope exceeded: "
                f"{self.iterations} iterations > {max_iter} limit"
            )

        logger.debug(f"Iteration {self.iterations}/{max_iter}")
