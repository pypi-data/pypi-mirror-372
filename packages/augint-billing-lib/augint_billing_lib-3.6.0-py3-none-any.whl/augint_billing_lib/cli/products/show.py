"""Show detailed information about a Stripe product."""

import json
import sys
from datetime import UTC
from typing import Any

import click
import stripe
from stripe.error import StripeError

from augint_billing_lib.cli.config import get_config


def get_stripe_key() -> str:
    """Get the Stripe key from environment."""
    config = get_config(None)  # Use default environment
    key = config.get_stripe_key()

    if not key:
        click.echo(
            click.style(
                "❌ No Stripe key found. Set STRIPE_SECRET_KEY or use environment-specific keys",
                fg="red",
            )
        )
        sys.exit(1)

    return key


def format_tier(tier: dict[str, Any], index: int) -> str:
    """Format a pricing tier for display."""
    parts = [f"Tier {index}:"]

    if tier.get("up_to") == "inf":
        parts.append("unlimited")
    else:
        parts.append(f"up to {tier.get('up_to'):,}")

    if tier.get("unit_amount") is not None:
        amount = tier["unit_amount"] / 100.0
        parts.append(f"@ ${amount:.3f}/unit")
    elif tier.get("flat_amount") is not None:
        amount = tier["flat_amount"] / 100.0
        parts.append(f"flat ${amount:.2f}")

    return " ".join(parts)


