"""Check infrastructure status."""

import json
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


def get_stack_outputs(stack_name: str, region: str) -> dict[str, str]:
    """Get CloudFormation stack outputs."""
    cfn = boto3.client("cloudformation", region_name=region)

    try:
        response = cfn.describe_stacks(StackName=stack_name)
        stack = response["Stacks"][0]

        outputs = {}
        for output in stack.get("Outputs", []):
            outputs[output["OutputKey"]] = output["OutputValue"]

        return outputs
    except ClientError as e:
        if "does not exist" in str(e):
            raise click.ClickException(f"Stack '{stack_name}' not found in region {region}")
        raise


def check_lambda_status(function_name: str, region: str) -> dict[str, Any]:
    """Check Lambda function status."""
    lambda_client = boto3.client("lambda", region_name=region)

    try:
        response = lambda_client.get_function(FunctionName=function_name)
        config = response["Configuration"]

        return {
            "exists": True,
            "state": config.get("State", "Unknown"),
            "runtime": config.get("Runtime", "Unknown"),
            "last_modified": config.get("LastModified", "Unknown"),
            "memory": config.get("MemorySize", 0),
            "timeout": config.get("Timeout", 0),
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return {"exists": False}
        raise


def check_eventbridge_rule(rule_name: str, region: str) -> dict[str, Any]:
    """Check EventBridge rule status."""
    events = boto3.client("events", region_name=region)

    try:
        response = events.describe_rule(Name=rule_name)

        return {
            "exists": True,
            "state": response.get("State", "Unknown"),
            "schedule": response.get("ScheduleExpression", "N/A"),
            "description": response.get("Description", ""),
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return {"exists": False}
        raise


def check_usage_plans(region: str) -> list[dict[str, Any]]:
    """Check API Gateway usage plans."""
    apigw = boto3.client("apigateway", region_name=region)

    plans = []
    try:
        response = apigw.get_usage_plans()

        for plan in response.get("items", []):
            plan_info = {
                "id": plan["id"],
                "name": plan["name"],
                "api_stages": len(plan.get("apiStages", [])),
                "quota": plan.get("quota", {}),
                "throttle": plan.get("throttle", {}),
            }

            # Get API key count for this plan
            keys_response = apigw.get_usage_plan_keys(usagePlanId=plan["id"], limit=500)
            plan_info["api_keys"] = len(keys_response.get("items", []))

            plans.append(plan_info)
    except ClientError as e:
        click.echo(f"Warning: Could not fetch usage plans: {e}", err=True)

    return plans


def check_dlq_depth(queue_url: str, region: str) -> int:
    """Check DLQ message count."""
    sqs = boto3.client("sqs", region_name=region)

    try:
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )
        return int(response["Attributes"]["ApproximateNumberOfMessages"])
    except ClientError:
        return -1  # Indicates error


@click.command("status")
@click.option("--stack-name", envvar="STACK_NAME", help="CloudFormation stack name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def status(stack_name: str | None, region: str, output_json: bool) -> None:
    """
    Check infrastructure stack status.

    Shows the status of:
    - CloudFormation stack
    - Lambda functions (discovery, stripe-handler, usage-reporter)
    - EventBridge rules and their states
    - Usage plans and attached API count
    - DLQ depths (if configured)

    Example:
        ai-billing infra status
        ai-billing infra status --stack-name my-billing-stack
        ai-billing infra status --json
    """
    if not stack_name:
        click.echo(
            click.style("Error: Stack name required. Set STACK_NAME or use --stack-name", fg="red"),
            err=True,
        )
        raise click.Abort()

    status_data: dict[str, Any] = {
        "stack": {
            "name": stack_name,
            "region": region,
        },
        "lambdas": {},
        "eventbridge_rules": {},
        "usage_plans": [],
        "dlqs": {},
    }

    # Get stack outputs
    try:
        outputs = get_stack_outputs(stack_name, region)
        status_data["stack"]["outputs"] = outputs
        status_data["stack"]["status"] = "ACTIVE"
    except click.ClickException:
        status_data["stack"]["status"] = "NOT_FOUND"
        if output_json:
            click.echo(json.dumps(status_data, indent=2))
        else:
            click.echo(click.style(f"❌ Stack '{stack_name}' not found", fg="red"))
        return

    # Check Lambda functions
    lambda_functions = {
        "api-discovery": f"{stack_name}-api-discovery",
        "stripe-handler": f"{stack_name}-stripe-handler",
        "usage-reporter": f"{stack_name}-usage-reporter",
    }

    for name, function_name in lambda_functions.items():
        # Try to get from stack outputs first
        output_key = f"{name.replace('-', '_')}_function"
        if output_key in outputs:
            function_name = outputs[output_key]

        status_data["lambdas"][name] = check_lambda_status(function_name, region)

    # Check EventBridge rules
    rules = {
        "discovery": f"{stack_name}-ApiDiscoveryEveryFiveMinutesRule",
        "usage": f"{stack_name}-HourlyUsageReportingRule",
        "stripe": f"{stack_name}-StripeEventProcessorRule",
    }

    for name, rule_name in rules.items():
        status_data["eventbridge_rules"][name] = check_eventbridge_rule(rule_name, region)

    # Check usage plans
    status_data["usage_plans"] = check_usage_plans(region)

    # Output results
    if output_json:
        click.echo(json.dumps(status_data, indent=2))
    else:
        # Pretty print status
        click.echo(f"\n{'=' * 60}")
        click.echo(click.style(f"Infrastructure Status: {stack_name}", bold=True))
        click.echo(f"{'=' * 60}")

        # Stack status
        click.echo(f"\n📚 Stack: {status_data['stack']['status']}")

        # Lambda status
        click.echo("\n🔧 Lambda Functions:")
        for name, info in status_data["lambdas"].items():
            if info.get("exists"):
                state_color = "green" if info["state"] == "Active" else "yellow"
                click.echo(
                    f"  • {name}: "
                    f"{click.style(info['state'], fg=state_color)} "
                    f"(Memory: {info['memory']}MB, Timeout: {info['timeout']}s)"
                )
            else:
                click.echo(f"  • {name}: {click.style('NOT FOUND', fg='red')}")

        # EventBridge status
        click.echo("\n⏰ EventBridge Rules:")
        for name, info in status_data["eventbridge_rules"].items():
            if info.get("exists"):
                state_color = "green" if info["state"] == "ENABLED" else "yellow"
                click.echo(
                    f"  • {name}: {click.style(info['state'], fg=state_color)} ({info['schedule']})"
                )
            else:
                click.echo(f"  • {name}: {click.style('NOT FOUND', fg='red')}")

        # Usage plans
        click.echo("\n📊 Usage Plans:")
        for plan in status_data["usage_plans"]:
            click.echo(
                f"  • {plan['name']} ({plan['id']}): "
                f"{plan['api_stages']} stages, {plan['api_keys']} keys"
            )

        click.echo(f"\n{'=' * 60}\n")


__all__ = ["status"]
