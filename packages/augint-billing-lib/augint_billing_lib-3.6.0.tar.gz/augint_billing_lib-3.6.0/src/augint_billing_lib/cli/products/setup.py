"""Setup Stripe products and prices for an environment."""

import os
import sys
from pathlib import Path
from typing import Any

import click
import stripe
from dotenv import dotenv_values
from stripe.error import StripeError

from augint_billing_lib.cli.config import get_config


def get_stripe_key(environment: str) -> str:
    """Get the appropriate Stripe key for the environment."""
    config = get_config(environment)
    key = config.get_stripe_key()

    if not key:
        if environment == "production":
            click.echo(
                click.style(
                    "❌ No production Stripe key found (PROD_STRIPE_SECRET_KEY or STRIPE_LIVE_SECRET_KEY)",
                    fg="red",
                )
            )
        else:
            click.echo(
                click.style(
                    "❌ No staging Stripe key found (STAGING_STRIPE_SECRET_KEY or STRIPE_SECRET_KEY)",
                    fg="red",
                )
            )
        click.echo("\nConfiguration search order (highest to lowest precedence):")
        click.echo("1. Environment variables (export STAGING_STRIPE_SECRET_KEY=...)")
        click.echo("2. Current directory (./.env file)")
        click.echo("3. User config (~/.augint/.env file)")
        click.echo("\nTo fix, add to your .env file:")
        if environment == "staging":
            click.echo("STAGING_STRIPE_SECRET_KEY=sk_test_...")
        else:
            click.echo("PROD_STRIPE_SECRET_KEY=sk_live_...")
        sys.exit(1)

    return key


def get_stripe_key_source(environment: str) -> str:
    """Get the source of the Stripe key for diagnostic purposes."""
    config = get_config(environment)

    # Check in the same order as get_stripe_key
    keys_to_check = [
        ("STRIPE_SECRET_KEY", ""),
        ("STRIPE_TEST_SECRET_KEY", "") if environment != "production" else None,
        ("STRIPE_LIVE_SECRET_KEY", "") if environment == "production" else None,
    ]

    for key_tuple in keys_to_check:
        if key_tuple:
            key, _ = key_tuple
            if config.get(key):
                # Determine the source
                if key in os.environ:
                    return f"{key} (environment variable)"
                if (Path.cwd() / ".env").exists():
                    # Check if it's in local .env
                    local_config = dotenv_values(Path.cwd() / ".env")
                    if config._get_prefix() + key in local_config or key in local_config:
                        return f"{key} (local .env)"
                elif (Path.home() / ".augint" / ".env").exists():
                    return f"{key} (~/.augint/.env)"

    return "UNKNOWN"


def find_existing_product(name: str, environment: str) -> Any | None:
    """Find an existing product by name and environment."""
    try:
        # Ensure API key is set before making the call
        if not stripe.api_key:
            return None
        products = stripe.Product.list(limit=100)
        for product in products.data:
            if (
                product.name == name
                and product.metadata.get("environment") == environment
                and product.metadata.get("created_by") == "ai-billing-cli"
            ):
                return product
    except StripeError:
        pass
    return None


def create_subscription_price(
    product_id: str,
    amount: int,
    currency: str,
    interval: str = "month",
) -> Any:
    """Create a subscription price."""
    return stripe.Price.create(
        product=product_id,
        currency=currency,
        unit_amount=amount,
        recurring={"interval": interval},
        metadata={"created_by": "ai-billing-cli", "type": "subscription_base"},
    )


def create_metered_price_with_tiers(
    product_id: str,
    currency: str,
    tiers: list[dict[str, Any]],
) -> Any:
    """Create a metered price with graduated tiers."""
    # Stripe accepts "inf" as a string directly for the last tier
    # No need to convert or remove it
    return stripe.Price.create(
        product=product_id,
        currency=currency,
        recurring={
            "interval": "month",
            "usage_type": "metered",
        },
        billing_scheme="tiered",
        tiers_mode="graduated",
        tiers=tiers,  # Pass tiers directly, Stripe handles "inf"
        metadata={"created_by": "ai-billing-cli", "type": "metered_usage"},
    )