@click.command("show")
@click.argument("product_id")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
def show_product(product_id: str, output_json: bool) -> None:
    """
    Show detailed information about a Stripe product.

    Examples:
        # Show product details
        ai-billing products show prod_abc123

        # Output as JSON
        ai-billing products show prod_abc123 --json
    """
    # Get Stripe key
    stripe_key = get_stripe_key()
    stripe.api_key = stripe_key

    # Set API version to match setup command
    stripe.api_version = "2024-06-20"

    # Determine mode
    mode = "TEST" if stripe_key.startswith("sk_test") else "LIVE"

    try:
        # Fetch product
        product = stripe.Product.retrieve(product_id)

        # Fetch associated prices
        prices = stripe.Price.list(product=product_id, limit=100)

        if output_json:
            # JSON output
            output: dict[str, Any] = {
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "active": product.active,
                    "metadata": dict(product.metadata) if product.metadata else {},
                    "created": product.created,
                },
                "prices": [],
            }

            for price in prices.data:
                price_data = {
                    "id": price.id,
                    "active": price.active,
                    "currency": price.currency,
                    "type": price.type,
                }

                if price.type == "recurring":
                    price_data["recurring"] = {
                        "interval": price.recurring.get("interval"),
                        "usage_type": price.recurring.get("usage_type"),
                    }

                if price.unit_amount is not None:
                    price_data["unit_amount"] = price.unit_amount
                    price_data["unit_amount_decimal"] = price.unit_amount / 100.0

                if price.billing_scheme:
                    price_data["billing_scheme"] = price.billing_scheme

                if hasattr(price, "tiers") and price.tiers:
                    price_data["tiers"] = []
                    for tier in price.tiers:
                        tier_data = {}
                        if tier.get("up_to"):
                            tier_data["up_to"] = tier["up_to"]
                        if tier.get("unit_amount") is not None:
                            tier_data["unit_amount"] = tier["unit_amount"]
                            tier_data["unit_amount_decimal"] = tier["unit_amount"] / 100.0
                        if tier.get("flat_amount") is not None:
                            tier_data["flat_amount"] = tier["flat_amount"]
                            tier_data["flat_amount_decimal"] = tier["flat_amount"] / 100.0
                        price_data["tiers"].append(tier_data)

                if price.metadata:
                    price_data["metadata"] = dict(price.metadata)

                output["prices"].append(price_data)

            click.echo(json.dumps(output, indent=2))

        else:
            # Human-readable output
            click.echo(f"\n📦 Product Details (Stripe {mode} mode)\n")
            click.echo("=" * 60)

            # Product info
            active_status = "✅ Active" if product.active else "❌ Inactive"
            click.echo(f"{active_status}")
            click.echo(f"Name: {click.style(product.name, bold=True)}")
            click.echo(f"ID: {product.id}")

            if product.description:
                click.echo(f"Description: {product.description}")

            # Metadata
            if product.metadata:
                click.echo("\nMetadata:")
                for key, value in product.metadata.items():
                    click.echo(f"  {key}: {value}")

            # Created timestamp
            if hasattr(product, "created"):
                from datetime import datetime

                created_dt = datetime.fromtimestamp(product.created, tz=UTC)
                click.echo(f"\nCreated: {created_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")

            # Prices
            click.echo("\n" + "=" * 60)
            click.echo("💰 Prices")
            click.echo("=" * 60)

            if not prices.data:
                click.echo("No prices configured")
            else:
                # Separate prices by type
                subscription_prices = []
                metered_prices = []
                one_time_prices = []

                for price in prices.data:
                    if price.type == "recurring":
                        if price.recurring.get("usage_type") == "metered":
                            metered_prices.append(price)
                        else:
                            subscription_prices.append(price)
                    else:
                        one_time_prices.append(price)

                # Display subscription prices
                if subscription_prices:
                    click.echo("\n📅 Subscription Prices:")
                    for price in subscription_prices:
                        active = "✅" if price.active else "❌"
                        amount = price.unit_amount / 100.0 if price.unit_amount else 0
                        interval = price.recurring.get("interval", "month")
                        click.echo(f"\n  {active} ${amount:.2f}/{interval}")
                        click.echo(f"     ID: {price.id}")
                        click.echo(f"     Currency: {price.currency.upper()}")
                        if price.metadata:
                            click.echo(f"     Metadata: {dict(price.metadata)}")

                # Display metered prices
                if metered_prices:
                    click.echo("\n📊 Metered Usage Prices:")
                    for price in metered_prices:
                        active = "✅" if price.active else "❌"
                        click.echo(f"\n  {active} Metered billing")
                        click.echo(f"     ID: {price.id}")
                        click.echo(f"     Currency: {price.currency.upper()}")
                        click.echo(f"     Billing scheme: {price.billing_scheme}")

                        if price.billing_scheme == "tiered" and hasattr(price, "tiers"):
                            click.echo("     Pricing tiers:")
                            for i, tier in enumerate(price.tiers, 1):
                                click.echo(f"       {format_tier(tier, i)}")
                        elif price.unit_amount is not None:
                            amount = price.unit_amount / 100.0
                            click.echo(f"     Rate: ${amount:.3f}/unit")

                        if price.metadata:
                            click.echo(f"     Metadata: {dict(price.metadata)}")

                # Display one-time prices
                if one_time_prices:
                    click.echo("\n💵 One-Time Prices:")
                    for price in one_time_prices:
                        active = "✅" if price.active else "❌"
                        amount = price.unit_amount / 100.0 if price.unit_amount else 0
                        click.echo(f"\n  {active} ${amount:.2f}")
                        click.echo(f"     ID: {price.id}")
                        click.echo(f"     Currency: {price.currency.upper()}")
                        if price.metadata:
                            click.echo(f"     Metadata: {dict(price.metadata)}")

            # Environment variable suggestions
            click.echo("\n" + "=" * 60)
            click.echo("🔧 Configuration")
            click.echo("=" * 60)

            click.echo("\nSuggested environment variables:")
            click.echo(f'API_USAGE_PRODUCT_ID="{product.id}"')

            for price in prices.data:
                if price.type == "recurring" and price.recurring.get("usage_type") != "metered":
                    click.echo(f'BASE_SUBSCRIPTION_PRICE_ID="{price.id}"')
                    break

            for price in prices.data:
                if price.type == "recurring" and price.recurring.get("usage_type") == "metered":
                    click.echo(f'METERED_USAGE_PRICE_ID="{price.id}"')
                    break

    except StripeError as e:
        if e.http_status == 404:
            click.echo(click.style(f"❌ Product '{product_id}' not found", fg="red"), err=True)
        else:
            click.echo(click.style(f"❌ Stripe error: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


__all__ = ["show_product"]
