# Package root: src/

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

    @staticmethod
    def adversarial_iteration_task(ctx: MonitoredContext) -> str:
        """
        Example task that appears compliant but exceeds iteration limits at runtime.

        - Passes static verification (spec allows up to 3 iterations)
        - Attempts to perform 5 iterations, violating runtime boundary
        - Shows framework catches clever violations that weren't declared upfront

        Args:
            ctx: The monitored execution context

        Raises:
            RuntimeViolation: When iteration limit exceeded
        """
        # This looks innocent - just accessing allowed inputs
        ctx.tick()
        data = ctx.read_input("database", "users_table")
        ctx.perform_action("read", "summary")
        
        # But then we try to loop beyond our declared limit
        ctx.tick()
        ctx.tick()
        ctx.tick()
        # This next tick() will exceed max_iterations=3 and raise RuntimeViolation
        ctx.tick()
        
        return f"Processed {data}"

    @staticmethod
    def adversarial_data_size_task(ctx: MonitoredContext) -> str:
        """
        Example task that appears compliant but exceeds data size limit at runtime.

        - Passes static verification
        - Declares allowed input but attempts to read so much data it exceeds max_data_size
        - Shows framework prevents data exfiltration through multiple reads

        Args:
            ctx: The monitored execution context

        Raises:
            RuntimeViolation: When max_data_size exceeded
        """
        # Attempt to read the same input multiple times, accumulating data
        ctx.tick()
        # With max_data_size=1000, reading ~50 times will exceed it (27 bytes * 50 = 1350)
        for i in range(50):
            try:
                ctx.read_input("database", "users_table")
            except Exception:
                # Expected to fail when we hit the limit
                raise
        
        return "Should not reach here"
