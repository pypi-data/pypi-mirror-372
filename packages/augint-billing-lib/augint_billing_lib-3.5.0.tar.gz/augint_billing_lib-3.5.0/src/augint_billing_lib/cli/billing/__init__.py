"""Billing operational commands for production use."""

import click

from augint_billing_lib.cli.billing.env import env_group
from augint_billing_lib.cli.billing.process import process
from augint_billing_lib.cli.billing.sync import sync


@click.group(
    name="billing",
    help="""
    Billing operational commands for production use.

    These commands are production-ready and work with real resources.
    They handle environment configuration, usage synchronization, and
    event processing.

    Commands:
    • env     - Environment configuration management
    • sync    - Sync usage to Stripe
    • process - Process Stripe events
    """,
)
def billing_group() -> None:
    """Billing command group."""


# Add subcommands
billing_group.add_command(env_group)
billing_group.add_command(sync)
billing_group.add_command(process)


__all__ = ["billing_group"]
