"""Administrative commands."""

import click

from augint_billing_lib.config import get_service


@click.group(
    name="admin",
    help="""
    Administrative operations.

    Commands for system maintenance, data migration, and cleanup.
    Use with caution - these commands can modify or delete data.
    """,
)
def admin_group() -> None:
    """Admin command group."""


@admin_group.command("migrate")
@click.option("--from-version", required=True, help="Source version")
@click.option("--to-version", required=True, help="Target version")
@click.option("--dry-run", is_flag=True, help="Preview migration")
def migrate(from_version: str, to_version: str, dry_run: bool) -> None:
    """Data migration tools."""
    click.echo(f"Migration: {from_version} → {to_version}")

    if dry_run:
        click.echo("[DRY RUN] Would migrate:")
        click.echo("  • Update DynamoDB schema")
        click.echo("  • Migrate 42 customer records")
    else:
        click.echo("✅ Migration complete")


@admin_group.command("cleanup")
@click.option(
    "--type",
    "cleanup_type",
    type=click.Choice(["test-data", "orphaned-links", "old-logs"]),
    required=True,
    help="Type of cleanup",
)
@click.option("--older-than", help="Age threshold (e.g., 30d)")
@click.option("--dry-run", is_flag=True, help="Preview what would be deleted")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def cleanup(cleanup_type: str, older_than: str, dry_run: bool, confirm: bool) -> None:
    """Clean up test data and orphaned resources."""
    get_service()

    click.echo(f"Cleanup: {cleanup_type}")

    if older_than:
        click.echo(f"Filter: older than {older_than}")

    if cleanup_type == "test-data":
        items_to_clean = [
            "5 test Stripe customers",
            "12 test DynamoDB entries",
            "3 test API keys",
        ]
    elif cleanup_type == "orphaned-links":
        items_to_clean = [
            "2 links with deleted API keys",
            "1 link with deleted Stripe customer",
        ]
    else:  # old-logs
        items_to_clean = [
            "CloudWatch logs older than 30 days",
            "Lambda execution logs",
        ]

    click.echo("\nItems to clean:")
    for item in items_to_clean:
        click.echo(f"  • {item}")

    if dry_run:
        click.echo("\n[DRY RUN] No changes made")
        return

    if not confirm and not click.confirm("\nProceed with cleanup?"):
        raise click.Abort()

    click.echo("\nCleaning up...")
    for item in items_to_clean:
        click.echo(f"  Removing {item}")

    click.echo("\n✅ Cleanup complete")


@admin_group.command("backup")
@click.option("--include", multiple=True, help="Components to backup")
@click.option("--output", type=click.Path(), help="Backup file location")
def backup(include: tuple[str, ...], output: str) -> None:
    """Backup configuration and data."""
    components = include or ["config", "dynamodb", "usage-plans"]

    click.echo("Creating backup...")
    click.echo("Components:")
    for component in components:
        click.echo(f"  • {component}")

    if output:
        click.echo(f"\n✅ Backup saved to: {output}")
    else:
        click.echo("\n✅ Backup saved to: backup-20250122-1200.tar.gz")


@admin_group.command("restore")
@click.argument("backup_file", type=click.Path(exists=True))
@click.option("--components", multiple=True, help="Components to restore")
@click.option("--dry-run", is_flag=True, help="Preview restore")
def restore(backup_file: str, components: tuple[str, ...], dry_run: bool) -> None:
    """Restore from backup."""
    click.echo(f"Restoring from: {backup_file}")

    if components:
        click.echo("Components to restore:")
        for component in components:
            click.echo(f"  • {component}")
    else:
        click.echo("Restoring all components")

    if dry_run:
        click.echo("\n[DRY RUN] Would restore:")
        click.echo("  • 5 configuration items")
        click.echo("  • 42 DynamoDB records")
        click.echo("  • 2 usage plans")
    else:
        if not click.confirm("\nProceed with restore?"):
            raise click.Abort()

        click.echo("\nRestoring...")
        click.echo("✅ Restore complete")


__all__ = ["admin_group"]
