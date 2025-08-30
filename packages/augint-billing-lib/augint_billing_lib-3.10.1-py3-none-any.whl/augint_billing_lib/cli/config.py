"""Hierarchical configuration management for Augint CLI.

Configuration precedence (highest to lowest):
1. Command-line arguments
2. Environment variables
3. ./.env (current directory)
4. ~/.augint/.env (user config)
5. Default values

Environment-specific prefixes:
- staging: STAGING_
- production: PROD_
- default: no prefix
"""

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values


class CliConfig:
    """Manages hierarchical configuration for the CLI."""

    def __init__(self, environment: str | None = None):
        """Initialize configuration.

        Args:
            environment: The target environment (staging, production, or None for default)
        """
        self.environment = environment
        self.config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from all sources in precedence order."""
        # Start with OS environment variables
        self.config = dict(os.environ)

        # Layer 1: User global config (~/.augint/.env)
        user_config_path = Path.home() / ".augint" / ".env"
        if user_config_path.exists():
            user_config = dotenv_values(user_config_path)
            # Merge, with user config overriding OS env
            self.config.update(user_config)

        # Layer 2: Local project config (./.env)
        # Use the actual current working directory, not the Poetry project directory
        local_config_path = Path.cwd() / ".env"
        if local_config_path.exists():
            local_config = dotenv_values(local_config_path)
            # Merge, with local config overriding previous
            self.config.update(local_config)

        # Note: Command-line args are handled by the calling code
        # since they're passed directly to functions

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a configuration value with environment-specific prefixes.

        Args:
            key: The configuration key (without environment prefix)
            default: Default value if not found

        Returns:
            The configuration value or default

        Examples:
            >>> config = CliConfig(environment="staging")
            >>> config.get("STRIPE_SECRET_KEY")
            # First tries: STAGING_STRIPE_SECRET_KEY
            # Falls back to: STRIPE_SECRET_KEY
            # Returns default if neither found
        """
        # If we have an environment, try the prefixed version first
        if self.environment:
            prefix = self._get_prefix()
            prefixed_key = f"{prefix}{key}"
            if prefixed_key in self.config:
                value = self.config[prefixed_key]
                return str(value) if value is not None else None

        # Fall back to non-prefixed key
        if key in self.config:
            value = self.config[key]
            return str(value) if value is not None else None

        return default

    def _get_prefix(self) -> str:
        """Get the environment prefix."""
        if self.environment == "staging":
            return "STAGING_"
        if self.environment == "production":
            return "PROD_"
        return ""

    def get_stripe_key(self) -> str | None:
        """Get the Stripe API key for the current environment."""
        # Try multiple variations in order of preference
        keys_to_try = [
            "STRIPE_SECRET_KEY",
            "STRIPE_TEST_SECRET_KEY" if self.environment != "production" else None,
            "STRIPE_LIVE_SECRET_KEY" if self.environment == "production" else None,
        ]

        for key in keys_to_try:
            if key:
                value = self.get(key)
                if value:
                    return value

        return None

    def get_aws_region(self) -> str:
        """Get the AWS region."""
        return self.get("AWS_REGION", "us-east-1") or "us-east-1"

    def get_aws_account_id(self) -> str | None:
        """Get the AWS account ID."""
        return self.get("AWS_ACCOUNT_ID")

    def get_stack_name(self) -> str | None:
        """Get the CloudFormation stack name."""
        return self.get("STACK_NAME")

    def get_product_id(self) -> str | None:
        """Get the API usage product ID."""
        return self.get("API_USAGE_PRODUCT_ID")

    def get_subscription_price_id(self) -> str | None:
        """Get the base subscription price ID."""
        return self.get("BASE_SUBSCRIPTION_PRICE_ID")

    def get_metered_price_id(self) -> str | None:
        """Get the metered usage price ID."""
        return self.get("METERED_USAGE_PRICE_ID")

    def set(self, key: str, value: str) -> None:
        """Set a configuration value.

        This is used when values are set programmatically (e.g., after creating
        Stripe products).

        Args:
            key: The configuration key (will be prefixed if environment is set)
            value: The value to set
        """
        if self.environment:
            prefix = self._get_prefix()
            prefixed_key = f"{prefix}{key}"
            self.config[prefixed_key] = value
        else:
            self.config[key] = value

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"CliConfig(environment={self.environment}, config_keys={len(self.config)})"


# Global config instance that can be imported
_global_config: CliConfig | None = None


def get_config(environment: str | None = None) -> CliConfig:
    """Get or create the global configuration instance.

    Args:
        environment: The target environment (staging, production, or None)

    Returns:
        The global CliConfig instance
    """
    global _global_config  # noqa: PLW0603
    if _global_config is None or _global_config.environment != environment:
        _global_config = CliConfig(environment)
    return _global_config


def reset_config() -> None:
    """Reset the global configuration (mainly for testing)."""
    global _global_config  # noqa: PLW0603
    _global_config = None