def calculate_example_bills(
    base_price: int,
    included_requests: int,
    tiers: list[dict[str, Any]],
    example_requests: list[int],
) -> dict[int, float]:
    """Calculate example monthly bills for different usage levels."""
    bills = {}

    for requests in example_requests:
        # Start with base subscription
        total_cents = base_price

        # Calculate billable requests (after included)
        billable = max(0, requests - included_requests)

        # Calculate tiered pricing
        remaining = billable
        for tier in tiers:
            if remaining <= 0:
                break

            # Determine how many units in this tier
            if tier.get("up_to") == "inf":
                units_in_tier = remaining
            else:
                tier_limit = tier["up_to"]
                # For first tier, it's just the limit
                # For subsequent tiers, need to account for previous tiers
                prev_tier_limit = 0
                for prev_tier in tiers:
                    if prev_tier == tier:
                        break
                    if prev_tier.get("up_to") != "inf":
                        prev_tier_limit = prev_tier["up_to"]

                tier_size = tier_limit - prev_tier_limit
                units_in_tier = min(remaining, tier_size)

            # Add cost for this tier
            if tier.get("unit_amount"):
                total_cents += units_in_tier * tier["unit_amount"]
            elif tier.get("flat_amount"):
                total_cents += tier["flat_amount"]

            remaining -= units_in_tier

        bills[requests] = total_cents / 100.0

    return bills


