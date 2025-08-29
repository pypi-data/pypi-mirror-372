"""Stripe-only testing commands (no API keys)."""

import click

from augint_billing_lib.cli.test.stripe.event import event
from augint_billing_lib.cli.test.stripe.payment import payment
from augint_billing_lib.cli.test.stripe.webhook import webhook


@click.group(
    name="stripe",
    help="""
    Stripe-only testing commands (NO API keys).

    These commands test Stripe integration WITHOUT requiring API keys.
    They are useful for:
    • Testing webhook delivery to EventBridge
    • Testing Lambda event processing
    • Validating Stripe configuration

    LIMITATIONS:
    • Test customers have NO API keys
    • Cannot test usage tracking
    • Cannot test complete billing cycles

    For full integration testing with API keys, use 'test integration' commands.
    """,
)
def stripe_group() -> None:
    """Stripe test group."""


# Add commands
stripe_group.add_command(event)
stripe_group.add_command(webhook)
stripe_group.add_command(payment)


__all__ = ["stripe_group"]
