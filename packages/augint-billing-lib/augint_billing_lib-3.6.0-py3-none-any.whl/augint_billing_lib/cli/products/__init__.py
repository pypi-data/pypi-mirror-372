"""Stripe product management commands."""

import click

from augint_billing_lib.cli.products.diagnose import diagnose_setup
from augint_billing_lib.cli.products.list_products import list_products
from augint_billing_lib.cli.products.setup import setup_products
from augint_billing_lib.cli.products.show import show_product
from augint_billing_lib.cli.products.verify import verify_products


@click.group(
    name="products",
    help="""
    Stripe product and price management.

    These commands help you create and manage Stripe products and prices
    for your billing infrastructure. Products must be properly configured
    in Stripe before the billing system can function.

    Commands:
    • setup   - Create/update products for an environment
    • verify  - Verify existing products are configured correctly
    • list    - List products in Stripe account
    • show    - Show detailed information about a product
    • diagnose - Diagnose Stripe connection and configuration issues

    Example workflow:
      1. ai-billing products setup staging --model subscription-plus-metered
      2. ai-billing products verify staging
      3. Deploy infrastructure with product IDs from .env
    """,
)
def products_group() -> None:
    """Products command group."""


products_group.add_command(setup_products)
products_group.add_command(verify_products)
products_group.add_command(list_products)
products_group.add_command(show_product)
products_group.add_command(diagnose_setup)


__all__ = ["products_group"]
