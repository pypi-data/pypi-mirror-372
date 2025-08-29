"""List Stripe products."""

import sys

import click
import stripe
from stripe.error import StripeError

from augint_billing_lib.cli.config import get_config


def get_stripe_key(environment: str | None) -> str:
    """Get the appropriate Stripe key for the environment."""
    config = get_config(environment)
    key = config.get_stripe_key()

    if not key:
        if environment == "production":
            click.echo(
                click.style(
                    "❌ No production Stripe key found",
                    fg="red",
                )
            )
        elif environment == "staging":
            click.echo(
                click.style(
                    "❌ No staging Stripe key found",
                    fg="red",
                )
            )
        else:
            click.echo(
                click.style(
                    "❌ No Stripe key found",
                    fg="red",
                )
            )
        sys.exit(1)

    return key


@click.command("list")
@click.option(
    "--environment",
    type=click.Choice(["staging", "production"]),
    help="Environment to list products for (uses appropriate Stripe key)",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    help="Maximum number of products to list",
)
@click.option(
    "--show-prices",
    is_flag=True,
    help="Also show prices for each product",
)
@click.option(
    "--filter-created-by-cli",
    is_flag=True,
    help="Only show products created by ai-billing CLI",
)
def list_products(
    environment: str | None,
    limit: int,
    show_prices: bool,
    filter_created_by_cli: bool,
) -> None:
    """
    List products in your Stripe account.

    Examples:
        # List all products
        ai-billing products list

        # List products for staging environment
        ai-billing products list --environment staging

        # List products with their prices
        ai-billing products list --show-prices

        # List only products created by this CLI
        ai-billing products list --filter-created-by-cli
    """
    # Get Stripe key
    stripe_key = get_stripe_key(environment)
    stripe.api_key = stripe_key

    # Set API version to match setup command
    stripe.api_version = "2024-06-20"

    # Determine mode
    mode = "TEST" if stripe_key.startswith("sk_test") else "LIVE"
    env_str = f" ({environment})" if environment else ""
    click.echo(f"\n📋 Listing products in Stripe {mode} mode{env_str}\n")

    try:
        # Fetch products
        products = stripe.Product.list(limit=limit)

        if not products.data:
            click.echo("No products found")
            return

        # Filter if requested
        display_products = products.data
        if filter_created_by_cli:
            display_products = [
                p for p in products.data if p.metadata.get("created_by") == "ai-billing-cli"
            ]
            if not display_products:
                click.echo("No products created by ai-billing CLI found")
                return

        # Display products
        for product in display_products:
            # Product header
            active_status = "✅" if product.active else "❌"
            click.echo(f"{active_status} {click.style(product.name, bold=True)} [{product.id}]")

            # Product details
            if product.description:
                click.echo(f"   Description: {product.description}")

            # Metadata
            if product.metadata:
                env_meta = product.metadata.get("environment")
                model_meta = product.metadata.get("model")
                created_by = product.metadata.get("created_by")

                metadata_parts = []
                if env_meta:
                    metadata_parts.append(f"env: {env_meta}")
                if model_meta:
                    metadata_parts.append(f"model: {model_meta}")
                if created_by:
                    metadata_parts.append(f"created by: {created_by}")

                if metadata_parts:
                    click.echo(f"   Metadata: {', '.join(metadata_parts)}")

            # Show prices if requested
            if show_prices:
                try:
                    prices = stripe.Price.list(product=product.id, limit=10)
                    if prices.data:
                        click.echo("   Prices:")
                        for price in prices.data:
                            active = "✓" if price.active else "✗"

                            # Format price description
                            if price.type == "recurring":
                                if price.recurring.get("usage_type") == "metered":
                                    if price.billing_scheme == "tiered":
                                        tier_count = (
                                            len(price.tiers) if hasattr(price, "tiers") else 0
                                        )
                                        desc = f"Metered with {tier_count} tiers"
                                    else:
                                        amount = (
                                            price.unit_amount / 100.0 if price.unit_amount else 0
                                        )
                                        desc = f"Metered at ${amount:.3f}/unit"
                                else:
                                    amount = price.unit_amount / 100.0 if price.unit_amount else 0
                                    interval = price.recurring.get("interval", "month")
                                    desc = f"${amount:.2f}/{interval}"
                            else:
                                amount = price.unit_amount / 100.0 if price.unit_amount else 0
                                desc = f"${amount:.2f} one-time"

                            click.echo(f"     {active} {desc} [{price.id}]")
                    else:
                        click.echo("   No prices configured")
                except StripeError:
                    click.echo("   Could not fetch prices")

            click.echo()  # Blank line between products

        # Summary
        total_count = len(display_products)
        if filter_created_by_cli:
            click.echo(f"Showing {total_count} product(s) created by ai-billing CLI")
        else:
            click.echo(f"Showing {total_count} of {len(products.data)} product(s)")

        if products.has_more:
            click.echo("More products available. Use --limit to see more.")

    except StripeError as e:
        click.echo(click.style(f"❌ Stripe error: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


__all__ = ["list_products"]
