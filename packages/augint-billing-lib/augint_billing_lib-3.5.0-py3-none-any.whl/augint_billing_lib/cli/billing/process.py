"""Process Stripe events."""

import json

import click

from augint_billing_lib.bootstrap import process_event_and_apply_plan_moves
from augint_billing_lib.config import get_service


@click.command("process")
@click.option(
    "--file",
    "event_file",
    type=click.Path(exists=True),
    help="JSON file containing Stripe event",
)
@click.option(
    "--event-id",
    help="Stripe event ID to fetch and process",
)
@click.option(
    "--validate",
    is_flag=True,
    default=True,
    help="Validate event before processing",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would happen without processing",
)
def process(
    event_file: str | None,
    event_id: str | None,
    validate: bool,
    dry_run: bool,
) -> None:
    """
    Process Stripe events for billing updates.

    This command processes Stripe webhook events to update API key
    usage plans based on payment status changes.

    Examples:

        # Process event from file
        ai-billing core process --file event.json

        # Fetch and process event by ID
        ai-billing core process --event-id evt_xxx

        # Dry run to preview changes
        ai-billing core process --file event.json --dry-run
    """
    if not event_file and not event_id:
        click.echo(
            click.style("❌ Either --file or --event-id required", fg="red"),
            err=True,
        )
        raise click.Abort()

    service = get_service()

    # Load or fetch event
    if event_file:
        with open(event_file) as f:
            event_data = json.load(f)
        click.echo(f"Loaded event from {event_file}")
    else:
        # Fetch from Stripe
        try:
            import stripe

            stripe.api_key = service.config.stripe_secret_key
            event = stripe.Event.retrieve(event_id)
            event_data = dict(event)
            click.echo(f"Fetched event {event_id} from Stripe")
        except Exception as e:
            click.echo(
                click.style(f"❌ Failed to fetch event: {e}", fg="red"),
                err=True,
            )
            raise click.Abort()

    # Display event info
    click.echo(f"Event Type: {event_data.get('type')}")
    click.echo(f"Event ID:   {event_data.get('id')}")

    if validate:
        # Validate event structure
        required_fields = ["id", "type", "data"]
        missing = [f for f in required_fields if f not in event_data]
        if missing:
            click.echo(
                click.style(
                    f"❌ Invalid event: missing fields {missing}",
                    fg="red",
                ),
                err=True,
            )
            raise click.Abort()

    if dry_run:
        click.echo("\n[DRY RUN] Would process event:")
        click.echo(f"  Type: {event_data.get('type')}")

        # Show what would happen based on event type
        event_type = event_data.get("type")
        if event_type == "checkout.session.completed":
            click.echo("  Action: Promote API key to metered plan")
        elif event_type == "payment_method.attached":
            click.echo("  Action: Mark customer as having payment method")
        elif event_type == "customer.subscription.deleted":
            click.echo("  Action: Demote API key to free plan")
        else:
            click.echo(f"  Action: Process {event_type} event")

        # Show affected customer if available
        if "customer" in event_data.get("data", {}).get("object", {}):
            customer_id = event_data["data"]["object"]["customer"]
            click.echo(f"  Customer: {customer_id}")

        return

    # Process the event
    try:
        click.echo("Processing event...")
        result = process_event_and_apply_plan_moves(event_data)

        if result.get("success"):
            click.echo(click.style("✅ Event processed successfully", fg="green"))
            if result.get("action"):
                click.echo(f"  Action: {result['action']}")
            if result.get("api_key"):
                click.echo(f"  API Key: {result['api_key']}")
            if result.get("new_plan"):
                click.echo(f"  New Plan: {result['new_plan']}")
        else:
            click.echo(
                click.style(
                    f"⚠️  Event processed with warnings: {result.get('message')}",
                    fg="yellow",
                )
            )

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to process event: {e}", fg="red"),
            err=True,
        )
        raise


__all__ = ["process"]