@click.command("setup")
@click.argument(
    "environment",
    type=click.Choice(["staging", "production"]),
)
@click.option(
    "--model",
    type=click.Choice(["subscription-plus-metered", "metered-only", "subscription-only"]),
    default="subscription-plus-metered",
    help="Pricing model to use",
)
@click.option(
    "--base-price",
    type=int,
    default=2999,
    help="Base subscription price in cents (default: 2999 for $29.99)",
)
@click.option(
    "--currency",
    default="usd",
    help="Currency code (default: usd)",
)
@click.option(
    "--included-requests",
    type=int,
    default=1000,
    help="Requests included in base subscription (default: 1000)",
)
@click.option(
    "--tier-1-limit",
    type=int,
    default=10000,
    help="Upper limit for tier 1 (default: 10000)",
)
@click.option(
    "--tier-1-price",
    type=int,
    default=10,
    help="Price per request in tier 1 in cents (default: 10 for $0.10)",
)
@click.option(
    "--tier-2-limit",
    type=int,
    default=100000,
    help="Upper limit for tier 2 (default: 100000)",
)
@click.option(
    "--tier-2-price",
    type=int,
    default=8,
    help="Price per request in tier 2 in cents (default: 8 for $0.08)",
)
@click.option(
    "--tier-3-price",
    type=int,
    default=5,
    help="Price per request in tier 3+ in cents (default: 5 for $0.05)",
)
@click.option(
    "--product-name",
    help="Custom product name (default: AI API Subscription (Environment))",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without making changes",
)
def setup_products(
    environment: str,
    model: str,
    base_price: int,
    currency: str,
    included_requests: int,
    tier_1_limit: int,
    tier_1_price: int,
    tier_2_limit: int,
    tier_2_price: int,
    tier_3_price: int,
    product_name: str | None,
    dry_run: bool,
) -> None:
    """
    Create or update Stripe products for an environment.

    This command sets up the necessary Stripe products and prices for your
    billing infrastructure. It supports multiple pricing models and handles
    existing products gracefully.

    IMPORTANT: This CLI is read-only for configuration. It will:
    - Read your Stripe API key from environment variables or .env files
    - Create products and prices in Stripe
    - Display the created resource IDs for you to manually configure
    - NEVER modify any .env files

    Configuration is read from (in order of precedence):
    1. Environment variables (e.g., export STAGING_STRIPE_SECRET_KEY=sk_test_...)
    2. ./.env file in current directory
    3. ~/.augint/.env user configuration file

    After running setup, manually add the displayed environment variables to your
    .env file or export them in your shell.

    Environment-specific prefixes:
    - Staging: STAGING_ (e.g., STAGING_API_USAGE_PRODUCT_ID)
    - Production: PROD_ (e.g., PROD_API_USAGE_PRODUCT_ID)

    Examples:
        # Setup staging with default subscription + metered model
        ai-billing products setup staging

        # Setup production with custom pricing
        ai-billing products setup production --base-price 3999 --tier-1-price 15

        # Dry run to see what would be created
        ai-billing products setup staging --dry-run

        # Metered-only model (no base subscription)
        ai-billing products setup staging --model metered-only

        # After setup, add the displayed variables to your .env:
        echo 'STAGING_API_USAGE_PRODUCT_ID="prod_xxx"' >> .env
        echo 'STAGING_METERED_USAGE_PRICE_ID="price_xxx"' >> .env
    """
    # Get Stripe key
    stripe_key = get_stripe_key(environment)
    stripe.api_key = stripe_key

    # Set API version to avoid meter requirement for metered prices
    stripe.api_version = "2024-06-20"

    # Determine mode
    mode = "TEST" if stripe_key.startswith("sk_test") else "LIVE"
    click.echo(f"\n🔑 Using Stripe {mode} mode for {environment} environment")

    # Verify the API key is valid before proceeding
    if not dry_run:
        try:
            # Make a simple API call to verify the key works
            stripe.Product.list(limit=1)
        except stripe.error.AuthenticationError:
            click.echo(
                click.style(
                    f"\n❌ Invalid Stripe API key: {stripe_key[:12]}...{stripe_key[-4:] if len(stripe_key) > 16 else ''}",
                    fg="red",
                )
            )
            click.echo(
                click.style(
                    "   Please check your Stripe key is valid and has the correct permissions.",
                    fg="red",
                )
            )
            click.echo("\n   Troubleshooting steps:")
            click.echo(
                "   1. Verify the key starts with 'sk_test_' for test mode or 'sk_live_' for live mode"
            )
            click.echo("   2. Check the key hasn't been revoked in your Stripe dashboard")
            click.echo("   3. Ensure you're using the correct environment (staging vs production)")
            click.echo(
                f"   4. The key was loaded from environment variable: {get_stripe_key_source(environment)}"
            )
            sys.exit(1)
        except Exception as e:
            click.echo(
                click.style(
                    f"\n❌ Failed to connect to Stripe API: {e}",
                    fg="red",
                )
            )
            sys.exit(1)

    if dry_run:
        click.echo(click.style("🔍 DRY RUN - No changes will be made\n", fg="yellow", bold=True))

    # Set product name
    if not product_name:
        product_name = f"AI API Subscription ({environment.title()})"

    try:
        # Check for existing product
        existing_product = find_existing_product(product_name, environment)

        if existing_product:
            click.echo(f"✅ Found existing product: {existing_product.id}")
            product = existing_product
        elif dry_run:
            click.echo(f"Would create product: {product_name}")
            product = type("obj", (object,), {"id": f"prod_{environment}_mock"})()
        else:
            product = stripe.Product.create(
                name=product_name,
                description=f"API usage billing for {environment} environment",
                metadata={
                    "created_by": "ai-billing-cli",
                    "environment": environment,
                    "model": model,
                },
            )
            click.echo(f"✅ Created product in Stripe: {product.id}")

            # Verify the product was actually created
            try:
                verification = stripe.Product.retrieve(product.id)
                if verification and verification.id == product.id:
                    click.echo(f"✅ Verified product exists: {product.id}")
                else:
                    click.echo(
                        click.style(
                            f"⚠️  Product {product.id} creation reported success but verification failed",
                            fg="yellow",
                        )
                    )
            except StripeError as e:
                click.echo(
                    click.style(
                        f"⚠️  Product {product.id} creation reported success but verification failed: {e}",
                        fg="yellow",
                    )
                )
                click.echo("\n   This may indicate:")
                click.echo("   1. Network connectivity issues")
                click.echo("   2. Stripe API rate limiting")
                click.echo("   3. Permission issues with your API key")
                click.echo(f"\n   To manually verify, run: stripe products retrieve {product.id}")

        # Create prices based on model
        subscription_price = None
        metered_price = None

        if model in ["subscription-plus-metered", "subscription-only"]:
            # Create or find subscription price
            if not dry_run and hasattr(product, "id"):
                existing_prices = stripe.Price.list(product=product.id, limit=100)
                for price in existing_prices.data:
                    if (
                        price.type == "recurring"
                        and price.recurring.get("usage_type") != "metered"
                        and price.unit_amount == base_price
                        and price.currency == currency
                    ):
                        subscription_price = price
                        click.echo(f"✅ Found existing subscription price: {price.id}")
                        break

            if not subscription_price:
                if dry_run:
                    click.echo(
                        f"Would create subscription price: ${base_price / 100:.2f}/{currency}/month"
                    )
                    subscription_price = type(
                        "obj", (object,), {"id": f"price_sub_{environment}_mock"}
                    )()
                else:
                    subscription_price = create_subscription_price(product.id, base_price, currency)
                    click.echo(f"✅ Created subscription price: {subscription_price.id}")

        if model in ["subscription-plus-metered", "metered-only"]:
            # Build tiers configuration
            tiers: list[dict[str, Any]] = []

            # For subscription-plus-metered, the tiers apply AFTER the included requests
            # For metered-only, tiers start from 0
            if model == "subscription-plus-metered":
                # Tier 1: Usage from (included+1) to tier_1_limit
                # In Stripe tiers, this is 0 to (tier_1_limit - included_requests)
                tier_1_up_to = tier_1_limit - included_requests
                if tier_1_up_to <= 0:
                    click.echo(
                        click.style(
                            f"❌ Error: Tier 1 limit ({tier_1_limit}) must be greater than included requests ({included_requests})",
                            fg="red",
                        )
                    )
                    sys.exit(1)
                tiers.append(
                    {
                        "up_to": tier_1_up_to,
                        "unit_amount": tier_1_price,
                    }
                )
                # Tier 2: Usage from (tier_1_limit+1) to tier_2_limit
                # In Stripe graduated tiers, each tier's up_to is cumulative from 0
                # So tier 2 goes from (tier_1_limit - included) to (tier_2_limit - included)
                tier_2_up_to = tier_2_limit - included_requests
                if tier_2_up_to <= tier_1_up_to:
                    click.echo(
                        click.style(
                            f"❌ Error: Tier 2 limit ({tier_2_limit}) must be greater than tier 1 limit ({tier_1_limit})",
                            fg="red",
                        )
                    )
                    sys.exit(1)
                tiers.append(
                    {
                        "up_to": tier_2_up_to,
                        "unit_amount": tier_2_price,
                    }
                )
            else:
                # Tier 1: From 0 to tier_1_limit
                tiers.append(
                    {
                        "up_to": tier_1_limit,
                        "unit_amount": tier_1_price,
                    }
                )
                # Tier 2: From tier_1_limit+1 to tier_2_limit
                tiers.append(
                    {
                        "up_to": tier_2_limit,
                        "unit_amount": tier_2_price,
                    }
                )

            # Tier 3: Above tier_2_limit (infinite)
            tiers.append(
                {
                    "up_to": "inf",
                    "unit_amount": tier_3_price,
                }
            )

            # Create or find metered price
            if not dry_run and hasattr(product, "id"):
                existing_prices = stripe.Price.list(product=product.id, limit=100)
                for price in existing_prices.data:
                    if (
                        price.type == "recurring"
                        and price.recurring.get("usage_type") == "metered"
                        and price.billing_scheme == "tiered"
                    ):
                        # Check if tiers match
                        if len(price.tiers) == len(tiers):
                            metered_price = price
                            click.echo(f"✅ Found existing metered price: {price.id}")
                            break

            if not metered_price:
                if dry_run:
                    click.echo("Would create metered price with tiered pricing")
                    metered_price = type(
                        "obj", (object,), {"id": f"price_metered_{environment}_mock"}
                    )()
                else:
                    metered_price = create_metered_price_with_tiers(product.id, currency, tiers)
                    click.echo(f"✅ Created metered price: {metered_price.id}")

        # Update .env file if requested
        env_vars_to_add = {}

        # Determine environment variable prefix
        prefix = "PROD_" if environment == "production" else "STAGING_"

        # Add product ID
        env_vars_to_add[f"{prefix}API_USAGE_PRODUCT_ID"] = (
            product.id if hasattr(product, "id") else f"prod_{environment}_mock"
        )

        # Add price IDs based on model
        if subscription_price:
            env_vars_to_add[f"{prefix}BASE_SUBSCRIPTION_PRICE_ID"] = (
                subscription_price.id
                if hasattr(subscription_price, "id")
                else f"price_sub_{environment}_mock"
            )

        if metered_price:
            env_vars_to_add[f"{prefix}METERED_USAGE_PRICE_ID"] = (
                metered_price.id
                if hasattr(metered_price, "id")
                else f"price_metered_{environment}_mock"
            )

        # Display summary
        click.echo("\n" + "=" * 60)
        click.echo(
            click.style(
                f"✅ Product setup complete for {environment} environment", fg="green", bold=True
            )
        )
        click.echo("=" * 60)

        # Always show the created IDs for users to manually configure if needed
        if not dry_run:
            click.echo("\n📝 Next Steps:")
            click.echo("Add these environment variables to your .env file:\n")
            for key, value in env_vars_to_add.items():
                click.echo(f'{key}="{value}"')
            click.echo("\nThen sync to GitHub Actions with: ai-gh-push")
            click.echo(
                "\nNote: This CLI never modifies .env files. Configuration is always read-only."
            )

        click.echo(f"\nPricing Structure ({model}):")

        if model == "subscription-plus-metered":
            click.echo(f"- Base: ${base_price / 100:.2f}/month")
            click.echo(f"- Included: {included_requests:,} requests")
            click.echo(
                f"- {included_requests + 1:,}-{tier_1_limit:,}: ${tier_1_price / 100:.2f}/request"
            )
            click.echo(
                f"- {tier_1_limit + 1:,}-{tier_2_limit:,}: ${tier_2_price / 100:.2f}/request"
            )
            click.echo(f"- {tier_2_limit + 1:,}+: ${tier_3_price / 100:.2f}/request")

            # Calculate example bills
            example_requests = [500, 5000, 50000, 150000]
            bills = calculate_example_bills(
                base_price,
                included_requests,
                tiers,
                example_requests,
            )

            click.echo("\nExample monthly bills:")
            for requests, bill in bills.items():
                click.echo(f"- {requests:,} requests: ${bill:,.2f}")

        elif model == "metered-only":
            click.echo(f"- 0-{tier_1_limit:,}: ${tier_1_price / 100:.2f}/request")
            click.echo(
                f"- {tier_1_limit + 1:,}-{tier_2_limit:,}: ${tier_2_price / 100:.2f}/request"
            )
            click.echo(f"- {tier_2_limit + 1:,}+: ${tier_3_price / 100:.2f}/request")

            # Calculate example bills
            example_requests = [1000, 10000, 50000, 150000]
            bills = {}
            for requests in example_requests:
                total = 0
                remaining = requests

                # Tier 1
                tier_1_units = min(remaining, tier_1_limit)
                total += tier_1_units * tier_1_price
                remaining -= tier_1_units

                # Tier 2
                if remaining > 0:
                    tier_2_units = min(remaining, tier_2_limit - tier_1_limit)
                    total += tier_2_units * tier_2_price
                    remaining -= tier_2_units

                # Tier 3
                if remaining > 0:
                    total += remaining * tier_3_price

                bills[requests] = total / 100.0

            click.echo("\nExample monthly bills:")
            for requests, bill in bills.items():
                click.echo(f"- {requests:,} requests: ${bill:,.2f}")

        elif model == "subscription-only":
            click.echo(f"- Fixed price: ${base_price / 100:.2f}/month")
            click.echo("- No usage tracking")

    except StripeError as e:
        click.echo(click.style(f"❌ Stripe error: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


__all__ = ["setup_products"]
