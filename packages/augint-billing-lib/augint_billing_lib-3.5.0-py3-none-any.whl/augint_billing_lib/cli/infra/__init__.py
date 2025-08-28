"""Infrastructure management commands for Zero-Touch architecture."""

import click

from augint_billing_lib.cli.infra.attach import attach
from augint_billing_lib.cli.infra.detach import detach
from augint_billing_lib.cli.infra.list import list_apis
from augint_billing_lib.cli.infra.pause import pause
from augint_billing_lib.cli.infra.resume import resume
from augint_billing_lib.cli.infra.status import status
from augint_billing_lib.cli.infra.trigger import trigger_discovery
from augint_billing_lib.cli.infra.verify import verify


@click.group(
    name="infra",
    help="""
    Infrastructure management commands for Zero-Touch architecture.

    These commands help you manage and monitor the infrastructure stack
    that automatically discovers and attaches APIs to usage plans.

    Commands:
    • status           - Check infrastructure status
    • trigger-discovery - Manually trigger API discovery
    • list-apis        - List discovered APIs
    • verify           - Verify API attachments
    • attach           - Emergency manual attachment
    • detach           - Remove API from plans
    • pause            - Pause auto-discovery
    • resume           - Resume auto-discovery

    NOTE: Manual attachment/detachment should only be used in emergency
    situations. The Zero-Touch architecture handles this automatically.
    """,
)
def infra_group() -> None:
    """Infrastructure command group."""


infra_group.add_command(status)
infra_group.add_command(trigger_discovery)
infra_group.add_command(list_apis)
infra_group.add_command(attach)
infra_group.add_command(detach)
infra_group.add_command(pause)
infra_group.add_command(resume)
infra_group.add_command(verify)


__all__ = ["infra_group"]
