"""Verify API attachments and configuration."""

import json
from collections import defaultdict
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


def get_expected_apis(table_name: str, region: str) -> list[dict[str, Any]]:
    """Get expected APIs from DynamoDB tracking table."""
    dynamodb = boto3.client("dynamodb", region_name=region)

    apis = []
    try:
        paginator = dynamodb.get_paginator("scan")
        for page in paginator.paginate(TableName=table_name):
            for item in page.get("Items", []):
                if "api_id" in item:
                    api_info = {
                        "api_id": item["api_id"]["S"],
                        "stage": item.get("stage", {}).get("S", "unknown"),
                        "expected_plan": item.get("expected_plan", {}).get("S", "unknown"),
                        "last_seen": item.get("last_seen", {}).get("S", ""),
                    }
                    apis.append(api_info)
    except ClientError as e:
        click.echo(f"Warning: Could not read tracking table: {e}", err=True)

    return apis


def verify_api_attachment(
    api_id: str, stage: str, expected_plan: str, region: str
) -> dict[str, Any]:
    """Verify that an API is attached to the correct usage plan."""
    apigw = boto3.client("apigateway", region_name=region)

    result: dict[str, Any] = {
        "api_id": api_id,
        "stage": stage,
        "expected_plan": expected_plan,
        "actual_plans": [],
        "status": "UNKNOWN",
        "message": "",
    }

    try:
        # Check which plans the API is attached to
        response = apigw.get_usage_plans()

        for plan in response.get("items", []):
            for api_stage in plan.get("apiStages", []):
                if api_stage["apiId"] == api_id and api_stage.get("stage") == stage:
                    result["actual_plans"].append(plan["name"])

        # Determine status
        if not result["actual_plans"]:
            result["status"] = "NOT_ATTACHED"
            result["message"] = "API not attached to any usage plan"
        elif expected_plan.upper() in [p.upper() for p in result["actual_plans"]]:
            if len(result["actual_plans"]) == 1:
                result["status"] = "CORRECT"
                result["message"] = "Attached to correct plan"
            else:
                result["status"] = "MULTIPLE"
                result["message"] = (
                    f"Attached to multiple plans: {', '.join(result['actual_plans'])}"
                )
        else:
            result["status"] = "WRONG_PLAN"
            result["message"] = (
                f"Expected {expected_plan}, found in {', '.join(result['actual_plans'])}"
            )

    except ClientError as e:
        result["status"] = "ERROR"
        result["message"] = str(e)

    return result


def check_api_exists(api_id: str, region: str) -> bool:
    """Check if an API exists in API Gateway."""
    apigw = boto3.client("apigateway", region_name=region)

    try:
        apigw.get_rest_api(restApiId=api_id)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFoundException":
            return False
        raise


