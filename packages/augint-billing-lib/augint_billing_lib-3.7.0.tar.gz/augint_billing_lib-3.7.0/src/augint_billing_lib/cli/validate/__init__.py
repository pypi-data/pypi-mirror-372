"""Validation and verification commands."""

import click

from augint_billing_lib.cli.validate.billing import billing_group
from augint_billing_lib.cli.validate.config import config_group
from augint_billing_lib.cli.validate.customer import customer_group


@click.group(
    name="validate",
    help="""
    Validation and verification commands.

    These commands verify that the billing system is properly configured
    and functioning correctly. Use them to:

    • Check system configuration
    • Validate billing cycles
    • Verify customer state
    • Find and fix issues
    """,
)
def validate_group() -> None:
    """Validate command group."""


# Add subgroups
validate_group.add_command(config_group)
validate_group.add_command(billing_group)
validate_group.add_command(customer_group)


__all__ = ["validate_group"]
