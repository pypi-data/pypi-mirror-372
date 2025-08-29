"""List discovered APIs and their attachment status."""

import json
from collections import defaultdict
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


def get_all_apis(region: str) -> list[dict[str, Any]]:
    """Get all REST APIs in the region."""
    apigw = boto3.client("apigateway", region_name=region)

    apis = []
    try:
        paginator = apigw.get_paginator("get_rest_apis")
        for page in paginator.paginate():
            for api in page.get("items", []):
                api_info = {
                    "id": api["id"],
                    "name": api["name"],
                    "description": api.get("description", ""),
                    "created_date": str(api.get("createdDate", "")),
                    "endpoint_configuration": api.get("endpointConfiguration", {}).get("types", []),
                    "stages": [],
                    "attached_to": [],
                }

                # Get stages for this API
                try:
                    stages_response = apigw.get_stages(restApiId=api["id"])
                    api_info["stages"] = [
                        stage["stageName"] for stage in stages_response.get("item", [])
                    ]
                except ClientError:
                    pass

                apis.append(api_info)

    except ClientError as e:
        click.echo(f"Error fetching APIs: {e}", err=True)

    return apis


def get_usage_plan_attachments(region: str) -> dict[str, list[str]]:
    """Get all APIs attached to usage plans."""
    apigw = boto3.client("apigateway", region_name=region)

    attachments = defaultdict(list)

    try:
        response = apigw.get_usage_plans()

        for plan in response.get("items", []):
            plan_name = plan["name"]

            for api_stage in plan.get("apiStages", []):
                api_id = api_stage["apiId"]
                stage = api_stage.get("stage", "unknown")
                attachments[api_id].append(f"{plan_name}/{stage}")

    except ClientError as e:
        click.echo(f"Error fetching usage plans: {e}", err=True)

    return attachments


def check_api_in_dynamodb(api_id: str, table_name: str, region: str) -> bool:
    """Check if API exists in DynamoDB tracking table."""
    dynamodb = boto3.client("dynamodb", region_name=region)

    try:
        response = dynamodb.get_item(TableName=table_name, Key={"api_id": {"S": api_id}})
        return "Item" in response
    except ClientError:
        return False


@click.command("list-apis")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option("--filter-attached", is_flag=True, help="Show only attached APIs")
@click.option("--filter-unattached", is_flag=True, help="Show only unattached APIs")
def list_apis(
    region: str, output_format: str, filter_attached: bool, filter_unattached: bool
) -> None:
    """
    List all discovered APIs with attachment status.

    Shows all REST APIs in the region along with their attachment
    status to usage plans (FREE/METERED/BOTH/NONE).

    Example:
        ai-billing infra list-apis
        ai-billing infra list-apis --filter-unattached
        ai-billing infra list-apis --format json
    """
    click.echo("🔍 Fetching APIs and usage plan attachments...")

    # Get all APIs
    apis = get_all_apis(region)

    # Get usage plan attachments
    attachments = get_usage_plan_attachments(region)

    # Merge attachment info
    for api in apis:
        api["attached_to"] = attachments.get(api["id"], [])

        # Determine attachment status
        plan_types = set()
        for attachment in api["attached_to"]:
            if "free" in attachment.lower():
                plan_types.add("FREE")
            elif "metered" in attachment.lower():
                plan_types.add("METERED")
            else:
                plan_types.add("OTHER")

        if "FREE" in plan_types and "METERED" in plan_types:
            api["status"] = "BOTH"
        elif "FREE" in plan_types:
            api["status"] = "FREE"
        elif "METERED" in plan_types:
            api["status"] = "METERED"
        elif plan_types:
            api["status"] = "OTHER"
        else:
            api["status"] = "NONE"

    # Apply filters
    if filter_attached:
        apis = [api for api in apis if api["status"] != "NONE"]
    elif filter_unattached:
        apis = [api for api in apis if api["status"] == "NONE"]

    # Output results
    if output_format == "json":
        click.echo(json.dumps(apis, indent=2, default=str))
    else:
        # Table format
        click.echo(f"\n{'=' * 100}")
        click.echo(click.style("Discovered APIs", bold=True))
        click.echo(f"{'=' * 100}")

        if not apis:
            click.echo("No APIs found")
        else:
            # Header
            click.echo(f"{'API ID':<30} {'Name':<30} {'Status':<10} {'Stages':<20}")
            click.echo("-" * 100)

            # Rows
            for api in apis:
                status_color = {
                    "BOTH": "green",
                    "FREE": "cyan",
                    "METERED": "blue",
                    "OTHER": "yellow",
                    "NONE": "red",
                }.get(api["status"], "white")

                stages = ", ".join(api["stages"][:3])  # Show first 3 stages
                if len(api["stages"]) > 3:
                    stages += f" (+{len(api['stages']) - 3})"

                status_styled = click.style(api["status"], fg=status_color)
                click.echo(
                    f"{api['id']:<30} {api['name'][:29]:<30} {status_styled:<20} {stages:<20}"
                )

            # Summary
            click.echo(f"\n{'=' * 100}")
            total = len(apis)
            attached = len([a for a in apis if a["status"] != "NONE"])
            unattached = total - attached

            click.echo(f"Total APIs: {total}")
            click.echo(f"  • Attached: {attached}")
            click.echo(f"  • Unattached: {unattached}")

            # Breakdown by status
            status_counts: dict[str, int] = defaultdict(int)
            for api in apis:
                status_counts[api["status"]] += 1

            if status_counts:
                click.echo("\nBy Status:")
                for status, count in sorted(status_counts.items()):
                    click.echo(f"  • {status}: {count}")

            click.echo()


__all__ = ["list_apis"]
