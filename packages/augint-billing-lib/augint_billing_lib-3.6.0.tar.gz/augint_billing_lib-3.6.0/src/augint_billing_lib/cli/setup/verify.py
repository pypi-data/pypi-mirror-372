"""Comprehensive setup verification."""

import json
import sys
from typing import Any

import boto3
import click
import stripe

from augint_billing_lib.config import config


@click.command("verify")
@click.option(
    "--environment",
    type=click.Choice(["staging", "production"]),
    help="Environment to verify",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to fix issues automatically",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format",
)
def verify(
    environment: str,
    fix: bool,
    output: str,
) -> None:
    """
    Comprehensive setup verification.

    This command verifies that all components of the billing system
    are properly configured and ready for use.

    Example:
        ai-billing setup verify --output markdown
    """
    click.echo(
        click.style(
            f"🔍 Verifying Billing System Setup - {environment or 'CURRENT'}",
            fg="cyan",
            bold=True,
        )
    )

    results = {
        "stripe": verify_stripe(),
        "eventbridge": verify_eventbridge(),
        "aws_resources": verify_aws_resources(),
        "configuration": verify_configuration(),
    }

    # Calculate overall status
    all_checks = []
    for _category, checks in results.items():
        for _check_name, check_result in checks.items():
            all_checks.append(check_result)

    passed = sum(1 for c in all_checks if c["status"] == "pass")
    warnings = sum(1 for c in all_checks if c["status"] == "warning")
    failed = sum(1 for c in all_checks if c["status"] == "fail")

    # Output results
    if output == "json":
        print(
            json.dumps(
                {
                    "results": results,
                    "summary": {
                        "passed": passed,
                        "warnings": warnings,
                        "failed": failed,
                        "total": len(all_checks),
                    },
                },
                indent=2,
            )
        )
    elif output == "markdown":
        output_markdown(results, passed, warnings, failed, len(all_checks))
    else:  # text
        output_text(results, passed, warnings, failed, len(all_checks), fix)

    # Exit with error if critical checks failed
    if failed > 0 and not fix:
        sys.exit(1)


def verify_stripe() -> dict[str, Any]:
    """Verify Stripe configuration."""
    results = {}

    try:
        stripe.api_key = config.stripe_secret_key

        # Check API key
        try:
            account = stripe.Account.retrieve()
            results["api_key"] = {
                "status": "pass",
                "message": f"Valid ({'test' if stripe.api_key.startswith('sk_test') else 'live'} mode)",
                "details": {"account_id": account.id},
            }
        except Exception as e:
            results["api_key"] = {
                "status": "fail",
                "message": f"Invalid API key: {e!s}",
                "fix": "Check STRIPE_SECRET_KEY environment variable",
            }
            return results  # Can't continue without valid key

        # Check products
        products = stripe.Product.list(limit=100)
        metered_products = [
            p for p in products.data if p.metadata.get("created_by") == "ai-billing-cli"
        ]

        if metered_products:
            results["products"] = {
                "status": "pass",
                "message": f"Found {len(metered_products)} configured product(s)",
                "details": {"product_ids": [p.id for p in metered_products]},
            }
        else:
            results["products"] = {
                "status": "warning",
                "message": "No products created by CLI found",
                "fix": "Run: ai-billing setup stripe-product",
            }

        # Check prices
        if metered_products:
            prices = stripe.Price.list(product=metered_products[0].id, limit=100)
            metered_prices = [
                p for p in prices.data if p.recurring and p.recurring.get("usage_type") == "metered"
            ]

            if metered_prices:
                results["prices"] = {
                    "status": "pass",
                    "message": f"Found {len(metered_prices)} metered price(s)",
                    "details": {"price_ids": [p.id for p in metered_prices]},
                }
            else:
                results["prices"] = {
                    "status": "warning",
                    "message": "No metered prices found",
                    "fix": "Run: ai-billing setup stripe-product",
                }

        # Check for meters (new API)
        try:
            # Use getattr to avoid mypy error
            billing = getattr(stripe, "billing", None)
            if billing and hasattr(billing, "Meter"):
                Meter = getattr(billing, "Meter", None)
                meters = Meter.list(limit=10) if Meter else None
            else:
                meters = None

            if meters and meters.data:
                results["meters"] = {
                    "status": "pass",
                    "message": f"Found {len(meters.data)} meter(s) (modern API)",
                    "details": {"meter_ids": [m.id for m in meters.data]},
                }
            else:
                results["meters"] = {
                    "status": "warning",
                    "message": "No meters found",
                }
        except (AttributeError, stripe.error.InvalidRequestError):
            results["meters"] = {
                "status": "fail",
                "message": "Meter API not available - please upgrade Stripe API version",
                "fix": "Upgrade to Stripe API version 2025-03-31 or later",
            }

    except Exception as e:
        results["connection"] = {
            "status": "fail",
            "message": f"Cannot connect to Stripe: {e!s}",
            "fix": "Check network and API key configuration",
        }

    return results


