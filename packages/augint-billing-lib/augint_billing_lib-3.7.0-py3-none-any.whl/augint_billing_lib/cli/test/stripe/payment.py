"""Simulate payment scenarios."""

import click

from augint_billing_lib.config import get_service


@click.command("payment")
@click.option(
    "--customer",
    "customer_id",
    required=True,
    help="Stripe customer ID",
)
@click.option(
    "--scenario",
    type=click.Choice(["success", "failure", "retry", "expired"]),
    required=True,
    help="Payment scenario to simulate",
)
@click.option(
    "--amount",
    type=float,
    default=10.00,
    help="Payment amount",
)
def payment(
    customer_id: str,
    scenario: str,
    amount: float,
) -> None:
    """
    Simulate payment scenarios for testing.

    This command simulates various payment scenarios to test
    how the system handles different payment states.

    Example:
        ai-billing test stripe payment --customer cus_xxx --scenario failure
    """
    service = get_service()

    import stripe

    stripe.api_key = service.config.stripe_secret_key

    click.echo(f"Simulating {scenario} payment scenario for {customer_id}")

    try:
        if scenario == "success":
            # Create successful payment
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                customer=customer_id,
                payment_method="pm_card_visa",
                confirm=True,
                description=f"Test payment - {scenario}",
            )
            click.echo(f"✅ Payment succeeded: {intent.id}")

        elif scenario == "failure":
            # Use card that always fails
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),
                    currency="usd",
                    customer=customer_id,
                    payment_method="pm_card_chargeCustomerFail",
                    confirm=True,
                    description=f"Test payment - {scenario}",
                )
            except stripe.error.CardError as e:
                click.echo(f"✅ Payment failed as expected: {e.user_message}")

        elif scenario == "retry":
            click.echo("Creating payment that requires retry...")
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency="usd",
                customer=customer_id,
                description=f"Test payment - {scenario}",
            )
            click.echo(f"Payment intent created: {intent.id}")
            click.echo("Status: requires_payment_method")
            click.echo("This payment can be retried with a valid payment method")

        elif scenario == "expired":
            click.echo("Creating payment that will expire...")
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency="usd",
                customer=customer_id,
                description=f"Test payment - {scenario}",
            )
            click.echo(f"Payment intent created: {intent.id}")
            click.echo("This payment will expire if not completed within 24 hours")

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to simulate payment: {e}", fg="red"),
            err=True,
        )
        raise


__all__ = ["payment"]
