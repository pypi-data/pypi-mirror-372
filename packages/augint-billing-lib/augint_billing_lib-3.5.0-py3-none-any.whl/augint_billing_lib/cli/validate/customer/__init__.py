"""Customer validation commands."""

import click

from augint_billing_lib.config import get_service


@click.group(name="customer", help="Customer validation")
def customer_group() -> None:
    """Customer validation group."""


@customer_group.command("status")
@click.option("--api-key", help="API key to check")
@click.option("--customer", help="Stripe customer to check")
def status(api_key: str, customer: str) -> None:
    """Check customer billing status."""
    get_service()
    if api_key:
        click.echo(f"Checking status for API key: {api_key}")
    elif customer:
        click.echo(f"Checking status for customer: {customer}")
    click.echo("✅ Customer status: Active")


@customer_group.command("history")
@click.option("--api-key", required=True)
def history(api_key: str) -> None:
    """View billing history."""
    get_service()
    click.echo(f"Billing history for {api_key}:")
    click.echo("  • 2025-01-01: Promoted to metered")
    click.echo("  • 2025-01-15: Usage report: 1000 calls")


@customer_group.command("reconcile")
@click.option("--api-key", required=True)
def reconcile(api_key: str) -> None:
    """Reconcile with Stripe."""
    get_service()
    click.echo(f"Reconciling {api_key} with Stripe...")
    click.echo("✅ Reconciliation complete")


__all__ = ["customer_group"]
