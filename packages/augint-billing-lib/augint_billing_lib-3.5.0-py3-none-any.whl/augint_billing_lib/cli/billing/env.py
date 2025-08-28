"""Environment configuration management commands."""

import json
import os

import click

from augint_billing_lib.config import config


@click.group(
    name="env",
    help="Environment configuration management",
)
def env_group() -> None:
    """Environment command group."""


@env_group.command("show")
@click.option(
    "--format",
    type=click.Choice(["text", "json", "shell"]),
    default="text",
    help="Output format",
)
def show(format: str) -> None:
    """Display current environment configuration."""
    env_vars = {
        "STACK_NAME": config.stack_name,
        "AWS_REGION": config.region,
        "TABLE_NAME": config.table_name,
        "FREE_USAGE_PLAN_ID": config.free_usage_plan_id,
        "METERED_USAGE_PLAN_ID": config.metered_usage_plan_id,
        "API_USAGE_PRODUCT_ID": config.api_usage_product_id,
        "STRIPE_CONFIGURED": "Yes" if config.stripe_secret_key else "No",
    }

    # Add optional vars if set
    if hasattr(config, "metered_price_id"):
        env_vars["METERED_PRICE_ID"] = config.metered_price_id

    if format == "json":
        click.echo(json.dumps(env_vars, indent=2))
    elif format == "shell":
        for key, value in env_vars.items():
            click.echo(f'export {key}="{value}"')
    else:  # text
        click.echo("Current Environment Configuration:")
        click.echo("=" * 50)
        for key, value in env_vars.items():
            click.echo(f"{key:25} : {value}")


@env_group.command("validate")
@click.option("--verbose", is_flag=True, help="Show detailed validation")
def validate(verbose: bool) -> None:
    """Validate environment configuration."""
    errors = []
    warnings = []

    # Required variables
    if not config.stack_name:
        errors.append("STACK_NAME is not set")
    if not config.region:
        errors.append("AWS_REGION is not set")
    if not config.stripe_secret_key:
        errors.append("STRIPE_SECRET_KEY or STRIPE_SECRET_ARN is not set")

    # Check AWS connectivity
    try:
        import boto3

        sts = boto3.client("sts", region_name=config.region)
        identity = sts.get_caller_identity()
        if verbose:
            click.echo(f"✅ AWS connectivity verified (Account: {identity['Account']})")
    except Exception as e:
        errors.append(f"Cannot connect to AWS: {e}")

    # Check DynamoDB table
    if config.table_name:
        try:
            dynamodb = boto3.client("dynamodb", region_name=config.region)
            dynamodb.describe_table(TableName=config.table_name)
            if verbose:
                click.echo(f"✅ DynamoDB table exists: {config.table_name}")
        except Exception as e:
            warnings.append(f"Cannot access DynamoDB table: {e}")

    # Check API Gateway
    if config.free_usage_plan_id:
        try:
            apigw = boto3.client("apigateway", region_name=config.region)
            apigw.get_usage_plan(usagePlanId=config.free_usage_plan_id)
            if verbose:
                click.echo(f"✅ Free usage plan exists: {config.free_usage_plan_id}")
        except Exception as e:
            warnings.append(f"Cannot access free usage plan: {e}")

    # Report results
    if errors:
        click.echo(click.style("❌ Validation failed with errors:", fg="red", bold=True))
        for error in errors:
            click.echo(click.style(f"  • {error}", fg="red"))

    if warnings:
        click.echo(click.style("⚠️  Warnings:", fg="yellow"))
        for warning in warnings:
            click.echo(click.style(f"  • {warning}", fg="yellow"))

    if not errors and not warnings:
        click.echo(click.style("✅ Environment configuration is valid", fg="green"))

    # Exit with error code if validation failed
    if errors:
        raise click.Abort()


@env_group.command("export")
@click.option(
    "--format",
    type=click.Choice(["json", "env"]),
    default="json",
    help="Export format",
)
@click.argument("output_file", type=click.Path(), required=False)
def export(format: str, output_file: str) -> None:
    """Export environment configuration."""
    env_vars = {
        "STACK_NAME": config.stack_name,
        "AWS_REGION": config.region,
        "TABLE_NAME": config.table_name,
        "FREE_USAGE_PLAN_ID": config.free_usage_plan_id,
        "METERED_USAGE_PLAN_ID": config.metered_usage_plan_id,
        "API_USAGE_PRODUCT_ID": config.api_usage_product_id,
    }

    if format == "json":
        content = json.dumps(env_vars, indent=2)
    else:  # env
        content = "\n".join(f'{k}="{v}"' for k, v in env_vars.items())

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        click.echo(f"Configuration exported to {output_file}")
    else:
        click.echo(content)


@env_group.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show what would be imported")
def import_env(input_file: str, dry_run: bool) -> None:
    """Import environment configuration from file."""
    with open(input_file) as f:
        content = f.read()

    # Try to parse as JSON first
    try:
        env_vars = json.loads(content)
    except json.JSONDecodeError:
        # Try to parse as env file
        env_vars = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"')

    click.echo("Environment variables to import:")
    for key, value in env_vars.items():
        masked_value = value if key != "STRIPE_SECRET_KEY" else "***"
        click.echo(f"  {key} = {masked_value}")

    if not dry_run:
        for key, value in env_vars.items():
            os.environ[key] = value
        click.echo(click.style("✅ Environment imported", fg="green"))
    else:
        click.echo(click.style("(Dry run - no changes made)", fg="yellow"))


__all__ = ["env_group"]
