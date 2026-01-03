from runtime.monitored_context import MonitoredContext


class MockAISystem:
    """
    Mock AI system demonstrating compliant and violating task patterns.

    Used for testing and demonstration purposes.
    """

    @staticmethod
    def compliant_task(ctx: MonitoredContext) -> str:
        """
        Example task that respects all authorization boundaries.

        - Only accesses allowed inputs
        - Only performs permitted actions
        - Respects iteration limits

        Args:
            ctx: The monitored execution context

        Returns:
            Result of the compliant task execution
        """
        ctx.tick()
        data = ctx.read_input("database", "users_table")
        ctx.perform_action("read", "summary")
        return f"Processed {data}"

    @staticmethod
    def violating_task(ctx: MonitoredContext) -> str:
        """
        Example task that violates authorization boundaries.

        - Attempts to access forbidden inputs (passwords_table)
        - Will raise RuntimeViolation

        Args:
            ctx: The monitored execution context

        Raises:
            RuntimeViolation: When attempting unauthorized access
        """
        ctx.tick()
        # This access is not in allowed_inputs and will raise RuntimeViolation
        data = ctx.read_input("database", "passwords_table")
        return f"Processed {data}"
