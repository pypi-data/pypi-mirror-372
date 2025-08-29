"""Manually trigger API discovery."""

import json
import time
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


def invoke_discovery_lambda(
    function_name: str, region: str, wait: bool = False, show_output: bool = False
) -> dict[str, Any]:
    """Invoke the API discovery Lambda function."""
    lambda_client = boto3.client("lambda", region_name=region)

    try:
        # Invoke the function
        invocation_type = "RequestResponse" if wait else "Event"

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps({"source": "manual-trigger", "timestamp": int(time.time())}),
        )

        result = {
            "status_code": response["StatusCode"],
            "request_id": response.get("ResponseMetadata", {}).get("RequestId"),
        }

        if wait and "Payload" in response:
            payload = json.loads(response["Payload"].read())
            result["response"] = payload

            if show_output:
                click.echo("\nLambda Response:")
                click.echo(json.dumps(payload, indent=2))

        return result

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise click.ClickException(f"Lambda function '{function_name}' not found")
        raise click.ClickException(f"Failed to invoke Lambda: {e}")


def get_discovery_lambda_name(stack_name: str, region: str) -> str:
    """Get the discovery Lambda function name from stack outputs."""
    cfn = boto3.client("cloudformation", region_name=region)

    try:
        response = cfn.describe_stacks(StackName=stack_name)
        stack = response["Stacks"][0]

        # Look for the discovery Lambda in outputs
        for output in stack.get("Outputs", []):
            if "Discovery" in output["OutputKey"] and "Function" in output["OutputKey"]:
                return str(output["OutputValue"])

        # Fallback to conventional naming
        return f"{stack_name}-api-discovery"

    except ClientError:
        # Fallback to conventional naming
        return f"{stack_name}-api-discovery"


@click.command("trigger-discovery")
@click.option("--stack-name", envvar="STACK_NAME", help="CloudFormation stack name")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--wait", is_flag=True, help="Wait for completion")
@click.option("--show-output", is_flag=True, help="Display Lambda response")
@click.option("--function-name", help="Override Lambda function name")
def trigger_discovery(
    stack_name: str | None,
    region: str,
    wait: bool,
    show_output: bool,
    function_name: str | None,
) -> None:
    """
    Manually trigger the API discovery Lambda.

    This command invokes the ApiDiscovery Lambda function in the infrastructure
    stack, which will scan for APIs and attach them to the appropriate usage plans.

    Options:
    - --wait: Wait for the Lambda to complete and show results
    - --show-output: Display the full Lambda response (requires --wait)

    Example:
        ai-billing infra trigger-discovery
        ai-billing infra trigger-discovery --wait --show-output
        ai-billing infra trigger-discovery --stack-name my-stack
    """
    if not stack_name:
        click.echo(
            click.style("Error: Stack name required. Set STACK_NAME or use --stack-name", fg="red"),
            err=True,
        )
        raise click.Abort()

    # Determine Lambda function name
    if not function_name:
        function_name = get_discovery_lambda_name(stack_name, region)

    click.echo(f"🔍 Triggering API discovery Lambda: {function_name}")

    if not wait:
        click.echo("   (Running asynchronously, use --wait to see results)")

    try:
        result = invoke_discovery_lambda(function_name, region, wait, show_output)

        if result["status_code"] == 202:
            click.echo(
                click.style(
                    f"✅ Discovery triggered successfully (Request ID: {result['request_id']})",
                    fg="green",
                )
            )

            if not wait:
                click.echo("\nTo monitor progress, use:")
                click.echo("  ai-billing monitor discovery --since 1m")

        elif result["status_code"] == 200 and wait:
            response = result.get("response", {})

            if response.get("statusCode") == 200:
                body = json.loads(response.get("body", "{}"))

                click.echo(click.style("\n✅ Discovery completed successfully!", fg="green"))

                if "discovered" in body:
                    click.echo(f"\nDiscovered APIs: {body['discovered']}")
                if "attached" in body:
                    click.echo(f"Attached to plans: {body['attached']}")
                if body.get("errors"):
                    click.echo(
                        click.style(f"\nErrors encountered: {len(body['errors'])}", fg="yellow")
                    )
                    for error in body["errors"][:5]:  # Show first 5 errors
                        click.echo(f"  • {error}")
            else:
                click.echo(
                    click.style(
                        f"⚠️  Discovery completed with status: {response.get('statusCode')}",
                        fg="yellow",
                    )
                )
        else:
            click.echo(
                click.style(f"⚠️  Unexpected status code: {result['status_code']}", fg="yellow")
            )

    except click.ClickException:
        raise
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        raise click.Abort()


__all__ = ["trigger_discovery"]
