"""Educational simulation commands."""

import click

from augint_billing_lib.cli.test.simulate.explain import explain
from augint_billing_lib.cli.test.simulate.flow import flow
from augint_billing_lib.cli.test.simulate.scenario import scenario


@click.group(
    name="simulate",
    help="""
    Educational simulation (no real resources).

    These commands simulate the complete billing flow without creating
    or modifying any real resources. Perfect for:

    • Understanding how the system works
    • Learning the billing flow
    • Planning integration tests
    • Training and documentation

    All operations are simulated - no actual API calls or state changes.
    """,
)
def simulate_group() -> None:
    """Simulate test group."""


# Add commands
simulate_group.add_command(flow)
simulate_group.add_command(scenario)
simulate_group.add_command(explain)


__all__ = ["simulate_group"]
