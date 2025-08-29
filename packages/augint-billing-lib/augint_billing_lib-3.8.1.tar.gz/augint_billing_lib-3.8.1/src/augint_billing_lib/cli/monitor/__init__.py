"""Monitoring commands."""

import click

from augint_billing_lib.cli.monitor.dashboard import dashboard


@click.group(
    name="monitor",
    help="""
    Monitor Zero-Touch operations.

    Real-time monitoring of API discovery, attachment, and usage reporting.

    Commands:
    • dashboard - Real-time monitoring dashboard

    Use these commands to observe the automatic processes and verify
    that APIs are being discovered and attached correctly.
    """,
)
def monitor_group() -> None:
    """Monitor command group."""


monitor_group.add_command(dashboard)


__all__ = ["monitor_group"]