def verify_eventbridge() -> dict[str, Any]:
    """Verify EventBridge configuration."""
    results = {}

    try:
        events = boto3.client("events", region_name=config.region)

        # Check for partner event sources
        sources = events.list_event_sources(NamePrefix="aws.partner/stripe.com")

        if sources.get("EventSources"):
            active_sources = [s for s in sources["EventSources"] if s["State"] == "ACTIVE"]

            if active_sources:
                results["partner_source"] = {
                    "status": "pass",
                    "message": f"Found {len(active_sources)} active Stripe source(s)",
                    "details": {"sources": [s["Name"] for s in active_sources]},
                }
            else:
                results["partner_source"] = {
                    "status": "warning",
                    "message": f"Found {len(sources['EventSources'])} inactive source(s)",
                    "fix": "Run: ai-billing setup activate-eventbus",
                }
        else:
            results["partner_source"] = {
                "status": "fail",
                "message": "No Stripe partner event sources found",
                "fix": "Configure EventBridge in Stripe Dashboard",
            }

        # Check for event buses
        buses = events.list_event_buses(Limit=100)
        stripe_buses = [
            b
            for b in buses.get("EventBuses", [])
            if "stripe" in b["Name"].lower()
            or b.get("EventSourceName", "").startswith("aws.partner/stripe")
        ]

        if stripe_buses:
            results["event_bus"] = {
                "status": "pass",
                "message": f"Found {len(stripe_buses)} Stripe event bus(es)",
                "details": {"buses": [b["Name"] for b in stripe_buses]},
            }
        else:
            results["event_bus"] = {
                "status": "warning",
                "message": "No Stripe event buses found",
                "fix": "Run: ai-billing setup activate-eventbus",
            }

        # Check for rules
        all_rules = []
        for bus in stripe_buses:
            rules = events.list_rules(EventBusName=bus["Name"], Limit=100)
            all_rules.extend(rules.get("Rules", []))

        if all_rules:
            enabled_rules = [r for r in all_rules if r["State"] == "ENABLED"]
            results["rules"] = {
                "status": "pass" if enabled_rules else "warning",
                "message": f"Found {len(enabled_rules)}/{len(all_rules)} enabled rule(s)",
                "details": {"rules": [r["Name"] for r in enabled_rules]},
            }
        else:
            results["rules"] = {
                "status": "warning",
                "message": "No EventBridge rules found",
                "fix": "Create rules to route events to Lambda",
            }

    except Exception as e:
        results["connection"] = {
            "status": "fail",
            "message": f"Cannot connect to EventBridge: {e!s}",
            "fix": "Check AWS credentials and region",
        }

    return results


def verify_aws_resources() -> dict[str, Any]:
    """Verify AWS resources."""
    results = {}

    # Check Lambda functions
    try:
        lambda_client = boto3.client("lambda", region_name=config.region)
        functions = lambda_client.list_functions(MaxItems=100)

        billing_functions = [
            f for f in functions.get("Functions", []) if config.stack_name in f["FunctionName"]
        ]

        if billing_functions:
            results["lambda"] = {
                "status": "pass",
                "message": f"Found {len(billing_functions)} Lambda function(s)",
                "details": {"functions": [f["FunctionName"] for f in billing_functions]},
            }
        else:
            results["lambda"] = {
                "status": "fail",
                "message": "No Lambda functions found",
                "fix": "Deploy infrastructure with CDK/CloudFormation",
            }
    except Exception as e:
        results["lambda"] = {
            "status": "fail",
            "message": f"Cannot check Lambda: {e!s}",
        }

    # Check DynamoDB
    try:
        dynamodb = boto3.client("dynamodb", region_name=config.region)
        table = dynamodb.describe_table(TableName=config.table_name)

        results["dynamodb"] = {
            "status": "pass",
            "message": f"Table '{config.table_name}' exists",
            "details": {
                "item_count": table["Table"]["ItemCount"],
                "status": table["Table"]["TableStatus"],
            },
        }
    except Exception as e:
        results["dynamodb"] = {
            "status": "fail",
            "message": f"Table not found: {e!s}",
            "fix": "Deploy infrastructure with CDK/CloudFormation",
        }

    # Check API Gateway
    try:
        apigw = boto3.client("apigateway", region_name=config.region)

        # Check usage plans
        plan_checks = {}
        for plan_name, plan_id in [
            ("free", config.free_usage_plan_id),
            ("metered", config.metered_usage_plan_id),
        ]:
            try:
                apigw.get_usage_plan(usagePlanId=plan_id)
                plan_checks[plan_name] = True
            except Exception:
                plan_checks[plan_name] = False

        if all(plan_checks.values()):
            results["api_gateway"] = {
                "status": "pass",
                "message": "All usage plans configured",
                "details": plan_checks,
            }
        elif any(plan_checks.values()):
            results["api_gateway"] = {
                "status": "warning",
                "message": "Some usage plans missing",
                "details": plan_checks,
            }
        else:
            results["api_gateway"] = {
                "status": "fail",
                "message": "No usage plans found",
                "fix": "Configure API Gateway usage plans",
            }
    except Exception as e:
        results["api_gateway"] = {
            "status": "fail",
            "message": f"Cannot check API Gateway: {e!s}",
        }

    return results


