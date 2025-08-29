"""Link existing API key to Stripe customer."""

import json
from typing import Any

import click

from augint_billing_lib.config import get_service
from augint_billing_lib.models import Link


def preflight_check(service: Any, api_key_id: str) -> dict[str, Any]:
    """Verify API key exists before testing."""
    results = {
        "api_key_exists": False,
        "api_key_enabled": False,
        "current_plan": None,
        "customer_exists": False,
        "customer_has_payment": False,
        "existing_link": False,
    }

    try:
        # Check API Gateway
        import boto3

        apigw = boto3.client("apigateway", region_name=service.config.region)

        # Get API key
        key_response = apigw.get_api_key(apiKey=api_key_id, includeValue=False)
        results["api_key_exists"] = True
        results["api_key_enabled"] = key_response.get("enabled", False)

        # Check usage plan - simplified since we can't get plans for a specific key
        # In a real implementation, would need to iterate through plans and check keys
        results["current_plan"] = "unknown"  # type: ignore[assignment]

    except Exception:
        pass

    # Check for existing link
    try:
        link = service.customer_repo.get_link(api_key_id)
        if link:
            results["existing_link"] = True
    except:
        pass

    return results


@click.command("link")
@click.option(
    "--api-key",
    "api_key_id",
    required=True,
    help="Existing API key from your application",
)
@click.option(
    "--customer",
    "stripe_customer_id",
    required=True,
    help="Stripe customer ID",
)
@click.option(
    "--validate-key",
    is_flag=True,
    default=True,
    help="Validate API key exists",
)
@click.option(
    "--validate-customer",
    is_flag=True,
    default=True,
    help="Validate Stripe customer exists",
)
@click.option(
    "--check-existing",
    is_flag=True,
    default=True,
    help="Check for existing links",
)
@click.option(
    "--json-output",
    "use_json",
    is_flag=True,
    help="Output as JSON",
)
def link(
    api_key_id: str,
    stripe_customer_id: str,
    validate_key: bool,
    validate_customer: bool,
    check_existing: bool,
    use_json: bool,
) -> None:
    """
    Link an EXISTING API key to a Stripe customer.

    This command links a real API key from your application to a
    Stripe customer for integration testing.

    REQUIREMENTS:
    • API key must exist in API Gateway
    • Stripe customer must exist
    • No existing link should be present (unless overriding)

    Examples:

        # Link with full validation
        ai-billing test integration link \\
            --api-key ${REAL_API_KEY} \\
            --customer cus_xxx

        # Skip validation for faster execution
        ai-billing test integration link \\
            --api-key ${REAL_API_KEY} \\
            --customer cus_xxx \\
            --no-validate-key \\
            --no-validate-customer
    """
    service = get_service()

    # Pre-flight checks
    if validate_key:
        click.echo(f"Validating API key: {api_key_id}...")
        validation = preflight_check(service, api_key_id)

        if not validation["api_key_exists"]:
            click.echo(
                click.style(f"❌ API key not found: {api_key_id}", fg="red"),
                err=True,
            )
            click.echo("", err=True)
            click.echo("Integration tests require a real API key.", err=True)
            click.echo("Options:", err=True)
            click.echo("1. Use an existing key from your application", err=True)
            click.echo("2. Create a user through your normal signup flow", err=True)
            click.echo("3. Use 'test stripe' commands for Stripe-only testing", err=True)
            raise click.Abort()

        if not validation["api_key_enabled"]:
            click.echo(click.style("⚠️  API key exists but is disabled", fg="yellow"))
    else:
        validation = {"api_key_exists": True}

    # Validate Stripe customer
    if validate_customer:
        click.echo(f"Validating Stripe customer: {stripe_customer_id}...")
        try:
            import stripe

            stripe.api_key = service.config.stripe_secret_key
            stripe.Customer.retrieve(stripe_customer_id)
            validation["customer_exists"] = True

            # Check for payment method
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer_id,
                type="card",
            )
            validation["customer_has_payment"] = len(payment_methods.data) > 0

        except Exception as e:
            click.echo(
                click.style(f"❌ Stripe customer not found: {e}", fg="red"),
                err=True,
            )
            raise click.Abort()

    # Check existing link
    if check_existing:
        existing_link = service.customer_repo.get_link(api_key_id)
        if existing_link:
            validation["existing_link"] = True
            click.echo(
                click.style(
                    f"⚠️  API key already linked to {existing_link.stripe_customer_id}",
                    fg="yellow",
                )
            )
            if existing_link.stripe_customer_id != stripe_customer_id:
                if not click.confirm("Replace existing link?"):
                    raise click.Abort()

    # Create link
    try:
        link = Link(
            api_key_id=api_key_id,
            stripe_customer_id=stripe_customer_id,
            plan="free",  # Start with free plan
            usage_plan_id=service.config.free_usage_plan_id,
        )

        service.customer_repo.save_link(link)

        # Prepare output
        ready_for = []
        if validation.get("customer_has_payment"):
            ready_for.extend(["promotion", "billing_cycle"])
        ready_for.append("traffic")

        result = {
            "validations": validation,
            "link_created": True,
            "ready_for": ready_for,
        }

        if use_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(
                click.style(
                    f"✅ Linked {api_key_id} to {stripe_customer_id}",
                    fg="green",
                )
            )
            click.echo(f"Current plan: {validation.get('current_plan', 'unknown')}")

            if validation.get("customer_has_payment"):
                click.echo("✅ Customer has payment method - ready for promotion")
            else:
                click.echo("⚠️  Customer needs payment method for promotion")

            click.echo("\nReady for:")
            for item in ready_for:
                click.echo(f"  • {item}")

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to create link: {e}", fg="red"),
            err=True,
        )
        raise


__all__ = ["link"]
