"""Setup and initialization commands."""

import click

from augint_billing_lib.cli.setup.activate_eventbus import activate_eventbus
from augint_billing_lib.cli.setup.eventbridge import eventbridge
from augint_billing_lib.cli.setup.stripe_product import stripe_product
from augint_billing_lib.cli.setup.verify import verify


@click.group(
    name="setup",
    help="""
    Setup and initialization commands.

    These commands help configure the billing system infrastructure,
    including Stripe products, EventBridge integration, and verification.

    Commands:
    • stripe-product    - Create/update Stripe products with meter support
    • eventbridge       - Configure Stripe→EventBridge integration
    • activate-eventbus - Activate AWS partner event source
    • verify            - Comprehensive setup verification
    """,
)
def setup_group() -> None:
    """Setup command group."""


# Add subcommands
setup_group.add_command(stripe_product)
setup_group.add_command(eventbridge)
setup_group.add_command(activate_eventbus)
setup_group.add_command(verify)


__all__ = ["setup_group"]
