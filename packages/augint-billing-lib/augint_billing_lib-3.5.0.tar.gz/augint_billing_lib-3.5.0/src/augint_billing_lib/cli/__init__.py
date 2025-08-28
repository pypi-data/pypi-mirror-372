"""Augint Billing CLI - Zero-Touch Architecture Edition."""

import click

from augint_billing_lib.cli.admin import admin_group
from augint_billing_lib.cli.aws import aws_group
from augint_billing_lib.cli.billing import billing_group
from augint_billing_lib.cli.infra import infra_group
from augint_billing_lib.cli.monitor import monitor_group
from augint_billing_lib.cli.products import products_group
from augint_billing_lib.cli.report import report_group
from augint_billing_lib.cli.setup import setup_group
from augint_billing_lib.cli.test import test_group
from augint_billing_lib.cli.troubleshoot import troubleshoot_group
from augint_billing_lib.cli.validate import validate_group


@click.group(
    name="ai-billing",
    help="""Augint Billing CLI - Zero-Touch Architecture Edition.

This CLI provides tools for managing the billing system with automatic
API discovery and zero-touch operations.

\b
CONFIGURATION SOURCES (in order of precedence):
  1. Environment variables (export STACK_NAME=mystack)
  2. ./.env file in current directory
  3. ~/.augint/.env user configuration file
  4. Default values

\b
REQUIRED CONFIGURATION:
  STACK_NAME         CloudFormation stack name
  AWS_REGION         AWS region (default: us-east-1)
  STRIPE_SECRET_KEY  Stripe API key (sk_test_... or sk_live_...)

\b
OPTIONAL CONFIGURATION:
  TABLE_NAME              DynamoDB table (auto-discovered from stack)
  FREE_USAGE_PLAN_ID      Free tier plan (default: FREE_10K)
  METERED_USAGE_PLAN_ID   Paid tier plan (default: METERED)
  API_USAGE_PRODUCT_ID    Stripe product ID (auto-discovered)
  STRIPE_PRICE_ID_METERED Stripe price ID (auto-discovered)

\b
ENVIRONMENT PREFIXES:
  STAGING_  For staging environment
  PROD_     For production environment

\b
COMMAND GROUPS:
  infra        Infrastructure management (status, discovery, APIs)
  monitor      Real-time monitoring (discovery, events, usage)
  aws          AWS operations (Lambda, EventBridge, CloudWatch)
  billing      Billing operations (process events, sync usage)
  products     Stripe product and price management
  test         Testing commands (separated by capability)
  validate     Validation and verification
  troubleshoot Diagnostic and debugging
  report       Reporting and analytics
  admin        Administrative operations
  setup        Initial setup and configuration

Use 'ai-billing COMMAND --help' for more information on a command.""",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Main CLI entry point."""
    # Store common settings in context
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(infra_group)
cli.add_command(monitor_group)
cli.add_command(aws_group)
cli.add_command(billing_group)
cli.add_command(products_group)
cli.add_command(test_group)
cli.add_command(validate_group)
cli.add_command(troubleshoot_group)
cli.add_command(report_group)
cli.add_command(admin_group)
cli.add_command(setup_group)


# Provide legacy command mappings with deprecation warnings
@cli.command(
    "env-dump",
    hidden=True,  # Hide from help but still available
    help="[DEPRECATED] Use 'billing env show' instead",
)
@click.pass_context
def env_dump_legacy(ctx: click.Context) -> None:
    """Legacy env-dump command - redirects to billing env show."""
    from augint_billing_lib.cli.billing.env import show

    click.echo(
        click.style(
            "⚠️  'env-dump' is deprecated. Use 'ai-billing billing env show' instead.",
            fg="yellow",
        ),
        err=True,
    )
    ctx.invoke(show)


if __name__ == "__main__":
    cli()
