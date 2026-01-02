from .monitored_context import MonitoredContext



class MockAISystem:
    """
    Simulated AI system.
    Behaves like an agent requesting inputs and actions.
    """

    @staticmethod
    def compliant_task(ctx: MonitoredContext):
        ctx.tick()
        data = ctx.read_input("database", "users_table")
        ctx.perform_action("read", "summary")
        return f"Processed {data}"

    @staticmethod
    def violating_task(ctx: MonitoredContext):
        ctx.tick()
        ctx.read_input("database", "passwords_table")  # should fail
