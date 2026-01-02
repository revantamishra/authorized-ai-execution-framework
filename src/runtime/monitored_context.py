from typing import Any
from specification.authorization_spec import AuthorizationSpec



class RuntimeViolation(Exception):
    """Raised when an unauthorized runtime operation is attempted."""
    pass


class MonitoredContext:
    """
    The ONLY interface through which an AI system can interact
    with inputs, actions, or execution state.
    """

    def __init__(self, spec: AuthorizationSpec):
        self.spec = spec
        self.iterations = 0

    def read_input(self, source_type: str, source_id: str) -> Any:
        # Check authorization
        for allowed in self.spec.allowed_inputs:
            if allowed.source_type == source_type and allowed.source_id == source_id:
                return f"[DATA from {source_id}]"

        raise RuntimeViolation(
            f"Unauthorized input access: {source_type}:{source_id}"
        )

    def perform_action(self, action_type: str, target_type: str) -> None:
        for action in self.spec.permitted_actions:
            if action.action_type == action_type and action.target_type == target_type:
                return

        raise RuntimeViolation(
            f"Unauthorized action: {action_type} on {target_type}"
        )

    def tick(self) -> None:
        self.iterations += 1
        if self.iterations > self.spec.execution_scope.max_iterations:
            raise RuntimeViolation("Execution scope exceeded")
