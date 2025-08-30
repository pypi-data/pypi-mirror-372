"""Emergency API detachment from usage plans."""

import boto3
import click
from botocore.exceptions import ClientError


def detach_api_from_plan(api_id: str, stage: str, usage_plan_id: str, region: str) -> bool:
    """Detach an API stage from a usage plan."""
    apigw = boto3.client("apigateway", region_name=region)

    try:
        apigw.update_usage_plan(
            usagePlanId=usage_plan_id,
            patchOperations=[{"op": "remove", "path": "/apiStages", "value": f"{api_id}:{stage}"}],
        )
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "NotFoundException":
            click.echo(f"⚠️  API {api_id} stage {stage} not found in plan", err=True)
            return False
        click.echo(f"❌ Error detaching API: {e}", err=True)
        return False


def find_api_in_plans(api_id: str, stage: str, region: str) -> list[str]:
    """Find which usage plans an API is attached to."""
    apigw = boto3.client("apigateway", region_name=region)
    attached_plans = []

    try:
        response = apigw.get_usage_plans()
        for plan in response.get("items", []):
            for api_stage in plan.get("apiStages", []):
                if api_stage["apiId"] == api_id and api_stage.get("stage") == stage:
                    attached_plans.append(plan["id"])
    except ClientError:
        pass

    return attached_plans


@click.command("detach")
@click.option("--api-id", required=True, help="API Gateway REST API ID")
@click.option("--stage", required=True, help="API stage name")
@click.option("--plan-id", help="Specific usage plan ID to detach from")
@click.option("--all", "detach_all", is_flag=True, help="Detach from all usage plans")
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def detach(
    api_id: str,
    stage: str,
    plan_id: str | None,
    detach_all: bool,
    region: str,
    force: bool,
) -> None:
    """
    Emergency: Manually detach an API from usage plans.

    This is an EMERGENCY OPERATION for removing APIs from usage plans
    when automatic management has failed.

    You can either:
    - Detach from a specific plan with --plan-id
    - Detach from all plans with --all
    - Let the command find and prompt for which plans to detach from

    Example:
        ai-billing infra detach --api-id abc123 --stage prod --all
        ai-billing infra detach --api-id xyz789 --stage v1 --plan-id FREE_10K
    """
    # Find current attachments
    attached_plans = find_api_in_plans(api_id, stage, region)

    if not attached_plans:
        click.echo(f"API {api_id} stage {stage} is not attached to any usage plans")
        return

    # Determine which plans to detach from
    if detach_all:
        plans_to_detach = attached_plans
    elif plan_id:
        if plan_id not in attached_plans:
            click.echo(
                click.style(f"❌ API {api_id} stage {stage} is not attached to {plan_id}", fg="red")
            )
            click.echo(f"Currently attached to: {', '.join(attached_plans)}")
            raise click.Abort()
        plans_to_detach = [plan_id]
    else:
        # Interactive selection
        click.echo(f"API {api_id} stage {stage} is attached to:")
        for idx, pid in enumerate(attached_plans, 1):
            click.echo(f"  {idx}. {pid}")

        if len(attached_plans) == 1:
            plans_to_detach = attached_plans
        else:
            choice = click.prompt(
                "Enter plan number to detach from (or 'all' for all plans)", type=str
            )
            if choice.lower() == "all":
                plans_to_detach = attached_plans
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(attached_plans):
                        plans_to_detach = [attached_plans[idx]]
                    else:
                        raise ValueError()
                except (ValueError, IndexError):
                    click.echo("Invalid selection")
                    raise click.Abort()

    # Confirmation prompt
    if not force:
        click.echo(
            click.style("⚠️  WARNING: This is an emergency operation.", fg="yellow", bold=True)
        )
        click.echo("\nYou are about to detach:")
        click.echo(f"  API: {api_id}")
        click.echo(f"  Stage: {stage}")
        click.echo(f"  From plans: {', '.join(plans_to_detach)}")
        click.echo(f"  Region: {region}")

        if not click.confirm("\nDo you want to proceed?"):
            click.echo("Aborted.")
            return

    # Perform detachment
    success_count = 0
    for pid in plans_to_detach:
        click.echo(f"\n🔓 Detaching from {pid}...")
        if detach_api_from_plan(api_id, stage, pid, region):
            click.echo(click.style(f"✅ Detached from {pid}", fg="green"))
            success_count += 1
        else:
            click.echo(click.style(f"❌ Failed to detach from {pid}", fg="red"))

    if success_count == len(plans_to_detach):
        click.echo(
            click.style(f"\n✅ Successfully detached API from {success_count} plan(s)", fg="green")
        )
    elif success_count > 0:
        click.echo(
            click.style(
                f"\n⚠️  Partially successful: detached from {success_count}/{len(plans_to_detach)} plans",
                fg="yellow",
            )
        )
    else:
        raise click.ClickException("Failed to detach API from any plans")


__all__ = ["detach"]
