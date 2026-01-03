# Package root: src/

"""Human-readable spec generator.

Converts an AuthorizationSpec into clear English text for review and auditing.
Helps non-technical stakeholders understand what an AI system is allowed to do.
"""

from specification.authorization_spec import AuthorizationSpec


class SpecExplainer:
    """Generates human-readable descriptions of authorization specs."""

    @staticmethod
    def explain(spec: AuthorizationSpec) -> str:
        """
        Convert a spec to plain English.

        Args:
            spec: The authorization specification

        Returns:
            A multi-line English description of the spec
        """
        lines = []

        # Title
        lines.append(f"AUTHORIZATION SPECIFICATION: {spec.spec_id}")
        lines.append(f"Version: {spec.version}")
        lines.append("")

        # Allowed inputs
        lines.append("ALLOWED DATA SOURCES:")
        if spec.allowed_inputs:
            for inp in spec.allowed_inputs:
                lines.append(
                    f"  • {inp.source_type.upper()}: {inp.source_id} "
                    f"(schema: {inp.data_schema})"
                )
        else:
            lines.append("  • None (system cannot read any inputs)")
        lines.append("")

        # Forbidden inputs
        lines.append("FORBIDDEN DATA SOURCES:")
        if spec.forbidden_inputs:
            for forbidden in spec.forbidden_inputs:
                lines.append(
                    f"  • {forbidden.pattern_type}: {forbidden.pattern_value} "
                    f"(reason: {forbidden.reason})"
                )
        else:
            lines.append("  • None explicitly forbidden")
        lines.append("")

        # Permitted actions
        lines.append("PERMITTED ACTIONS:")
        if spec.permitted_actions:
            for action in spec.permitted_actions:
                params = (
                    f"with parameters {action.parameters_schema}"
                    if action.parameters_schema
                    else "with no parameters"
                )
                lines.append(
                    f"  • {action.action_type.upper()} on {action.target_type} {params}"
                )
        else:
            lines.append("  • None (system cannot perform any actions)")
        lines.append("")

        # Execution scope
        scope = spec.execution_scope
        lines.append("EXECUTION BOUNDARIES:")
        lines.append(f"  • Max iterations: {scope.max_iterations:,}")
        lines.append(
            f"  • Max data size: {SpecExplainer._format_bytes(scope.max_data_size)}"
        )
        lines.append(f"  • Timeout: {scope.timeout_seconds}s ({SpecExplainer._format_time(scope.timeout_seconds)})")
        if scope.allowed_resources:
            lines.append(f"  • Allowed resources: {', '.join(scope.allowed_resources)}")
        lines.append("")

        # Summary
        lines.append("SUMMARY:")
        input_names = ", ".join([inp.source_id for inp in spec.allowed_inputs])
        action_names = ", ".join(
            [f"{a.action_type}({a.target_type})" for a in spec.permitted_actions]
        )
        lines.append(
            f"This AI system may read from {input_names or 'no sources'}, "
            f"perform actions: {action_names or 'none'}, and execute within "
            f"{scope.max_iterations:,} iterations and {scope.timeout_seconds}s timeout."
        )

        return "\n".join(lines)

    @staticmethod
    def _format_bytes(num_bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if num_bytes < 1024:
                return f"{num_bytes:.1f} {unit}"
            num_bytes /= 1024
        return f"{num_bytes:.1f} PB"

    @staticmethod
    def _format_time(seconds: int) -> str:
        """Format seconds as human-readable time."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