def verify_configuration() -> dict[str, Any]:
    """Verify environment configuration."""
    results = {}

    # Check required environment variables
    required_vars = {
        "STACK_NAME": config.stack_name,
        "AWS_REGION": config.region,
        "STRIPE_SECRET_KEY": bool(config.stripe_secret_key),
    }

    missing = [k for k, v in required_vars.items() if not v]

    if not missing:
        results["environment"] = {
            "status": "pass",
            "message": "All required variables set",
        }
    else:
        results["environment"] = {
            "status": "fail",
            "message": f"Missing variables: {', '.join(missing)}",
            "fix": "Set missing environment variables",
        }

    # Check optional but recommended variables
    optional_vars = {
        "METERED_PRICE_ID": hasattr(config, "metered_price_id"),
        "METERED_PRODUCT_ID": hasattr(config, "metered_product_id"),
    }

    missing_optional = [k for k, v in optional_vars.items() if not v]

    if not missing_optional:
        results["optional_config"] = {
            "status": "pass",
            "message": "All optional variables set",
        }
    else:
        results["optional_config"] = {
            "status": "warning",
            "message": f"Missing optional: {', '.join(missing_optional)}",
            "fix": "Run: ai-billing setup stripe-product --update-env",
        }

    return results


def output_text(
    results: dict[str, Any],
    passed: int,
    warnings: int,
    failed: int,
    total: int,
    fix: bool,
) -> None:
    """Output results as text."""
    for category, checks in results.items():
        click.echo(f"\n{category.upper().replace('_', ' ')}:")
        for check_name, result in checks.items():
            status = result["status"]
            message = result["message"]

            if status == "pass":
                click.echo(f"  ✅ {check_name}: {message}")
            elif status == "warning":
                click.echo(click.style(f"  ⚠️  {check_name}: {message}", fg="yellow"))
                if "fix" in result:
                    click.echo(click.style(f"     Fix: {result['fix']}", fg="yellow"))
            else:  # fail
                click.echo(click.style(f"  ❌ {check_name}: {message}", fg="red"))
                if "fix" in result:
                    click.echo(click.style(f"     Fix: {result['fix']}", fg="red"))

    # Summary
    click.echo("\n" + "=" * 50)
    click.echo(
        f"VERIFICATION SUMMARY: {passed}/{total} passed, {warnings} warnings, {failed} failed"
    )

    if failed == 0 and warnings == 0:
        click.echo(click.style("✅ System is fully configured and ready!", fg="green", bold=True))
    elif failed == 0:
        click.echo(click.style("⚠️  System is operational with warnings", fg="yellow", bold=True))
    else:
        click.echo(click.style("❌ System is not ready - fix critical issues", fg="red", bold=True))

    if fix and failed > 0:
        click.echo("\n🔧 Attempting to fix issues...")
        # Would implement auto-fix logic here
        click.echo("Auto-fix not yet implemented")


def output_markdown(
    results: dict[str, Any], passed: int, warnings: int, failed: int, total: int
) -> None:
    """Output results as markdown."""
    print("# Billing System Verification Report\n")
    print(f"**Summary:** {passed}/{total} checks passed, {warnings} warnings, {failed} failures\n")

    for category, checks in results.items():
        print(f"## {category.replace('_', ' ').title()}\n")
        for check_name, result in checks.items():
            status = result["status"]
            message = result["message"]

            icon = "✅" if status == "pass" else "⚠️" if status == "warning" else "❌"
            print(f"- {icon} **{check_name}**: {message}")

            if "fix" in result:
                print(f"  - _Fix:_ {result['fix']}")

            if "details" in result:
                print(f"  - _Details:_ `{json.dumps(result['details'])}`")
        print()

    # Recommendations
    print("## Recommendations\n")
    if failed > 0:
        print("1. Fix critical issues before proceeding")
        print("2. Re-run verification after fixes")
    elif warnings > 0:
        print("1. Address warnings for optimal operation")
        print("2. Consider running suggested fix commands")
    else:
        print("✅ System is ready for production use!")


__all__ = ["verify"]
