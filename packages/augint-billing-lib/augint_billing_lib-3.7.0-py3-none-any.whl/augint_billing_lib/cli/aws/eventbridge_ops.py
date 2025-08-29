"""AWS EventBridge operations commands."""

import json
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


@click.group(name="eventbridge", help="EventBridge operations")
def eventbridge_group() -> None:
    """EventBridge command group."""


@eventbridge_group.command("list-rules")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--prefix", help="Filter rules by name prefix")
@click.option("--state", type=click.Choice(["ENABLED", "DISABLED"]), help="Filter by state")
def list_rules(region: str, prefix: str | None, state: str | None) -> None:
    """
    List EventBridge rules.

    Example:
        ai-billing aws eventbridge list-rules
        ai-billing aws eventbridge list-rules --prefix billing-
        ai-billing aws eventbridge list-rules --state DISABLED
    """
    events = boto3.client("events", region_name=region)

    try:
        response = events.list_rules(NamePrefix=prefix or "")

        click.echo(f"\n{'Rule Name':<50} {'State':<12} {'Schedule/Pattern':<40}")
        click.echo("-" * 102)

        for rule in response.get("Rules", []):
            # Apply state filter if specified
            if state and rule.get("State") != state:
                continue

            # Format schedule or event pattern
            schedule = ""
            if rule.get("ScheduleExpression"):
                schedule = rule["ScheduleExpression"]
            elif rule.get("EventPattern"):
                try:
                    pattern = json.loads(rule["EventPattern"])
                    if "source" in pattern:
                        schedule = f"Event: {pattern['source'][0]}"
                    else:
                        schedule = "Event Pattern"
                except json.JSONDecodeError:
                    schedule = "Event Pattern"

            state_color = "green" if rule.get("State") == "ENABLED" else "yellow"
            state_styled = click.style(rule.get("State", "UNKNOWN"), fg=state_color)

            click.echo(f"{rule['Name'][:49]:<50} {state_styled:<12} {schedule[:39]:<40}")

    except ClientError as e:
        click.echo(f"Error listing rules: {e}", err=True)
        raise click.Abort()


@eventbridge_group.command("describe-rule")
@click.option("--rule", required=True, help="Rule name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def describe_rule(rule: str, region: str, output_json: bool) -> None:
    """
    Describe an EventBridge rule in detail.

    Example:
        ai-billing aws eventbridge describe-rule --rule MyRule
        ai-billing aws eventbridge describe-rule --rule MyRule --json
    """
    events = boto3.client("events", region_name=region)

    try:
        response = events.describe_rule(Name=rule)

        # Get targets
        targets_response = events.list_targets_by_rule(Rule=rule)
        targets = targets_response.get("Targets", [])

        if output_json:
            output = {"rule": response, "targets": targets}
            click.echo(json.dumps(output, indent=2, default=str))
        else:
            click.echo(f"\n📋 Rule: {response['Name']}")
            click.echo(
                f"   State: {click.style(response.get('State', 'UNKNOWN'), fg='green' if response.get('State') == 'ENABLED' else 'yellow')}"
            )
            click.echo(f"   Description: {response.get('Description', 'No description')}")

            if response.get("ScheduleExpression"):
                click.echo(f"   Schedule: {response['ScheduleExpression']}")

            if response.get("EventPattern"):
                click.echo("   Event Pattern:")
                try:
                    pattern = json.loads(response["EventPattern"])
                    click.echo(json.dumps(pattern, indent=6))
                except json.JSONDecodeError:
                    click.echo(f"      {response['EventPattern']}")

            if targets:
                click.echo(f"\n🎯 Targets ({len(targets)}):")
                for target in targets:
                    click.echo(f"   - {target['Id']}: {target['Arn']}")
                    if target.get("Input"):
                        click.echo(f"     Input: {target['Input'][:100]}...")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            click.echo(f"Rule '{rule}' not found", err=True)
        else:
            click.echo(f"Error describing rule: {e}", err=True)
        raise click.Abort()


@eventbridge_group.command("enable-rule")
@click.option("--rule", required=True, help="Rule name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
def enable_rule(rule: str, region: str) -> None:
    """
    Enable an EventBridge rule.

    Example:
        ai-billing aws eventbridge enable-rule --rule MyRule
    """
    events = boto3.client("events", region_name=region)

    try:
        events.enable_rule(Name=rule)
        click.echo(click.style(f"✅ Rule '{rule}' enabled", fg="green"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            click.echo(f"Rule '{rule}' not found", err=True)
        else:
            click.echo(f"Error enabling rule: {e}", err=True)
        raise click.Abort()


@eventbridge_group.command("disable-rule")
@click.option("--rule", required=True, help="Rule name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
def disable_rule(rule: str, region: str) -> None:
    """
    Disable an EventBridge rule.

    Example:
        ai-billing aws eventbridge disable-rule --rule MyRule
    """
    events = boto3.client("events", region_name=region)

    try:
        events.disable_rule(Name=rule)
        click.echo(click.style(f"⏸️  Rule '{rule}' disabled", fg="yellow"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            click.echo(f"Rule '{rule}' not found", err=True)
        else:
            click.echo(f"Error disabling rule: {e}", err=True)
        raise click.Abort()


@eventbridge_group.command("put-event")
@click.option("--source", required=True, help="Event source")
@click.option("--detail-type", required=True, help="Event detail type")
@click.option("--detail", help="Event detail (JSON string)")
@click.option("--detail-file", type=click.File("r"), help="Event detail from file")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
def put_event(
    source: str,
    detail_type: str,
    detail: str | None,
    detail_file: Any | None,
    region: str,
) -> None:
    """
    Put a custom event to EventBridge.

    Example:
        ai-billing aws eventbridge put-event --source myapp --detail-type "Test Event" --detail '{}'
        ai-billing aws eventbridge put-event --source myapp --detail-type "Test" --detail-file event.json
    """
    events = boto3.client("events", region_name=region)

    # Prepare detail
    event_detail = "{}"
    if detail:
        event_detail = detail
    elif detail_file:
        event_detail = detail_file.read()

    try:
        response = events.put_events(
            Entries=[
                {
                    "Source": source,
                    "DetailType": detail_type,
                    "Detail": event_detail,
                }
            ]
        )

        if response["FailedEntryCount"] == 0:
            click.echo(click.style("✅ Event sent successfully", fg="green"))
        else:
            click.echo(
                click.style(
                    f"❌ Failed to send event: {response['Entries'][0].get('ErrorMessage')}",
                    fg="red",
                )
            )

    except ClientError as e:
        click.echo(f"Error sending event: {e}", err=True)
        raise click.Abort()


__all__ = ["eventbridge_group"]
