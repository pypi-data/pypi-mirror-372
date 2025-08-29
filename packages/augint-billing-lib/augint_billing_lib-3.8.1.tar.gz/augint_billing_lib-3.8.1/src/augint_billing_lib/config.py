"""Configuration module for the CLI."""

import os
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv

# Load .env at module import time so CLI commands work without exported vars
# In Lambda, this is a no-op since env vars are already set
load_dotenv()

if TYPE_CHECKING:
    from augint_billing_lib.service import BillingService


class Config:
    """Configuration from environment variables."""

    def __init__(self) -> None:
        """Initialize configuration from environment."""
        self.stack_name = os.environ.get("STACK_NAME", "")
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.table_name = os.environ.get("TABLE_NAME", "")
        self.free_usage_plan_id = os.environ.get("FREE_USAGE_PLAN_ID", "FREE_10K")
        self.metered_usage_plan_id = os.environ.get("METERED_USAGE_PLAN_ID", "METERED")
        self.api_usage_product_id = os.environ.get("API_USAGE_PRODUCT_ID", "")
        self.stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY", "")
        self.stripe_secret_arn = os.environ.get("STRIPE_SECRET_ARN", "")
        self.metered_price_id = os.environ.get("STRIPE_PRICE_ID_METERED", "")

    def is_configured(self) -> bool:
        """Check if minimum configuration is present."""
        return bool(
            self.stack_name and self.region and (self.stripe_secret_key or self.stripe_secret_arn)
        )


# Global config instance
config = Config()


class ServiceWrapper:
    """Wrapper to provide access to service and config."""

    def __init__(self, service: "BillingService", config_obj: Config):
        """Initialize wrapper."""
        self._service = service
        self.config = config_obj
        # Expose service attributes
        self.customer_repo = getattr(service, "_repo", None)
        self.plan_admin = getattr(service, "_plan_admin", None)

    def __getattr__(self, name: str) -> Any:
        """Delegate to the underlying service."""
        return getattr(self._service, name)


def get_service() -> Any:
    """Get or create a BillingService instance wrapped with config access."""
    from augint_billing_lib.bootstrap import build_service

    global config

    # Ensure environment is configured
    if not config.stack_name:
        # Try to load from .env file
        from dotenv import load_dotenv

        load_dotenv()
        # Reinitialize config after loading .env
        config = Config()

    service = build_service()
    return ServiceWrapper(service, config)
