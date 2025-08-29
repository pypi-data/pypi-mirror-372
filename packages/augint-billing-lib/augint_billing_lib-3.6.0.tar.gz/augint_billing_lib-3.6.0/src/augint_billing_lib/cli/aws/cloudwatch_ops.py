"""AWS CloudWatch operations commands."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


@click.group(name="cloudwatch", help="CloudWatch operations")
def cloudwatch_group() -> None:
    """CloudWatch command group."""


@cloudwatch_group.command("list-log-groups")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--prefix", help="Filter log groups by prefix")
@click.option("--limit", type=int, default=50, help="Maximum number to list")
def list_log_groups(region: str, prefix: str | None, limit: int) -> None:
    """
    List CloudWatch log groups.

    Example:
        ai-billing aws cloudwatch list-log-groups
        ai-billing aws cloudwatch list-log-groups --prefix /aws/lambda/
    """
    logs = boto3.client("logs", region_name=region)

    try:
        params: dict[str, Any] = {"limit": limit}
        if prefix:
            params["logGroupNamePrefix"] = prefix

        response = logs.describe_log_groups(**params)

        click.echo(f"\n{'Log Group':<50} {'Retention':<15} {'Size (MB)':<15}")
        click.echo("-" * 80)

        for group in response.get("logGroups", []):
            retention = (
                f"{group.get('retentionInDays', 'Never')} days"
                if group.get("retentionInDays")
                else "Never"
            )
            size_mb = f"{group.get('storedBytes', 0) / 1024 / 1024:.2f}"

            click.echo(f"{group['logGroupName'][:49]:<50} {retention:<15} {size_mb:<15}")

    except ClientError as e:
        click.echo(f"Error listing log groups: {e}", err=True)
        raise click.Abort()


@cloudwatch_group.command("tail-logs")
@click.option("--log-group", required=True, help="Log group name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--filter", "filter_pattern", help="CloudWatch filter pattern")
@click.option("--since", type=int, default=5, help="Minutes to look back")
@click.option("--follow", is_flag=True, help="Follow log output")
def tail_logs(
    log_group: str,
    region: str,
    filter_pattern: str | None,
    since: int,
    follow: bool,
) -> None:
    """
    Tail CloudWatch logs.

    Example:
        ai-billing aws cloudwatch tail-logs --log-group /aws/lambda/my-func
        ai-billing aws cloudwatch tail-logs --log-group /aws/lambda/my-func --follow
        ai-billing aws cloudwatch tail-logs --log-group /aws/lambda/my-func --filter ERROR
    """
    logs = boto3.client("logs", region_name=region)

    start_time = datetime.now(UTC) - timedelta(minutes=since)
    start_timestamp = int(start_time.timestamp() * 1000)

    if follow:
        click.echo(f"Following logs from {log_group} (Ctrl+C to stop)...")
        click.echo("-" * 80)

        last_timestamp = start_timestamp
        try:
            while True:
                response = logs.filter_log_events(
                    logGroupName=log_group,
                    startTime=last_timestamp,
                    filterPattern=filter_pattern or "",
                )

                for event in response.get("events", []):
                    timestamp = datetime.fromtimestamp(event["timestamp"] / 1000, UTC)
                    message = event["message"].rstrip()
                    click.echo(f"[{timestamp.isoformat()}] {message}")
                    last_timestamp = max(last_timestamp, event["timestamp"] + 1)

                # Sleep before next poll
                import time

                time.sleep(2)

        except KeyboardInterrupt:
            click.echo("\nStopped following logs")
    else:
        click.echo(f"Fetching logs from {log_group} (last {since} minutes)...")

        try:
            response = logs.filter_log_events(
                logGroupName=log_group,
                startTime=start_timestamp,
                filterPattern=filter_pattern or "",
                limit=100,
            )

            for event in response.get("events", []):
                timestamp = datetime.fromtimestamp(event["timestamp"] / 1000, UTC)
                message = event["message"].rstrip()
                click.echo(f"[{timestamp.isoformat()}] {message}")

            if not response.get("events"):
                click.echo("No logs found in the specified time range")

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                click.echo(f"Log group '{log_group}' not found", err=True)
            else:
                click.echo(f"Error fetching logs: {e}", err=True)
            raise click.Abort()


@cloudwatch_group.command("list-alarms")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option(
    "--state", type=click.Choice(["OK", "ALARM", "INSUFFICIENT_DATA"]), help="Filter by state"
)
@click.option("--prefix", help="Filter alarms by name prefix")
def list_alarms(region: str, state: str | None, prefix: str | None) -> None:
    """
    List CloudWatch alarms.

    Example:
        ai-billing aws cloudwatch list-alarms
        ai-billing aws cloudwatch list-alarms --state ALARM
        ai-billing aws cloudwatch list-alarms --prefix billing-
    """
    cloudwatch = boto3.client("cloudwatch", region_name=region)

    try:
        params: dict[str, Any] = {}
        if state:
            params["StateValue"] = state
        if prefix:
            params["AlarmNamePrefix"] = prefix

        response = cloudwatch.describe_alarms(**params)

        if not response.get("MetricAlarms"):
            click.echo("No alarms found")
            return

        click.echo(f"\n{'Alarm Name':<40} {'State':<20} {'Metric':<30}")
        click.echo("-" * 90)

        for alarm in response["MetricAlarms"]:
            state_value = alarm["StateValue"]
            state_color = (
                "green" if state_value == "OK" else "red" if state_value == "ALARM" else "yellow"
            )
            state_styled = click.style(state_value, fg=state_color)

            metric_name = f"{alarm.get('Namespace', '')}/{alarm.get('MetricName', '')}"

            click.echo(f"{alarm['AlarmName'][:39]:<40} {state_styled:<20} {metric_name[:29]:<30}")

    except ClientError as e:
        click.echo(f"Error listing alarms: {e}", err=True)
        raise click.Abort()


@cloudwatch_group.command("get-metrics")
@click.option("--namespace", required=True, help="CloudWatch namespace (e.g., AWS/Lambda)")
@click.option("--metric", required=True, help="Metric name (e.g., Invocations)")
@click.option("--dimensions", help='Dimensions as JSON (e.g., \'{"FunctionName": "my-func"}\')')
@click.option("--hours", type=int, default=1, help="Hours to look back")
@click.option(
    "--stat",
    type=click.Choice(["Sum", "Average", "Maximum", "Minimum"]),
    default="Sum",
    help="Statistic",
)
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
def get_metrics(
    namespace: str,
    metric: str,
    dimensions: str | None,
    hours: int,
    stat: str,
    region: str,
) -> None:
    """
    Get CloudWatch metrics.

    Example:
        ai-billing aws cloudwatch get-metrics --namespace AWS/Lambda --metric Invocations --dimensions '{"FunctionName": "my-func"}'
        ai-billing aws cloudwatch get-metrics --namespace AWS/ApiGateway --metric Count --hours 24
    """
    cloudwatch = boto3.client("cloudwatch", region_name=region)

    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(hours=hours)

    # Parse dimensions
    dimension_list = []
    if dimensions:
        try:
            dims = json.loads(dimensions)
            dimension_list = [{"Name": k, "Value": v} for k, v in dims.items()]
        except json.JSONDecodeError:
            click.echo("Invalid dimensions JSON", err=True)
            raise click.Abort()

    try:
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric,
            Dimensions=dimension_list,
            StartTime=start_time,
            EndTime=end_time,
            Period=3600 if hours > 1 else 300,  # 1 hour or 5 minute periods
            Statistics=[stat],
        )

        if not response.get("Datapoints"):
            click.echo("No data points found for the specified metric and time range")
            return

        click.echo(f"\n📊 Metric: {namespace}/{metric}")
        if dimension_list:
            click.echo(f"   Dimensions: {dimensions}")
        click.echo(f"   Period: Last {hours} hour(s)")
        click.echo(f"   Statistic: {stat}")
        click.echo("\n   Data Points:")

        # Sort by timestamp
        datapoints = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])

        for point in datapoints:
            timestamp = point["Timestamp"].strftime("%Y-%m-%d %H:%M")
            value = point[stat]
            if isinstance(value, float):
                value = f"{value:.2f}"
            click.echo(f"     {timestamp}: {value}")

        # Show summary
        if len(datapoints) > 1:
            values = [p[stat] for p in datapoints]
            click.echo("\n   Summary:")
            click.echo(f"     Total points: {len(datapoints)}")
            if stat == "Sum":
                click.echo(f"     Grand total: {sum(values):.2f}")
            else:
                click.echo(f"     Min: {min(values):.2f}")
                click.echo(f"     Max: {max(values):.2f}")
                click.echo(f"     Avg: {sum(values) / len(values):.2f}")

    except ClientError as e:
        click.echo(f"Error getting metrics: {e}", err=True)
        raise click.Abort()


__all__ = ["cloudwatch_group"]
