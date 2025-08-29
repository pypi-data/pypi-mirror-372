"""Integration testing with real API keys."""

import click

from augint_billing_lib.cli.test.integration.cycle import cycle
from augint_billing_lib.cli.test.integration.link import link
from augint_billing_lib.cli.test.integration.reporting import reporting
from augint_billing_lib.cli.test.integration.traffic import traffic


@click.group(
    name="integration",
    help="""
    Integration testing with REAL API keys.

    These commands test the complete billing flow using real API keys
    from your application. They require:

    • An existing API key from API Gateway
    • A Stripe customer (can be created with 'test stripe customer')
    • Proper AWS and Stripe configuration

    IMPORTANT: These commands work with REAL resources:
    • Generate actual API traffic (billable)
    • Create real usage records
    • Affect production systems if not careful

    Always use test/staging environments when possible.
    """,
)
def integration_group() -> None:
    """Integration test group."""


# Add commands
integration_group.add_command(link)
integration_group.add_command(traffic)
integration_group.add_command(cycle)
integration_group.add_command(reporting)


__all__ = ["integration_group"]
