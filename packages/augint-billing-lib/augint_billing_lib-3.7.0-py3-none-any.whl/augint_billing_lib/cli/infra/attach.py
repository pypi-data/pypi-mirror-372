"""Emergency API attachment to usage plans."""

import boto3
import click
from botocore.exceptions import ClientError


def attach_api_to_plan(api_id: str, stage: str, usage_plan_id: str, region: str) -> bool:
    """Attach an API stage to a usage plan."""
    apigw = boto3.client("apigateway", region_name=region)

    try:
        apigw.update_usage_plan(
            usagePlanId=usage_plan_id,
            patchOperations=[{"op": "add", "path": "/apiStages", "value": f"{api_id}:{stage}"}],
        )
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "ConflictException":
            click.echo(f"⚠️  API {api_id} stage {stage} is already attached", err=True)
            return False
        if error_code == "NotFoundException":
            click.echo(f"❌ Usage plan {usage_plan_id} not found", err=True)
            return False
        click.echo(f"❌ Error attaching API: {e}", err=True)
        return False


@click.command("attach")
@click.option("--api-id", required=True, help="API Gateway REST API ID")
@click.option("--stage", required=True, help="API stage name")
@click.option(
    "--plan", type=click.Choice(["free", "metered"]), required=True, help="Usage plan type"
)
@click.option("--region", envvar="AWS_REGION", default="us-east-1", help="AWS region")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.option("--free-plan-id", envvar="FREE_USAGE_PLAN_ID", help="Free usage plan ID")
@click.option("--metered-plan-id", envvar="METERED_USAGE_PLAN_ID", help="Metered usage plan ID")
def attach(
    api_id: str,
    stage: str,
    plan: str,
    region: str,
    force: bool,
    free_plan_id: str | None,
    metered_plan_id: str | None,
) -> None:
    """
    Emergency: Manually attach an API to a usage plan.

    This is an EMERGENCY OPERATION that bypasses the automatic discovery
    process. Use only when automatic attachment has failed.

    The automatic discovery process should handle API attachments.
    This command is for emergency recovery situations only.

    Example:
        ai-billing infra attach --api-id abc123 --stage prod --plan free
        ai-billing infra attach --api-id xyz789 --stage v1 --plan metered --force
    """
    # Determine usage plan ID
    usage_plan_id = free_plan_id or "FREE_10K" if plan == "free" else metered_plan_id or "METERED"

    # Confirmation prompt
    if not force:
        click.echo(
            click.style(
                "⚠️  WARNING: This is an emergency operation that bypasses automatic discovery.",
                fg="yellow",
                bold=True,
            )
        )
        click.echo("\nYou are about to attach:")
        click.echo(f"  API: {api_id}")
        click.echo(f"  Stage: {stage}")
        click.echo(f"  Usage Plan: {usage_plan_id} ({plan})")
        click.echo(f"  Region: {region}")

        if not click.confirm("\nDo you want to proceed?"):
            click.echo("Aborted.")
            return

    # Perform attachment
    click.echo(f"\n🔗 Attaching API {api_id} stage {stage} to {usage_plan_id}...")

    if attach_api_to_plan(api_id, stage, usage_plan_id, region):
        click.echo(
            click.style(
                f"✅ Successfully attached API {api_id} stage {stage} to {usage_plan_id}",
                fg="green",
            )
        )
    else:
        raise click.ClickException("Failed to attach API to usage plan")


__all__ = ["attach"]
