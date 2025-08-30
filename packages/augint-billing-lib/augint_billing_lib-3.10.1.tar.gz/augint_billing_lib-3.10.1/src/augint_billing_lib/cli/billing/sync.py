"""Sync usage to Stripe."""

import time
from datetime import UTC, datetime, timedelta

import click

from augint_billing_lib.config import get_service


@click.command("sync")
@click.option(
    "--auto",
    is_flag=True,
    help="Automatically detect time window",
)
@click.option(
    "--since",
    type=click.DateTime(),
    help="Start of time window (ISO format)",
)
@click.option(
    "--until",
    type=click.DateTime(),
    help="End of time window (ISO format)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force sync even if already reported",
)
@click.option(
    "--retry",
    type=int,
    default=1,
    help="Number of retries on failure",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be synced without sending",
)
def sync(
    auto: bool,
    since: datetime | None,
    until: datetime | None,
    force: bool,
    retry: int,
    dry_run: bool,
) -> None:
    """
    Sync API usage to Stripe for billing.

    This command reports API usage from CloudWatch to Stripe for all
    customers on metered plans. It handles idempotency and retries.

    Examples:

        # Auto-detect window (last complete hour)
        ai-billing core sync --auto

        # Sync specific time window
        ai-billing core sync --since 2025-01-01T00:00:00Z --until 2025-01-01T01:00:00Z

        # Force re-sync with retries
        ai-billing core sync --force --retry 3
    """
    service = get_service()

    # Determine time window
    if auto:
        # Use last complete hour
        now = datetime.now(UTC)
        until = now.replace(minute=0, second=0, microsecond=0)
        since = until - timedelta(hours=1)
        click.echo(f"Auto-detected window: {since.isoformat()} to {until.isoformat()}")
    elif not since or not until:
        click.echo(
            click.style(
                "❌ Either --auto or both --since and --until required",
                fg="red",
            ),
            err=True,
        )
        raise click.Abort()

    # Ensure timezone awareness
    if since and since.tzinfo is None:
        since = since.replace(tzinfo=UTC)
    if until and until.tzinfo is None:
        until = until.replace(tzinfo=UTC)

    click.echo(f"Syncing usage from {since.isoformat()} to {until.isoformat()}")

    if dry_run:
        click.echo("[DRY RUN] Would sync usage for the following customers:")

        # Get all metered customers
        customers = service.customer_repo.get_metered_customers()
        click.echo(f"Found {len(customers)} metered customers")

        for customer in customers[:5]:  # Show first 5
            click.echo(f"  • {customer.api_key_id} -> {customer.stripe_customer_id}")
        if len(customers) > 5:
            click.echo(f"  ... and {len(customers) - 5} more")

        return

    # Perform sync with retries
    attempt = 0

    while attempt < retry:
        attempt += 1

        try:
            if attempt > 1:
                click.echo(f"Retry attempt {attempt}/{retry}...")

            # Call reconcile_usage_window
            result = service.reconcile_usage_window(
                since,  # window_start
                until,  # window_end
            )

            # Report results
            if isinstance(result, dict):
                click.echo(
                    click.style(
                        f"✅ Successfully synced usage for {result.get('customers_processed', 0)} customers",
                        fg="green",
                    )
                )

                if result.get("errors"):
                    click.echo(
                        click.style(
                            f"⚠️  {len(result['errors'])} customers had errors",
                            fg="yellow",
                        )
                    )
                    for error in result["errors"][:3]:
                        click.echo(f"  • {error}")
            else:
                # result is a list of report dicts
                click.echo(
                    click.style(
                        f"✅ Successfully synced usage for {len(result)} customers",
                        fg="green",
                    )
                )

            return

        except Exception as e:
            if attempt < retry:
                click.echo(
                    click.style(f"⚠️  Attempt {attempt} failed: {e}", fg="yellow"),
                    err=True,
                )
                # Exponential backoff
                time.sleep(2**attempt)
            else:
                click.echo(
                    click.style(f"❌ All {retry} attempts failed: {e}", fg="red"),
                    err=True,
                )
                raise


__all__ = ["sync"]
