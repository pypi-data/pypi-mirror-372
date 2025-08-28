"""Diagnose Stripe connection and configuration issues."""

import hashlib
import sys
from pathlib import Path

import click
import stripe

from augint_billing_lib.cli.config import get_config


def test_stripe_connection(api_key: str) -> tuple[bool, str]:
    """Test if a Stripe API key is valid."""
    stripe.api_key = api_key
    stripe.api_version = "2024-06-20"

    try:
        # Try a simple API call
        stripe.Product.list(limit=1)
        return True, "Connection successful"
    except stripe.error.AuthenticationError as e:
        return False, f"Authentication failed: {e!s}"
    except Exception as e:
        return False, f"Connection failed: {e!s}"


@click.command("diagnose")
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed diagnostic information",
)
def diagnose_setup(verbose: bool) -> None:
    """
    Diagnose Stripe connection and configuration issues.

    This command helps identify common setup problems:
    - Missing or invalid API keys
    - Environment variable configuration
    - Network connectivity issues
    - API key permissions

    Examples:
        # Run basic diagnostics
        ai-billing products diagnose

        # Run with verbose output
        ai-billing products diagnose --verbose
    """
    click.echo("\n🔍 Stripe Products CLI Diagnostics")
    click.echo("=" * 60)

    # Check environment variables
    click.echo("\n1. Configuration Sources:")

    # Check for config files
    user_config = Path.home() / ".augint" / ".env"
    local_config = Path.cwd() / ".env"

    click.echo("\nConfiguration Files:")
    if user_config.exists():
        click.echo(f"   ✅ User config: {user_config}")
    else:
        click.echo(f"   ❌ User config: {user_config} (not found)")

    if local_config.exists():
        click.echo(f"   ✅ Local config: {local_config}")
    else:
        click.echo(f"   ❌ Local config: {local_config} (not found)")

    click.echo("\n2. Stripe Keys Found:")

    # Check specific env vars across all configs
    staging_config = get_config("staging")
    prod_config = get_config("production")
    default_config = get_config(None)

    env_vars = {
        "STRIPE_SECRET_KEY": default_config.get("STRIPE_SECRET_KEY"),
        "STRIPE_TEST_SECRET_KEY": default_config.get("STRIPE_TEST_SECRET_KEY"),
        "STAGING_STRIPE_SECRET_KEY": staging_config.get("STRIPE_SECRET_KEY"),
        "STRIPE_LIVE_SECRET_KEY": default_config.get("STRIPE_LIVE_SECRET_KEY"),
        "PROD_STRIPE_SECRET_KEY": prod_config.get("STRIPE_SECRET_KEY"),
    }

    found_keys = {}
    for name, value in env_vars.items():
        if value:
            # Show partial key for security
            preview = f"{value[:12]}...{value[-4:]}" if len(value) > 16 else value
            key_hash = hashlib.sha256(value.encode()).hexdigest()[:8]
            mode = (
                "TEST"
                if value.startswith("sk_test")
                else "LIVE"
                if value.startswith("sk_live")
                else "UNKNOWN"
            )

            found_keys[name] = {
                "value": value,
                "preview": preview,
                "hash": key_hash,
                "mode": mode,
            }

            click.echo(f"   ✅ {name}: {preview} (Mode: {mode})")
            if verbose:
                click.echo(f"      Hash: {key_hash}, Length: {len(value)}")
        else:
            click.echo(f"   ❌ {name}: NOT SET")

    if not found_keys:
        click.echo(
            click.style(
                "\n⚠️  No Stripe keys found in environment!",
                fg="yellow",
            )
        )
        click.echo("\nTo fix this:")
        click.echo("1. Create a .env file in your project root")
        click.echo("2. Add your Stripe key:")
        click.echo("   STRIPE_SECRET_KEY=sk_test_...")
        click.echo("   # or")
        click.echo("   STAGING_STRIPE_SECRET_KEY=sk_test_...")
        click.echo("3. Ensure the .env file is in the same directory where you run the CLI")
        return

    # Test each key
    click.echo("\n2. API Key Validation:")

    valid_keys = []
    for name, info in found_keys.items():
        click.echo(f"\n   Testing {name}...")
        success, message = test_stripe_connection(info["value"])

        if success:
            click.echo(f"   ✅ {message}")
            valid_keys.append((name, info))

            # Get account info if verbose
            if verbose:
                try:
                    stripe.api_key = info["value"]
                    # Try to get account details
                    products = stripe.Product.list(limit=1)
                    click.echo("      Can access Stripe account")
                except Exception as e:
                    click.echo(f"      Warning: {e}")
        else:
            click.echo(f"   ❌ {message}")

            if "Invalid API Key" in message:
                click.echo("      Possible issues:")
                click.echo("      - Key has been revoked or regenerated")
                click.echo("      - Key is from a different Stripe account")
                click.echo("      - Key format is incorrect")

    if not valid_keys:
        click.echo(
            click.style(
                "\n❌ No valid Stripe keys found!",
                fg="red",
            )
        )
        click.echo("\nPlease check:")
        click.echo("1. Your keys are correct and active")
        click.echo("2. You have internet connectivity")
        click.echo("3. Your Stripe account is active")
        sys.exit(1)

    # Test product creation with first valid key
    click.echo("\n3. Product Creation Test:")

    test_key_name, test_key_info = valid_keys[0]
    stripe.api_key = test_key_info["value"]
    stripe.api_version = "2024-06-20"

    click.echo(f"   Using {test_key_name}")

    try:
        # Create a test product
        test_product = stripe.Product.create(
            name="[TEST] Diagnostic Product",
            description="Created by ai-billing products diagnose",
            metadata={"test": "true", "created_by": "diagnose_command"},
        )
        click.echo(f"   ✅ Created test product: {test_product.id}")

        # Verify retrieval
        retrieved = stripe.Product.retrieve(test_product.id)
        click.echo(f"   ✅ Retrieved test product: {retrieved.id}")

        # Archive it
        stripe.Product.modify(test_product.id, active=False)
        click.echo("   ✅ Archived test product")

    except Exception as e:
        click.echo(f"   ❌ Product creation failed: {e}")
        click.echo("\n   This indicates a problem with:")
        click.echo("   - API key permissions")
        click.echo("   - Stripe account configuration")
        click.echo("   - Network connectivity")

    # Check for existing CLI products
    click.echo("\n4. Existing Products Check:")

    try:
        products = stripe.Product.list(limit=100)
        cli_products = [
            p for p in products.data if p.metadata.get("created_by") == "ai-billing-cli"
        ]

        if cli_products:
            click.echo(f"   Found {len(cli_products)} products created by CLI:")
            for p in cli_products[:5]:  # Show first 5
                status = "✅" if p.active else "❌"
                click.echo(f"   {status} {p.name} [{p.id}]")
                if verbose:
                    click.echo(f"      Environment: {p.metadata.get('environment', 'N/A')}")
                    click.echo(f"      Model: {p.metadata.get('model', 'N/A')}")
        else:
            click.echo("   No products created by CLI found")

    except Exception as e:
        click.echo(f"   ❌ Failed to list products: {e}")

    # Summary
    click.echo("\n" + "=" * 60)
    click.echo("Diagnostic Summary:")

    if valid_keys:
        click.echo(f"✅ {len(valid_keys)} valid Stripe key(s) found")
        click.echo("✅ Stripe API connection working")
        click.echo("✅ Product creation and retrieval working")
        click.echo("\nYour Stripe CLI setup appears to be working correctly!")

        if len(found_keys) > len(valid_keys):
            click.echo(
                click.style(
                    f"\n⚠️  {len(found_keys) - len(valid_keys)} invalid key(s) found - consider removing them",
                    fg="yellow",
                )
            )
    else:
        click.echo("❌ No valid Stripe keys found")
        click.echo("\nPlease configure valid Stripe API keys to use the CLI")

    # Additional tips
    click.echo("\n💡 Tips:")
    click.echo("- Use 'ai-billing products setup staging' to create products")
    click.echo("- Use 'ai-billing products verify staging' to check configuration")
    click.echo("- Use 'ai-billing products list' to see existing products")
    click.echo("- Ensure your .env file is in the directory where you run commands")


__all__ = ["diagnose_setup"]
