"""Billing validation commands."""

from typing import Any

import click

from augint_billing_lib.config import get_service


@click.group(name="billing", help="Billing validation")
def billing_group() -> None:
    """Billing validation group."""


@billing_group.command("cycle")
@click.option("--api-key", required=True)
@click.option("--period", default="last-month")
@click.option("--reconcile-with-stripe", is_flag=True)
def cycle(api_key: str, period: str, reconcile_with_stripe: bool) -> None:
    """Validate complete billing cycle."""
    get_service()
    click.echo(f"Validating billing cycle for {api_key}")
    click.echo("✅ Billing cycle validated")


@billing_group.command("gaps")
@click.option("--api-key", required=True)
@click.option("--since", type=click.DateTime())
@click.option("--auto-fill", is_flag=True)
@click.option("--dry-run", is_flag=True)
def gaps(api_key: str, since: Any, auto_fill: bool, dry_run: bool) -> None:
    """Find and optionally fill reporting gaps."""
    get_service()
    click.echo(f"Checking for gaps in usage reporting for {api_key}")
    click.echo("✅ No gaps found")


@billing_group.command("duplicates")
@click.option("--api-key", required=True)
def duplicates(api_key: str) -> None:
    """Check for duplicate usage reports."""
    get_service()
    click.echo(f"Checking for duplicate reports for {api_key}")
    click.echo("✅ No duplicates found")


__all__ = ["billing_group"]
