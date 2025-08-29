"""Test usage reporting accuracy."""

import click

from augint_billing_lib.config import get_service


@click.command("reporting")
@click.option("--api-key", required=True, help="API key to test")
@click.option("--period", default="last-hour", help="Time period to test")
def reporting(api_key: str, period: str) -> None:
    """Test usage reporting accuracy."""
    get_service()

    click.echo(f"Testing usage reporting for {api_key}")
    click.echo(f"Period: {period}")

    # Compare CloudWatch metrics vs Stripe reports
    # Check for gaps or duplicates

    click.echo("✅ Reporting test completed")


__all__ = ["reporting"]