@click.command("verify")
@click.option("--stack-name", envvar="STACK_NAME", help="CloudFormation stack name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--table-name", envvar="TABLE_NAME", help="DynamoDB tracking table name")
@click.option("--fix", is_flag=True, help="Attempt to fix incorrect attachments")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def verify(
    stack_name: str | None,
    region: str,
    table_name: str | None,
    fix: bool,
    output_json: bool,
) -> None:
    """
    Verify API attachments match expected configuration.

    Checks that:
    - All tracked APIs exist in API Gateway
    - APIs are attached to the correct usage plans
    - No APIs are attached to multiple plans (unless expected)
    - No orphaned APIs (in plans but not tracked)

    Example:
        ai-billing infra verify
        ai-billing infra verify --fix
        ai-billing infra verify --json
    """
    # Determine table name
    if not table_name:
        if stack_name:
            table_name = f"{stack_name}-api-tracking"
        else:
            click.echo(
                click.style("Error: Need either STACK_NAME or TABLE_NAME to verify", fg="red"),
                err=True,
            )
            raise click.Abort()

    click.echo("🔍 Verifying API attachments...")

    # Get all actual API attachments
    apigw = boto3.client("apigateway", region_name=region)
    actual_attachments: dict[str, list[str]] = defaultdict(list)

    try:
        response = apigw.get_usage_plans()
        for plan in response.get("items", []):
            plan_name = plan["name"]
            for api_stage in plan.get("apiStages", []):
                api_key = f"{api_stage['apiId']}:{api_stage.get('stage', 'unknown')}"
                actual_attachments[api_key].append(plan_name)
    except ClientError as e:
        click.echo(f"Error fetching usage plans: {e}", err=True)
        raise click.Abort()

    # Get expected APIs from tracking table
    expected_apis = get_expected_apis(table_name, region)

    # Verify each expected API
    verification_results = []
    issues: dict[str, list[Any]] = {
        "not_attached": [],
        "wrong_plan": [],
        "multiple_plans": [],
        "api_not_found": [],
    }

    for api in expected_apis:
        api_id = api["api_id"]
        stage = api["stage"]

        # Check if API exists
        if not check_api_exists(api_id, region):
            issues["api_not_found"].append(api_id)
            verification_results.append(
                {
                    "api_id": api_id,
                    "stage": stage,
                    "status": "API_NOT_FOUND",
                    "message": "API does not exist in API Gateway",
                }
            )
            continue

        # Verify attachment
        result = verify_api_attachment(api_id, stage, api["expected_plan"], region)
        verification_results.append(result)

        if result["status"] == "NOT_ATTACHED":
            issues["not_attached"].append(result)
        elif result["status"] == "WRONG_PLAN":
            issues["wrong_plan"].append(result)
        elif result["status"] == "MULTIPLE":
            issues["multiple_plans"].append(result)

    # Find orphaned APIs (in plans but not tracked)
    tracked_keys = {f"{api['api_id']}:{api['stage']}" for api in expected_apis}
    orphaned = []
    for api_key, plans in actual_attachments.items():
        if api_key not in tracked_keys:
            api_id, stage = api_key.split(":", 1)
            orphaned.append(
                {
                    "api_id": api_id,
                    "stage": stage,
                    "plans": plans,
                }
            )

    # Output results
    if output_json:
        output = {
            "verification_results": verification_results,
            "issues": issues,
            "orphaned": orphaned,
            "summary": {
                "total_tracked": len(expected_apis),
                "correct": len([r for r in verification_results if r.get("status") == "CORRECT"]),
                "issues": sum(len(v) for v in issues.values()),
                "orphaned": len(orphaned),
            },
        }
        click.echo(json.dumps(output, indent=2, default=str))
    else:
        # Pretty print results
        click.echo(f"\n{'=' * 80}")
        click.echo(click.style("API Attachment Verification Report", bold=True))
        click.echo(f"{'=' * 80}")

        # Summary
        total = len(expected_apis)
        correct = len([r for r in verification_results if r.get("status") == "CORRECT"])

        click.echo("\n📊 Summary:")
        click.echo(f"  • Total tracked APIs: {total}")
        click.echo(f"  • Correctly attached: {click.style(str(correct), fg='green')}")
        click.echo(
            f"  • Issues found: {click.style(str(sum(len(v) for v in issues.values())), fg='yellow' if issues else 'green')}"
        )
        click.echo(
            f"  • Orphaned APIs: {click.style(str(len(orphaned)), fg='yellow' if orphaned else 'green')}"
        )

        # Issues detail
        if any(issues.values()):
            click.echo("\n⚠️  Issues Found:")

            if issues["api_not_found"]:
                click.echo(f"\n  {click.style('APIs Not Found:', fg='red')}")
                for api_id in issues["api_not_found"]:
                    click.echo(f"    • {api_id}")

            if issues["not_attached"]:
                click.echo(f"\n  {click.style('Not Attached:', fg='yellow')}")
                for result in issues["not_attached"]:
                    click.echo(f"    • {result['api_id']} ({result['stage']})")

            if issues["wrong_plan"]:
                click.echo(f"\n  {click.style('Wrong Plan:', fg='yellow')}")
                for result in issues["wrong_plan"]:
                    click.echo(f"    • {result['api_id']} ({result['stage']}): {result['message']}")

            if issues["multiple_plans"]:
                click.echo(f"\n  {click.style('Multiple Plans:', fg='yellow')}")
                for result in issues["multiple_plans"]:
                    click.echo(f"    • {result['api_id']} ({result['stage']}): {result['message']}")

        if orphaned:
            click.echo("\n🔍 Orphaned APIs (not tracked):")
            for api in orphaned:
                click.echo(f"  • {api['api_id']} ({api['stage']}) in {', '.join(api['plans'])}")

        # Fix option
        if fix and any(issues.values()):
            click.echo("\n🔧 Fix mode enabled")
            click.echo("Would attempt to fix the following:")
            click.echo(f"  • Attach {len(issues['not_attached'])} unattached APIs")
            click.echo(f"  • Move {len(issues['wrong_plan'])} APIs to correct plans")

            if click.confirm("\nProceed with fixes?"):
                # Implementation would go here
                click.echo("Fix implementation pending...")

        # Final status
        click.echo(f"\n{'=' * 80}")
        if not any(issues.values()) and not orphaned:
            click.echo(click.style("✅ All APIs are correctly configured!", fg="green", bold=True))
        else:
            click.echo(
                click.style(f"⚠️  Found {sum(len(v) for v in issues.values())} issues", fg="yellow")
            )
            if fix:
                click.echo("\nRun with --fix to attempt automatic correction")


__all__ = ["verify"]
