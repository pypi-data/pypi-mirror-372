"""Monitoring dashboard for Zero-Touch operations."""

from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


def get_recent_discoveries(table_name: str, region: str, hours: int = 1) -> list[dict[str, Any]]:
    """Get recently discovered APIs from tracking table."""
    dynamodb = boto3.client("dynamodb", region_name=region)

    # Calculate time threshold
    threshold = datetime.now(UTC) - timedelta(hours=hours)
    threshold_str = threshold.isoformat()

    apis = []
    try:
        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression="last_seen > :threshold",
            ExpressionAttributeValues={":threshold": {"S": threshold_str}},
        )

        for item in response.get("Items", []):
            apis.append(
                {
                    "api_id": item.get("api_id", {}).get("S", ""),
                    "stage": item.get("stage", {}).get("S", ""),
                    "expected_plan": item.get("expected_plan", {}).get("S", ""),
                    "last_seen": item.get("last_seen", {}).get("S", ""),
                }
            )
    except ClientError:
        pass

    return sorted(apis, key=lambda x: x["last_seen"], reverse=True)


def get_lambda_invocations(function_name: str, region: str, hours: int = 1) -> int:
    """Get Lambda invocation count."""
    cloudwatch = boto3.client("cloudwatch", region_name=region)

    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(hours=hours)

    try:
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName="Invocations",
            Dimensions=[{"Name": "FunctionName", "Value": function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=hours * 3600,
            Statistics=["Sum"],
        )

        if response["Datapoints"]:
            return int(response["Datapoints"][0]["Sum"])
    except ClientError:
        pass

    return 0


def get_eventbridge_rule_state(rule_name: str, region: str) -> str:
    """Get EventBridge rule state."""
    events = boto3.client("events", region_name=region)

    try:
        response = events.describe_rule(Name=rule_name)
        return str(response.get("State", "UNKNOWN"))
    except ClientError:
        return "NOT_FOUND"


@click.command("dashboard")
@click.option("--stack-name", envvar="STACK_NAME", required=True, help="CloudFormation stack name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option(
    "--refresh", type=int, default=0, help="Auto-refresh interval in seconds (0=disabled)"
)
def dashboard(stack_name: str, region: str, refresh: int) -> None:
    """
    Real-time monitoring dashboard for Zero-Touch operations.

    Shows:
    - EventBridge rule status
    - Recent Lambda invocations
    - API discovery activity
    - Recent attachments

    Example:
        ai-billing monitor dashboard
        ai-billing monitor dashboard --refresh 30
    """
    import time

    table_name = f"{stack_name}-api-tracking"

    try:
        while True:
            # Clear screen for refresh
            if refresh > 0:
                click.clear()

            click.echo(click.style("=" * 80, fg="blue"))
            click.echo(click.style(f"Zero-Touch Monitoring Dashboard - {stack_name}", bold=True))
            click.echo(click.style("=" * 80, fg="blue"))
            click.echo(f"Last Updated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")

            # EventBridge Rules Status
            click.echo("\n📅 EventBridge Rules:")
            rules = [
                ("API Discovery (5 min)", f"{stack_name}-ApiDiscoveryEveryFiveMinutesRule"),
                ("Usage Reporting (hourly)", f"{stack_name}-HourlyUsageReportingRule"),
                ("Stripe Events", f"{stack_name}-StripeEventProcessorRule"),
            ]

            for rule_desc, rule_name in rules:
                state = get_eventbridge_rule_state(rule_name, region)
                state_color = (
                    "green" if state == "ENABLED" else "red" if state == "DISABLED" else "yellow"
                )
                state_styled = click.style(state, fg=state_color)
                click.echo(f"  • {rule_desc:<30} {state_styled}")

            # Lambda Invocations
            click.echo("\n⚡ Lambda Activity (last hour):")
            lambdas = [
                ("API Discovery", f"{stack_name}-ApiDiscoveryFunction"),
                ("Usage Reporting", f"{stack_name}-UsageReportingFunction"),
                ("Stripe Events", f"{stack_name}-StripeEventProcessor"),
            ]

            for lambda_desc, lambda_name in lambdas:
                invocations = get_lambda_invocations(lambda_name, region, hours=1)
                color = "green" if invocations > 0 else "yellow"
                click.echo(
                    f"  • {lambda_desc:<30} {click.style(str(invocations), fg=color)} invocations"
                )

            # Recent Discoveries
            click.echo("\n🔍 Recent API Discoveries (last hour):")
            recent_apis = get_recent_discoveries(table_name, region, hours=1)

            if recent_apis:
                for api in recent_apis[:5]:  # Show top 5
                    last_seen = datetime.fromisoformat(api["last_seen"].replace("Z", "+00:00"))
                    mins_ago = int((datetime.now(UTC) - last_seen).total_seconds() / 60)
                    click.echo(
                        f"  • {api['api_id']} ({api['stage']}) → {api['expected_plan']} ({mins_ago}m ago)"
                    )
            else:
                click.echo("  No recent discoveries")

            # API Gateway Metrics
            click.echo("\n📊 API Gateway Metrics:")
            cloudwatch = boto3.client("cloudwatch", region_name=region)

            try:
                # Get API call count
                end_time = datetime.now(UTC)
                start_time = end_time - timedelta(hours=1)

                response = cloudwatch.get_metric_statistics(
                    Namespace="AWS/ApiGateway",
                    MetricName="Count",
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=["Sum"],
                )

                api_calls = int(response["Datapoints"][0]["Sum"]) if response["Datapoints"] else 0
                click.echo(f"  • Total API calls (last hour): {api_calls:,}")
            except ClientError:
                click.echo("  • API metrics unavailable")

            # Refresh or exit
            if refresh > 0:
                click.echo(f"\n↻ Refreshing in {refresh} seconds... (Ctrl+C to exit)")
                time.sleep(refresh)
            else:
                break

    except KeyboardInterrupt:
        click.echo("\n\nDashboard stopped")
    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        raise click.Abort()


__all__ = ["dashboard"]
