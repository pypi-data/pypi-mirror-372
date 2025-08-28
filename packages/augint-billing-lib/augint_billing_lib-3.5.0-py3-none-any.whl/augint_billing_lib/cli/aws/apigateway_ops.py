"""AWS API Gateway operations commands."""

import json
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


@click.group(name="apigateway", help="API Gateway operations")
def apigateway_group() -> None:
    """API Gateway command group."""


@apigateway_group.command("list-apis")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--limit", type=int, default=50, help="Maximum number of APIs to list")
def list_apis(region: str, limit: int) -> None:
    """
    List REST APIs in API Gateway.

    Example:
        ai-billing aws apigateway list-apis
        ai-billing aws apigateway list-apis --limit 100
    """
    apigw = boto3.client("apigateway", region_name=region)

    try:
        response = apigw.get_rest_apis(limit=limit)

        click.echo(f"\n{'API ID':<25} {'Name':<30} {'Created':<20} {'Endpoint Type':<15}")
        click.echo("-" * 90)

        for api in response.get("items", []):
            created_date = api.get("createdDate")
            created = (
                created_date.strftime("%Y-%m-%d %H:%M")
                if created_date and hasattr(created_date, "strftime")
                else "Unknown"
            )
            endpoint_types = ", ".join(api.get("endpointConfiguration", {}).get("types", []))

            click.echo(
                f"{api['id']:<25} "
                f"{api.get('name', 'Unnamed')[:29]:<30} "
                f"{created:<20} "
                f"{endpoint_types:<15}"
            )

    except ClientError as e:
        click.echo(f"Error listing APIs: {e}", err=True)
        raise click.Abort()


@apigateway_group.command("list-usage-plans")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def list_usage_plans(region: str, output_json: bool) -> None:
    """
    List usage plans and their attached APIs.

    Example:
        ai-billing aws apigateway list-usage-plans
        ai-billing aws apigateway list-usage-plans --json
    """
    apigw = boto3.client("apigateway", region_name=region)

    try:
        response = apigw.get_usage_plans()

        if output_json:
            click.echo(json.dumps(response["items"], indent=2, default=str))
        else:
            click.echo("\n📋 Usage Plans:")

            for plan in response.get("items", []):
                click.echo(f"\n{click.style(plan['name'], bold=True)} (ID: {plan['id']})")

                if plan.get("description"):
                    click.echo(f"  Description: {plan['description']}")

                if plan.get("throttle"):
                    throttle = plan["throttle"]
                    click.echo(
                        f"  Throttle: {throttle.get('rateLimit', 'N/A')} req/s, {throttle.get('burstLimit', 'N/A')} burst"
                    )

                if plan.get("quota"):
                    quota = plan["quota"]
                    click.echo(
                        f"  Quota: {quota.get('limit', 'N/A')} requests per {quota.get('period', 'N/A')}"
                    )

                if plan.get("apiStages"):
                    click.echo("  Attached APIs:")
                    for stage in plan["apiStages"]:
                        click.echo(
                            f"    - {stage['apiId']} (stage: {stage.get('stage', 'unknown')})"
                        )
                else:
                    click.echo("  No APIs attached")

    except ClientError as e:
        click.echo(f"Error listing usage plans: {e}", err=True)
        raise click.Abort()


@apigateway_group.command("get-api-keys")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--include-values", is_flag=True, help="Include API key values (sensitive)")
@click.option("--limit", type=int, default=50, help="Maximum number of keys to list")
def get_api_keys(region: str, include_values: bool, limit: int) -> None:
    """
    List API keys.

    Example:
        ai-billing aws apigateway get-api-keys
        ai-billing aws apigateway get-api-keys --include-values
    """
    apigw = boto3.client("apigateway", region_name=region)

    try:
        response = apigw.get_api_keys(limit=limit, includeValues=include_values)

        if include_values:
            click.echo(click.style("⚠️  WARNING: Displaying API key values", fg="yellow"))

        click.echo(f"\n{'Key ID':<25} {'Name':<30} {'Enabled':<10} {'Created':<20}")
        if include_values:
            click.echo(f"{'Value':<40}")
        click.echo("-" * (85 + (40 if include_values else 0)))

        for key in response.get("items", []):
            created_date = key.get("createdDate")
            created = (
                created_date.strftime("%Y-%m-%d %H:%M")
                if created_date and hasattr(created_date, "strftime")
                else "Unknown"
            )
            enabled = "Yes" if key.get("enabled") else "No"
            enabled_styled = click.style(enabled, fg="green" if enabled == "Yes" else "red")

            row = (
                f"{key['id']:<25} "
                f"{key.get('name', 'Unnamed')[:29]:<30} "
                f"{enabled_styled:<10} "
                f"{created:<20}"
            )

            if include_values:
                row += f" {key.get('value', 'N/A'):<40}"

            click.echo(row)

    except ClientError as e:
        click.echo(f"Error listing API keys: {e}", err=True)
        raise click.Abort()


