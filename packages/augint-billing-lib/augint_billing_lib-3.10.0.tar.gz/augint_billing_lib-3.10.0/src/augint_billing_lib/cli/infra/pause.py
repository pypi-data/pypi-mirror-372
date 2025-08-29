"""Pause automatic API discovery and processing."""

import boto3
import click
from botocore.exceptions import ClientError


def disable_eventbridge_rule(rule_name: str, region: str) -> bool:
    """Disable an EventBridge rule."""
    events = boto3.client("events", region_name=region)

    try:
        events.disable_rule(Name=rule_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            click.echo(f"⚠️  Rule {rule_name} not found", err=True)
        else:
            click.echo(f"❌ Error disabling rule: {e}", err=True)
        return False


@click.command("pause")
@click.option("--stack-name", envvar="STACK_NAME", required=True, help="CloudFormation stack name")
@click.option(
    "--component",
    type=click.Choice(["discovery", "usage", "stripe", "all"]),
    default="all",
    help="Component to pause",
)
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def pause(stack_name: str, component: str, region: str, force: bool) -> None:
    """
    Pause automatic discovery and processing.

    Disables EventBridge rules to stop automatic:
    - API discovery (every 5 minutes)
    - Usage reporting (hourly)
    - Stripe event processing

    Use this during maintenance or when troubleshooting issues.
    Remember to resume after maintenance is complete.

    Example:
        ai-billing infra pause                    # Pause all components
        ai-billing infra pause --component discovery  # Pause only discovery
        ai-billing infra pause --force            # Skip confirmation
    """
    # Define rules to disable
    rules_map = {
        "discovery": f"{stack_name}-ApiDiscoveryEveryFiveMinutesRule",
        "usage": f"{stack_name}-HourlyUsageReportingRule",
        "stripe": f"{stack_name}-StripeEventProcessorRule",
    }

    if component == "all":
        rules_to_disable = list(rules_map.values())
        component_names = list(rules_map.keys())
    else:
        rules_to_disable = [rules_map[component]]
        component_names = [component]

    # Confirmation prompt
    if not force:
        click.echo(
            click.style("⚠️  WARNING: This will pause automatic processing.", fg="yellow", bold=True)
        )
        click.echo("\nYou are about to pause:")
        for name in component_names:
            click.echo(f"  • {name}")
        click.echo(f"\nStack: {stack_name}")
        click.echo(f"Region: {region}")

        if not click.confirm("\nDo you want to proceed?"):
            click.echo("Aborted.")
            return

    # Disable rules
    click.echo("\n⏸️  Pausing automatic processing...")
    success_count = 0

    for rule_name, comp_name in zip(rules_to_disable, component_names, strict=False):
        click.echo(f"\nDisabling {comp_name}...")
        if disable_eventbridge_rule(rule_name, region):
            click.echo(click.style(f"✅ {comp_name} paused", fg="green"))
            success_count += 1
        else:
            click.echo(click.style(f"❌ Failed to pause {comp_name}", fg="red"))

    if success_count == len(rules_to_disable):
        click.echo(
            click.style(f"\n✅ Successfully paused {success_count} component(s)", fg="green")
        )
        click.echo("\n📌 Remember to resume with: ai-billing infra resume")
    elif success_count > 0:
        click.echo(
            click.style(
                f"\n⚠️  Partially successful: paused {success_count}/{len(rules_to_disable)} components",
                fg="yellow",
            )
        )
    else:
        raise click.ClickException("Failed to pause any components")


__all__ = ["pause"]
