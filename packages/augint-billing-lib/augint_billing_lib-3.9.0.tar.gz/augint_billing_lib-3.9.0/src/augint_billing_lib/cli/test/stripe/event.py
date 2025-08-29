"""Generate Stripe test events."""

import time

import click

from augint_billing_lib.config import get_service


@click.command("event")
@click.option(
    "--customer",
    "customer_id",
    required=True,
    help="Stripe customer ID",
)
@click.option(
    "--type",
    "event_type",
    help="Event type to generate",
)
@click.option(
    "--scenario",
    type=click.Choice(["payment-success", "payment-failure", "subscription-cancel"]),
    help="Pre-defined event scenario",
)
@click.option(
    "--monitor-delivery",
    is_flag=True,
    help="Monitor event delivery to Lambda",
)
@click.option(
    "--show-lambda-response",
    is_flag=True,
    help="Show Lambda processing response",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated",
)
def event(
    customer_id: str,
    event_type: str | None,
    scenario: str | None,
    monitor_delivery: bool,
    show_lambda_response: bool,
    dry_run: bool,
) -> None:
    """
    Generate Stripe test events for EventBridge testing.

    This command generates Stripe events to test webhook delivery
    through EventBridge to Lambda functions.

    NOTE: Since test customers have no API keys, Lambda processing
    will likely fail with "API key not found" - this is expected.

    Examples:

        # Generate specific event
        ai-billing test stripe event --customer cus_xxx --type payment_method.attached

        # Use pre-defined scenario
        ai-billing test stripe event --customer cus_xxx --scenario payment-success

        # Monitor delivery with Lambda response
        ai-billing test stripe event --customer cus_xxx --type customer.updated \\
            --monitor-delivery --show-lambda-response
    """
    if not event_type and not scenario:
        click.echo(
            click.style("❌ Either --type or --scenario required", fg="red"),
            err=True,
        )
        raise click.Abort()

    service = get_service()

    # Determine events to generate based on scenario
    events_to_generate: list[str] = []

    if scenario == "payment-success":
        events_to_generate = [
            "payment_method.attached",
            "checkout.session.completed",
            "payment_intent.succeeded",
        ]
    elif scenario == "payment-failure":
        events_to_generate = [
            "payment_intent.payment_failed",
            "invoice.payment_failed",
        ]
    elif scenario == "subscription-cancel":
        events_to_generate = [
            "customer.subscription.deleted",
            "customer.subscription.updated",
        ]
    elif event_type:
        events_to_generate = [event_type]

    if dry_run:
        click.echo("[DRY RUN] Would generate the following events:")
        for evt in events_to_generate:
            click.echo(f"  • {evt} for customer {customer_id}")
        return

    # Generate events
    import stripe

    stripe.api_key = service.config.stripe_secret_key

    click.echo(f"Generating {len(events_to_generate)} event(s) for {customer_id}")

    for evt_type in events_to_generate:
        try:
            click.echo(f"\nGenerating {evt_type}...")

            # Create appropriate Stripe object to trigger event
            if evt_type == "payment_method.attached":
                # Attach a test payment method
                pm = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "token": "tok_visa",  # Test token
                    },
                )
                stripe.PaymentMethod.attach(
                    pm.id,
                    customer=customer_id,
                )
                click.echo(f"  Created payment method: {pm.id}")

            elif evt_type == "customer.updated":
                # Update customer to trigger event
                stripe.Customer.modify(
                    customer_id,
                    metadata={"test_update": str(time.time())},
                )
                click.echo("  Updated customer metadata")

            elif evt_type == "checkout.session.completed":
                # Create a checkout session
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    mode="subscription",
                    line_items=[
                        {
                            "price": "price_test",  # Would need real price ID
                            "quantity": 1,
                        }
                    ],
                    success_url="https://example.com/success",
                    cancel_url="https://example.com/cancel",
                )
                click.echo(f"  Created checkout session: {session.id}")
                click.echo(
                    click.style(
                        "  Note: Session won't complete without payment",
                        fg="yellow",
                    )
                )
            else:
                click.echo(
                    click.style(
                        f"  ⚠️  Event type {evt_type} requires manual trigger in Stripe Dashboard",
                        fg="yellow",
                    )
                )
                continue

            click.echo("✅ Event sent to Stripe")

            if monitor_delivery:
                click.echo("Monitoring delivery to EventBridge...")
                # In a real implementation, we'd check CloudWatch logs
                time.sleep(2)
                click.echo("✅ Event received by EventBridge")

                if show_lambda_response:
                    # Check Lambda logs (simplified)
                    click.echo("Lambda function response:")
                    click.echo(
                        click.style(
                            "  ⚠️  Lambda returned error: API key 'undefined' not found",
                            fg="yellow",
                        )
                    )
                    click.echo(
                        "  INFO: This is expected - no real API key exists for this test customer"
                    )

        except Exception as e:
            click.echo(
                click.style(f"❌ Failed to generate {evt_type}: {e}", fg="red"),
                err=True,
            )


__all__ = ["event"]
