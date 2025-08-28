"""Create/update Stripe products with meter support."""

import os
import sys
from decimal import Decimal
from typing import Any

import click
import stripe

from augint_billing_lib.config import config


def create_meter_based_price(product_id: str, price_per_unit: Decimal) -> tuple[Any, Any]:
    """Create a meter-based price."""
    # Create meter for API usage - use getattr to avoid mypy error
    billing = getattr(stripe, "billing", None)
    if billing is None:
        raise ValueError(
            "Stripe billing API not available - please upgrade your Stripe API version"
        )
    Meter = getattr(billing, "Meter", None)
    if Meter is None:
        raise ValueError("Stripe Meter API not available - please upgrade your Stripe API version")

    meter = Meter.create(
        display_name="API Usage Meter",
        event_name="api_request",
        default_aggregation={"formula": "sum"},
        customer_facing_name="API Requests",
        value_settings={"interval": "month"},
    )

    # Create price with meter
    price = stripe.Price.create(
        product=product_id,
        currency="usd",
        billing_meter=meter.id,
        billing_scheme="per_unit",
        unit_amount=int(price_per_unit * 100),  # Convert to cents
        recurring={"usage_type": "metered", "interval": "month"},
        metadata={"created_by": "ai-billing-cli"},
    )

    return price, meter


@click.command("stripe-product")
@click.option(
    "--environment",
    type=click.Choice(["staging", "production"]),
    help="Environment to setup (uses appropriate Stripe key)",
)
@click.option(
    "--name",
    default="API Usage",
    help="Product name",
)
@click.option(
    "--price-per-unit",
    type=float,
    default=0.001,
    help="Price per API call (in dollars)",
)
@click.option(
    "--update-env",
    is_flag=True,
    default=True,
    help="Update .env file with created IDs",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without making changes",
)
def stripe_product(
    environment: str | None,
    name: str,
    price_per_unit: float,
    update_env: bool,
    dry_run: bool,
) -> None:
    """
    Create Stripe products for metered billing.

    This command creates the necessary Stripe products and prices for
    metered billing using Stripe's meter-based pricing.

    Example:
        ai-billing setup stripe-product --environment staging
    """
    # Determine which Stripe key to use
    if environment == "production":
        api_key = os.getenv("STRIPE_LIVE_SECRET_KEY")
        if not api_key:
            click.echo(
                click.style(
                    "❌ STRIPE_LIVE_SECRET_KEY not set for production",
                    fg="red",
                )
            )
            sys.exit(1)
    else:
        api_key = config.stripe_secret_key

    if not api_key:
        click.echo(
            click.style(
                "❌ No Stripe API key configured",
                fg="red",
            )
        )
        sys.exit(1)

    # Show environment
    mode = "TEST" if api_key.startswith("sk_test") else "LIVE"
    click.echo(f"Using Stripe {mode} mode")

    if dry_run:
        click.echo(
            click.style(
                "🔍 DRY RUN - No changes will be made",
                fg="yellow",
                bold=True,
            )
        )

    stripe.api_key = api_key

    try:
        # Check for existing product
        existing_products = stripe.Product.list(limit=100)
        api_product = None

        for product in existing_products.data:
            if product.name == name and product.metadata.get("created_by") == "ai-billing-cli":
                api_product = product
                click.echo(f"✅ Found existing product: {product.id}")
                break

        # Create product if needed
        if not api_product:
            if dry_run:
                click.echo(f"Would create product: {name}")
                api_product = type("obj", (object,), {"id": "prod_mock_123"})()
            else:
                api_product = stripe.Product.create(
                    name=name,
                    description=f"{name} - Metered billing",
                    metadata={
                        "created_by": "ai-billing-cli",
                        "environment": environment or "default",
                    },
                )
                click.echo(f"✅ Created product: {api_product.id}")

        # Check for existing price
        if not dry_run and api_product and hasattr(api_product, "id"):
            existing_prices = stripe.Price.list(product=api_product.id, limit=100)
            metered_price = None

            for price in existing_prices.data:
                if price.recurring and price.recurring.get("usage_type") == "metered":
                    metered_price = price
                    click.echo(f"✅ Found existing metered price: {price.id}")
                    break
        else:
            metered_price = None

        # Create price if needed
        meter = None
        if not metered_price:
            if dry_run:
                click.echo(f"Would create metered price at ${price_per_unit} per unit")
                metered_price = type("obj", (object,), {"id": "price_mock_123"})()
            else:
                metered_price, meter = create_meter_based_price(
                    api_product.id, Decimal(str(price_per_unit))
                )
                click.echo(f"✅ Created metered price: {metered_price.id}")
                if meter:
                    click.echo(f"✅ Created meter: {meter.id}")

        # Update .env file if requested
        if update_env and not dry_run:
            env_file = ".env"
            env_vars = {}

            # Read existing .env
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip('"')

            # Update with new values
            env_vars["METERED_PRODUCT_ID"] = (
                api_product.id if hasattr(api_product, "id") else "prod_mock_123"
            )
            env_vars["METERED_PRICE_ID"] = (
                metered_price.id if hasattr(metered_price, "id") else "price_mock_123"
            )
            if meter:
                env_vars["METERED_METER_ID"] = meter.id

            # Write updated .env
            with open(env_file, "w") as f:
                for key, value in sorted(env_vars.items()):
                    f.write(f'{key}="{value}"\n')

            click.echo(f"✅ Updated {env_file} with product IDs")

        # Summary
        click.echo("\n" + "=" * 50)
        click.echo(click.style("Setup Complete!", fg="green", bold=True))
        product_id = api_product.id if hasattr(api_product, "id") else "prod_mock_123"
        price_id = metered_price.id if hasattr(metered_price, "id") else "price_mock_123"
        click.echo(f"Product ID: {product_id}")
        click.echo(f"Price ID: {price_id}")
        if meter:
            click.echo(f"Meter ID: {meter.id}")
        click.echo(f"Price: ${price_per_unit} per unit")

        if not update_env:
            click.echo(
                click.style(
                    "\n⚠️  Remember to update your environment variables:",
                    fg="yellow",
                )
            )
            product_id = api_product.id if hasattr(api_product, "id") else "prod_mock_123"
            price_id = metered_price.id if hasattr(metered_price, "id") else "price_mock_123"
            click.echo(f'export METERED_PRODUCT_ID="{product_id}"')
            click.echo(f'export METERED_PRICE_ID="{price_id}"')
            if meter:
                click.echo(f'export METERED_METER_ID="{meter.id}"')

    except stripe.error.StripeError as e:
        click.echo(
            click.style(f"❌ Stripe error: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(
            click.style(f"❌ Error: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)


__all__ = ["stripe_product"]
