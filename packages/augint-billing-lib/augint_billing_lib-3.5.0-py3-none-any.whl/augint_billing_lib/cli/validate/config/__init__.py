"""Configuration validation commands."""

import click

from augint_billing_lib.cli.validate.config.check import check


@click.group(name="config", help="Configuration validation")
def config_group() -> None:
    """Config validation group."""


config_group.add_command(check)

__all__ = ["config_group"]
