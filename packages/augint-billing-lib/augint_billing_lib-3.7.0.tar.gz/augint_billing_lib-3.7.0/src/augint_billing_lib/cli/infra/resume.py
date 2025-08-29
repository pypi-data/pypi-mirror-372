"""Resume automatic API discovery and processing."""

import boto3
import click
from botocore.exceptions import ClientError


def enable_eventbridge_rule(rule_name: str, region: str) -> bool:
    """Enable an EventBridge rule."""
    events = boto3.client("events", region_name=region)

    try:
        events.enable_rule(Name=rule_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            click.echo(f"⚠️  Rule {rule_name} not found", err=True)
        else:
            click.echo(f"❌ Error enabling rule: {e}", err=True)
        return False


def check_rule_state(rule_name: str, region: str) -> str | None:
    """Check the current state of an EventBridge rule."""
    events = boto3.client("events", region_name=region)

    try:
        response = events.describe_rule(Name=rule_name)
        return str(response.get("State")) if response.get("State") else None
    except ClientError:
        return None


@click.command("resume")
@click.option("--stack-name", envvar="STACK_NAME", required=True, help="CloudFormation stack name")
@click.option(
    "--component",
    type=click.Choice(["discovery", "usage", "stripe", "all"]),
    default="all",
    help="Component to resume",
)
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--check", is_flag=True, help="Check current state without resuming")
def resume(stack_name: str, component: str, region: str, check: bool) -> None:
    """
    Resume automatic discovery and processing.

    Re-enables EventBridge rules to restart automatic:
    - API discovery (every 5 minutes)
    - Usage reporting (hourly)
    - Stripe event processing

    Use after maintenance or troubleshooting is complete.

    Example:
        ai-billing infra resume                    # Resume all components
        ai-billing infra resume --component usage  # Resume only usage reporting
        ai-billing infra resume --check            # Check current state
    """
    # Define rules to enable
    rules_map = {
        "discovery": f"{stack_name}-ApiDiscoveryEveryFiveMinutesRule",
        "usage": f"{stack_name}-HourlyUsageReportingRule",
        "stripe": f"{stack_name}-StripeEventProcessorRule",
    }

    if component == "all":
        rules_to_check = list(rules_map.items())
    else:
        rules_to_check = [(component, rules_map[component])]

    # Check mode - just show current state
    if check:
        click.echo(f"\n📊 Current state for stack '{stack_name}':")
        click.echo(f"{'Component':<15} {'Rule Name':<50} {'State':<10}")
        click.echo("-" * 75)

        for comp_name, rule_name in rules_to_check:
            state = check_rule_state(rule_name, region)
            if state:
                state_color = "green" if state == "ENABLED" else "yellow"
                state_styled = click.style(state, fg=state_color)
            else:
                state_styled = click.style("NOT FOUND", fg="red")

            click.echo(f"{comp_name:<15} {rule_name:<50} {state_styled}")

        return

    # Resume mode - enable rules
    click.echo("\n▶️  Resuming automatic processing...")
    success_count = 0
    already_enabled = 0

    for comp_name, rule_name in rules_to_check:
        # Check current state first
        current_state = check_rule_state(rule_name, region)

        if current_state == "ENABLED":
            click.echo(f"\n✅ {comp_name} is already enabled")
            already_enabled += 1
            success_count += 1
        else:
            click.echo(f"\nEnabling {comp_name}...")
            if enable_eventbridge_rule(rule_name, region):
                click.echo(click.style(f"✅ {comp_name} resumed", fg="green"))
                success_count += 1
            else:
                click.echo(click.style(f"❌ Failed to resume {comp_name}", fg="red"))

    # Summary
    if success_count == len(rules_to_check):
        if already_enabled == len(rules_to_check):
            click.echo(
                click.style(
                    f"\n✅ All {success_count} component(s) were already enabled", fg="green"
                )
            )
        else:
            click.echo(
                click.style(f"\n✅ Successfully resumed {success_count} component(s)", fg="green")
            )
    elif success_count > 0:
        click.echo(
            click.style(
                f"\n⚠️  Partially successful: resumed {success_count}/{len(rules_to_check)} components",
                fg="yellow",
            )
        )
    else:
        raise click.ClickException("Failed to resume any components")


__all__ = ["resume"]