@apigateway_group.command("get-usage")
@click.option("--plan-id", required=True, help="Usage plan ID")
@click.option("--key-id", help="API key ID (for specific key usage)")
@click.option("--start-date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", required=True, help="End date (YYYY-MM-DD)")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def get_usage(
    plan_id: str,
    key_id: str | None,
    start_date: str,
    end_date: str,
    region: str,
    output_json: bool,
) -> None:
    """
    Get usage data for a usage plan.

    Example:
        ai-billing aws apigateway get-usage --plan-id FREE_10K --start-date 2024-01-01 --end-date 2024-01-31
        ai-billing aws apigateway get-usage --plan-id METERED --key-id abc123 --start-date 2024-01-01 --end-date 2024-01-31
    """
    apigw = boto3.client("apigateway", region_name=region)

    try:
        params: dict[str, Any] = {
            "usagePlanId": plan_id,
            "startDate": start_date,
            "endDate": end_date,
        }

        if key_id:
            params["keyId"] = key_id

        response = apigw.get_usage(**params)

        if output_json:
            click.echo(json.dumps(response, indent=2, default=str))
        else:
            click.echo("\n📊 Usage Report")
            click.echo(f"   Plan: {plan_id}")
            if key_id:
                click.echo(f"   Key: {key_id}")
            click.echo(f"   Period: {start_date} to {end_date}")

            if response.get("items"):
                click.echo("\n   Usage by API Key:")
                # AWS API Gateway usage data is complex, just display the raw count
                for api_key_id in response["items"]:
                    click.echo(f"     {api_key_id}")
            else:
                click.echo("\n   No usage data found for this period")

    except ClientError as e:
        click.echo(f"Error getting usage: {e}", err=True)
        raise click.Abort()


@apigateway_group.command("update-api-key")
@click.option("--key-id", required=True, help="API key ID")
@click.option("--enable/--disable", help="Enable or disable the key")
@click.option("--name", help="New name for the key")
@click.option("--description", help="New description")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
def update_api_key(
    key_id: str,
    enable: bool | None,
    name: str | None,
    description: str | None,
    region: str,
) -> None:
    """
    Update an API key.

    Example:
        ai-billing aws apigateway update-api-key --key-id abc123 --disable
        ai-billing aws apigateway update-api-key --key-id abc123 --name "New Name"
    """
    apigw = boto3.client("apigateway", region_name=region)

    patch_operations = []

    if enable is not None:
        patch_operations.append({"op": "replace", "path": "/enabled", "value": str(enable).lower()})

    if name:
        patch_operations.append({"op": "replace", "path": "/name", "value": name})

    if description:
        patch_operations.append({"op": "replace", "path": "/description", "value": description})

    if not patch_operations:
        click.echo("No updates specified", err=True)
        return

    try:
        response = apigw.update_api_key(
            apiKey=key_id,
            patchOperations=patch_operations,  # type: ignore[arg-type]
        )

        click.echo(click.style(f"✅ API key {key_id} updated successfully", fg="green"))

        if response.get("name"):
            click.echo(f"   Name: {response['name']}")
        if "enabled" in response:
            status = "Enabled" if response["enabled"] else "Disabled"
            click.echo(f"   Status: {status}")
        if response.get("description"):
            click.echo(f"   Description: {response['description']}")

    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFoundException":
            click.echo(f"API key '{key_id}' not found", err=True)
        else:
            click.echo(f"Error updating API key: {e}", err=True)
        raise click.Abort()


__all__ = ["apigateway_group"]
