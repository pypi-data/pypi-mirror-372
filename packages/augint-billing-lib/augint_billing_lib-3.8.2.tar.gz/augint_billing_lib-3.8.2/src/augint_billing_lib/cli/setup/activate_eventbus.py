"""Activate AWS partner event source from Stripe."""

import json
import sys

import boto3
import click

from augint_billing_lib.config import config


@click.command("activate-eventbus")
@click.option(
    "--partner-event-source",
    help="Partner event source name (auto-detect if not specified)",
)
@click.option(
    "--event-bus-name",
    help="Custom event bus name (optional)",
)
@click.option(
    "--create-rules",
    is_flag=True,
    default=True,
    help="Create default rules for Lambda targets",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def activate_eventbus(
    partner_event_source: str | None,
    event_bus_name: str | None,
    create_rules: bool,
    dry_run: bool,
) -> None:
    """
    Activate the AWS partner event source created by Stripe.

    This command activates the Stripe partner event source in EventBridge
    and optionally creates rules to route events to Lambda functions.

    Example:
        ai-billing setup activate-eventbus
    """
    if dry_run:
        click.echo(
            click.style(
                "🔍 DRY RUN - No changes will be made",
                fg="yellow",
                bold=True,
            )
        )

    try:
        events = boto3.client("events", region_name=config.region)

        # List partner event sources
        click.echo("Searching for Stripe partner event sources...")
        sources = events.list_event_sources(NamePrefix="aws.partner/stripe.com")

        if not sources.get("EventSources"):
            click.echo(
                click.style(
                    "❌ No Stripe partner event sources found",
                    fg="red",
                )
            )
            click.echo("\nMake sure you have:")
            click.echo("1. Configured EventBridge in Stripe Dashboard")
            click.echo("2. Used the correct AWS account ID")
            click.echo("3. Used the correct AWS region")
            sys.exit(1)

        # Select event source
        if partner_event_source:
            source = None
            for s in sources["EventSources"]:
                if s["Name"] == partner_event_source:
                    source = s
                    break
            if not source:
                click.echo(
                    click.style(
                        f"❌ Partner event source '{partner_event_source}' not found",
                        fg="red",
                    )
                )
                sys.exit(1)
        else:
            # Auto-detect - use the first one
            source = sources["EventSources"][0]
            if len(sources["EventSources"]) > 1:
                click.echo(f"⚠️  Multiple sources found, using: {source['Name']}")

        click.echo(f"Found partner event source: {source['Name']}")
        click.echo(f"State: {source['State']}")
        click.echo(f"ARN: {source['Arn']}")

        # Check if already active
        if source["State"] == "ACTIVE":
            click.echo(
                click.style(
                    "✅ Partner event source is already active",
                    fg="green",
                )
            )
            # Get the event bus name
            if not event_bus_name:
                # The event bus name is typically the same as the source name
                event_bus_name = source["Name"]
        # Activate the source
        elif dry_run:
            click.echo("Would activate partner event source")
            event_bus_name = event_bus_name or source["Name"]
        else:
            click.echo("Activating partner event source...")

            # Create event bus with activation
            if not event_bus_name:
                event_bus_name = source["Name"]

            events.create_event_bus(
                Name=event_bus_name,
                EventSourceName=source["Name"],
            )

            click.echo(
                click.style(
                    f"✅ Activated event source with bus: {event_bus_name}",
                    fg="green",
                )
            )

        # Create rules if requested
        if create_rules:
            click.echo("\nCreating EventBridge rules...")

            # Define default rules
            rules = [
                {
                    "name": f"{config.stack_name}-stripe-events",
                    "description": "Route Stripe events to Lambda",
                    "event_pattern": {
                        "source": ["stripe.com"],
                    },
                },
            ]

            for rule_def in rules:
                rule_name = rule_def["name"]

                if dry_run:
                    click.echo(f"Would create rule: {rule_name}")
                else:
                    try:
                        # Create or update rule
                        events.put_rule(
                            Name=rule_name,
                            EventBusName=event_bus_name,
                            EventPattern=json.dumps(rule_def["event_pattern"]),
                            Description=rule_def["description"],
                            State="ENABLED",
                        )
                        click.echo(f"✅ Created rule: {rule_name}")

                        # Note: Adding Lambda targets requires the Lambda ARN
                        # which should be done after infrastructure deployment
                        click.echo(
                            click.style(
                                "  ⚠️  Remember to add Lambda target after deployment",
                                fg="yellow",
                            )
                        )

                    except Exception as e:
                        click.echo(
                            click.style(
                                f"  ⚠️  Could not create rule: {e}",
                                fg="yellow",
                            )
                        )

        # Summary
        click.echo("\n" + "=" * 50)
        click.echo(click.style("EventBridge Setup Complete!", fg="green", bold=True))
        click.echo(f"Event Bus: {event_bus_name}")
        click.echo(f"Partner Source: {source['Name']}")

        click.echo(
            click.style(
                "\n📝 Next Steps:",
                fg="cyan",
                bold=True,
            )
        )
        click.echo("1. Deploy Lambda functions for event processing")
        click.echo("2. Add Lambda targets to EventBridge rules")
        click.echo("3. Test with: ai-billing test stripe event")
        click.echo("4. Monitor CloudWatch Logs for Lambda execution")

    except boto3.exceptions.Boto3Error as e:
        click.echo(
            click.style(f"❌ AWS error: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(
            click.style(f"❌ Error: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)


__all__ = ["activate_eventbus"]
