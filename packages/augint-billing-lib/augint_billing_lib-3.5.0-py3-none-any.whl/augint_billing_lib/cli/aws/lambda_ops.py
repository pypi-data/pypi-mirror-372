"""AWS Lambda operations commands."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


@click.group(name="lambda", help="Lambda function operations")
def lambda_group() -> None:
    """Lambda command group."""


@lambda_group.command("list")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--prefix", help="Filter functions by name prefix")
@click.option("--runtime", help="Filter by runtime (e.g., python3.11)")
def list_functions(region: str, prefix: str | None, runtime: str | None) -> None:
    """
    List Lambda functions.

    Example:
        ai-billing aws lambda list
        ai-billing aws lambda list --prefix billing-
        ai-billing aws lambda list --runtime python3.11
    """
    lambda_client = boto3.client("lambda", region_name=region)

    try:
        paginator = lambda_client.get_paginator("list_functions")

        click.echo(f"\n{'Function Name':<50} {'Runtime':<15} {'Memory':<10} {'Timeout':<10}")
        click.echo("-" * 85)

        for page in paginator.paginate():
            for func in page["Functions"]:
                name = func["FunctionName"]

                # Apply filters
                if prefix and not name.startswith(prefix):
                    continue
                if runtime and func.get("Runtime") != runtime:
                    continue

                click.echo(
                    f"{name[:49]:<50} "
                    f"{func.get('Runtime', 'N/A'):<15} "
                    f"{func.get('MemorySize', 0):<10} "
                    f"{func.get('Timeout', 0):<10}"
                )

    except ClientError as e:
        click.echo(f"Error listing functions: {e}", err=True)
        raise click.Abort()


@lambda_group.command("invoke")
@click.option("--function", required=True, help="Function name or ARN")
@click.option("--payload", help="JSON payload string")
@click.option("--payload-file", type=click.File("r"), help="JSON payload file")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--async", "async_invoke", is_flag=True, help="Asynchronous invocation")
def invoke_function(
    function: str,
    payload: str | None,
    payload_file: Any | None,
    region: str,
    async_invoke: bool,
) -> None:
    """
    Invoke a Lambda function.

    Example:
        ai-billing aws lambda invoke --function my-func
        ai-billing aws lambda invoke --function my-func --payload '{"key": "value"}'
        ai-billing aws lambda invoke --function my-func --payload-file event.json
    """
    lambda_client = boto3.client("lambda", region_name=region)

    # Prepare payload
    invoke_payload = "{}"
    if payload:
        invoke_payload = payload
    elif payload_file:
        invoke_payload = payload_file.read()

    invocation_type = "Event" if async_invoke else "RequestResponse"

    try:
        click.echo(f"Invoking {function}...")

        response = lambda_client.invoke(
            FunctionName=function,
            InvocationType=invocation_type,
            Payload=invoke_payload,
        )

        status_code = response["StatusCode"]

        if async_invoke:
            if status_code == 202:
                click.echo(click.style("✅ Function invoked asynchronously", fg="green"))
            else:
                click.echo(click.style(f"❌ Invocation failed with status {status_code}", fg="red"))
        elif status_code == 200:
            click.echo(click.style("✅ Function executed successfully", fg="green"))

            # Show response payload
            if "Payload" in response:
                payload_str = response["Payload"].read().decode("utf-8")
                try:
                    payload_json = json.loads(payload_str)
                    click.echo("\nResponse:")
                    click.echo(json.dumps(payload_json, indent=2))
                except json.JSONDecodeError:
                    click.echo(f"\nResponse: {payload_str}")
        else:
            click.echo(click.style(f"❌ Function failed with status {status_code}", fg="red"))

            # Show error if available
            if "FunctionError" in response:
                click.echo(f"Error type: {response['FunctionError']}")
            if "Payload" in response:
                error_payload = response["Payload"].read().decode("utf-8")
                click.echo(f"Error details: {error_payload}")

    except ClientError as e:
        click.echo(f"Error invoking function: {e}", err=True)
        raise click.Abort()


@lambda_group.command("logs")
@click.option("--function", required=True, help="Function name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--hours", type=int, default=1, help="Hours of logs to fetch")
@click.option("--filter", "filter_pattern", help="CloudWatch filter pattern")
@click.option("--follow", is_flag=True, help="Follow log output")
def get_logs(
    function: str,
    region: str,
    hours: int,
    filter_pattern: str | None,
    follow: bool,
) -> None:
    """
    Get Lambda function logs.

    Example:
        ai-billing aws lambda logs --function my-func
        ai-billing aws lambda logs --function my-func --hours 24
        ai-billing aws lambda logs --function my-func --filter ERROR
        ai-billing aws lambda logs --function my-func --follow
    """
    logs_client = boto3.client("logs", region_name=region)

    log_group = f"/aws/lambda/{function}"
    start_time = datetime.now(UTC) - timedelta(hours=hours)
    start_timestamp = int(start_time.timestamp() * 1000)

    try:
        # Check if log group exists
        logs_client.describe_log_groups(logGroupNamePrefix=log_group)
    except ClientError:
        click.echo(f"No logs found for function {function}", err=True)
        return

    if follow:
        click.echo(f"Following logs for {function} (Ctrl+C to stop)...")
        click.echo("-" * 80)

        last_timestamp = start_timestamp
        try:
            while True:
                response = logs_client.filter_log_events(
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
        click.echo(f"Fetching logs for {function} (last {hours} hours)...")

        try:
            paginator = logs_client.get_paginator("filter_log_events")

            for page in paginator.paginate(
                logGroupName=log_group,
                startTime=start_timestamp,
                filterPattern=filter_pattern or "",
            ):
                for event in page.get("events", []):
                    timestamp = datetime.fromtimestamp(event["timestamp"] / 1000, UTC)
                    message = event["message"].rstrip()
                    click.echo(f"[{timestamp.isoformat()}] {message}")

        except ClientError as e:
            click.echo(f"Error fetching logs: {e}", err=True)


@lambda_group.command("errors")
@click.option("--function", required=True, help="Function name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--hours", type=int, default=24, help="Hours to look back")
def get_errors(function: str, region: str, hours: int) -> None:
    """
    Get Lambda function errors and metrics.

    Example:
        ai-billing aws lambda errors --function my-func
        ai-billing aws lambda errors --function my-func --hours 48
    """
    cloudwatch = boto3.client("cloudwatch", region_name=region)
    lambda_client = boto3.client("lambda", region_name=region)

    # Get function configuration
    try:
        func_config = lambda_client.get_function_configuration(FunctionName=function)
        click.echo(f"\n📊 Function: {func_config['FunctionName']}")
        click.echo(f"   Runtime: {func_config.get('Runtime', 'N/A')}")
        click.echo(f"   Memory: {func_config.get('MemorySize', 0)} MB")
        click.echo(f"   Timeout: {func_config.get('Timeout', 0)} seconds")
    except ClientError:
        click.echo(f"Function {function} not found", err=True)
        return

    # Get metrics
    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(hours=hours)

    metrics_to_fetch = [
        ("Invocations", "Sum", "Total invocations"),
        ("Errors", "Sum", "Total errors"),
        ("Throttles", "Sum", "Throttled invocations"),
        ("Duration", "Average", "Avg duration (ms)"),
        ("ConcurrentExecutions", "Maximum", "Max concurrent"),
    ]

    click.echo(f"\n📈 Metrics (last {hours} hours):")

    for metric_name, stat, label in metrics_to_fetch:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName=metric_name,
                Dimensions=[{"Name": "FunctionName", "Value": function}],
                StartTime=start_time,
                EndTime=end_time,
                Period=hours * 3600,  # One data point for entire period
                Statistics=[stat],
            )

            if response["Datapoints"]:
                value = response["Datapoints"][0][stat]
                if metric_name == "Duration":
                    value = f"{value:.2f}"
                elif metric_name == "Errors" and value > 0:
                    click.echo(f"   {label}: {click.style(str(value), fg='red')}")
                    continue
                click.echo(f"   {label}: {value}")
            else:
                click.echo(f"   {label}: 0")

        except ClientError:
            click.echo(f"   {label}: N/A")

    # Get recent errors from logs
    click.echo("\n🔍 Recent errors:")
    logs_client = boto3.client("logs", region_name=region)
    log_group = f"/aws/lambda/{function}"

    try:
        response = logs_client.filter_log_events(
            logGroupName=log_group,
            startTime=int(start_time.timestamp() * 1000),
            filterPattern="ERROR",
            limit=10,
        )

        if response.get("events"):
            for event in response["events"][:5]:  # Show first 5 errors
                timestamp = datetime.fromtimestamp(event["timestamp"] / 1000, UTC)
                message = event["message"].strip()[:200]  # Truncate long messages
                click.echo(f"   [{timestamp.strftime('%Y-%m-%d %H:%M')}] {message}")
        else:
            click.echo("   No errors found in logs")

    except ClientError:
        click.echo("   Could not fetch error logs")


__all__ = ["lambda_group"]
