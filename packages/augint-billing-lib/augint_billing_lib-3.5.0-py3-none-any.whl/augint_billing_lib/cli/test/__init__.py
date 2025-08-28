"""Testing commands separated by capability."""

import click

from augint_billing_lib.cli.test.integration import integration_group
from augint_billing_lib.cli.test.simulate import simulate_group
from augint_billing_lib.cli.test.stripe import stripe_group


@click.group(
    name="test",
    help="""
    Test commands for the billing system.

    IMPORTANT: Test commands are divided into three categories:

    1. stripe/      - Test Stripe integration only (no API keys)
       • Creates Stripe test customers
       • Tests webhook delivery
       • Tests EventBridge configuration
       • CANNOT test promotion or usage tracking

    2. integration/ - Test complete billing flow (requires REAL API keys)
       • Links existing API keys to Stripe
       • Generates real API traffic
       • Tests full billing cycles
       • Requires actual API keys from your application

    3. simulate/    - Educational simulation (no real resources)
       • Shows how the system works
       • Simulates complete flows
       • No actual API calls or state changes
       • Perfect for learning and understanding

    Most users should start with 'simulate' commands to understand the flow,
    then use 'integration' commands with real API keys for actual testing.

    ⚠️  CRITICAL: Test customers created in Stripe DO NOT have API keys.
    API keys are created by API Gateway when users sign up through your app.
    """,
)
def test_group() -> None:
    """Test command group."""


# Add subgroups
test_group.add_command(stripe_group)
test_group.add_command(integration_group)
test_group.add_command(simulate_group)


__all__ = ["test_group"]
