"""Data models for the billing system.

This module contains the core data structures used throughout the billing library.
The models are designed to be simple, immutable where possible, and focused on
representing the domain concepts clearly.

Example:
    Creating and working with a Link::

        from augint_billing_lib.models import Link
        from datetime import datetime

        # Create a new link for a free tier customer
        link = Link(
            api_key_id="key_abc123",
            stripe_customer_id="cus_xyz789",
            plan="free",
            usage_plan_id="FREE_10K"
        )

        # Upgrade to metered plan
        link.plan = "metered"
        link.usage_plan_id = "METERED"
        link.metered_subscription_item_id = "si_metered123"
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal


@dataclass
class Link:
    """Represents the link between an API key, Stripe customer, and usage plan.

    This is the core entity that maps API keys to Stripe customers and tracks
    their current plan status, usage reporting state, and subscription details.

    The Link model serves as the source of truth for:
        - Which usage plan an API key belongs to
        - Which Stripe customer owns the API key
        - Current billing state (free vs metered)
        - Usage reporting checkpoints

    Attributes:
        api_key_id: Unique identifier for the API key. This is the primary key
            used to look up customer information.

        stripe_customer_id: Stripe customer ID (e.g., 'cus_abc123'). Links the
            API key to a Stripe customer for billing.

        cognito_user_id: Optional AWS Cognito user ID for additional user context.
            May be None if the user hasn't authenticated via Cognito.

        plan: Current billing plan. Either 'free' for the limited free tier or
            'metered' for usage-based billing. Defaults to 'free'.

        usage_plan_id: API Gateway usage plan ID that controls rate limits and
            quotas. Typically 'FREE_10K' or 'METERED'. Defaults to 'FREE_10K'.

        metered_subscription_item_id: Stripe subscription item ID for metered billing.
            Required when plan='metered', None for free tier customers.

        last_reported_usage_ts: Timestamp of the last successful usage report to Stripe.
            Used to calculate incremental usage since last report. None if never reported.

        current_month_reported_units: Running total of units reported for the current
            billing month. Resets to 0 at month boundaries. Used to calculate deltas.

    Example:
        Free tier customer::

            link = Link(
                api_key_id="key_free123",
                stripe_customer_id="cus_free456",
                plan="free",
                usage_plan_id="FREE_10K"
            )

        Metered customer with usage history::

            link = Link(
                api_key_id="key_metered789",
                stripe_customer_id="cus_metered012",
                plan="metered",
                usage_plan_id="METERED",
                metered_subscription_item_id="si_abc123",
                last_reported_usage_ts=datetime(2024, 1, 15, 10, 0),
                current_month_reported_units=5000
            )

    Note:
        The Link model is persisted in DynamoDB with api_key_id as the partition key
        and stripe_customer_id indexed for reverse lookups.
    """

    api_key_id: str
    """Unique identifier for the API key (primary key)."""

    stripe_customer_id: str
    """Stripe customer ID for billing association."""

    cognito_user_id: str | None = None
    """Optional AWS Cognito user identifier."""

    plan: Literal["free", "metered"] = "free"
    """Current billing plan type."""

    usage_plan_id: str = "FREE_10K"
    """API Gateway usage plan ID for rate limiting."""

    metered_subscription_item_id: str | None = None
    """Stripe subscription item ID for usage reporting."""

    last_reported_usage_ts: datetime | None = None
    """Timestamp of last successful usage report."""

    current_month_reported_units: int = 0
    """Running total of reported units for current month."""

    last_usage_window_end: datetime | None = None
    """Track last processed window boundary to prevent overlaps."""

    last_usage_window_units: int | None = None
    """Units reported in last window for reconciliation."""

    last_usage_window_idem_key: str | None = None
    """Idempotency key used for debugging."""

    def is_metered(self) -> bool:
        """Check if this link is on a metered plan.

        Returns:
            True if plan is 'metered', False otherwise.
        """
        return self.plan == "metered"

    def is_free(self) -> bool:
        """Check if this link is on the free plan.

        Returns:
            True if plan is 'free', False otherwise.
        """
        return self.plan == "free"

    def can_report_usage(self) -> bool:
        """Check if this link is ready for usage reporting.

        A link can report usage if it's on a metered plan and has
        a valid subscription item ID.

        Returns:
            True if usage can be reported, False otherwise.
        """
        return self.is_metered() and self.metered_subscription_item_id is not None

    def needs_month_reset(self, current_time: datetime) -> bool:
        """Check if the usage counter needs to be reset for a new month.

        Args:
            current_time: The current timestamp to check against.

        Returns:
            True if the month has changed since last report, False otherwise.
        """
        if self.last_reported_usage_ts is None:
            return False

        return (
            self.last_reported_usage_ts.year != current_time.year
            or self.last_reported_usage_ts.month != current_time.month
        )


@dataclass
class UsageReport:
    """Immutable record of a usage report to Stripe.

    This model represents a single usage report sent to Stripe, providing
    an audit trail for billing reconciliation, debugging, and compliance.

    Attributes:
        api_key_id: The API key this report is for
        window_start: Start of the usage window (inclusive)
        window_end: End of the usage window (exclusive)
        units_reported: Number of units reported to Stripe
        stripe_customer_id: Customer ID in Stripe
        stripe_subscription_item_id: Subscription item for metered billing
        usage_plan_id: API Gateway usage plan at time of reporting
        stripe_idempotency_key: Key used to ensure idempotent Stripe calls
        stripe_response: Full response from Stripe API
        stripe_usage_record_id: ID of created usage record in Stripe
        reported_at: When this report was created
        reported_by_request_id: AWS Request ID or other tracking ID
        lambda_function_version: Version of Lambda function that created report
        library_version: Version of this library when report was created
        source_usage_count: Raw usage count from API Gateway (optional)
        previous_window_end: End of previous window for gap detection (optional)
    """

    # Key fields
    api_key_id: str
    window_start: datetime
    window_end: datetime

    # What was reported
    units_reported: int
    stripe_customer_id: str
    stripe_subscription_item_id: str
    usage_plan_id: str

    # Stripe interaction
    stripe_idempotency_key: str
    stripe_response: dict[str, Any]

    # Metadata
    reported_at: datetime
    reported_by_request_id: str
    lambda_function_version: str
    library_version: str

    # Optional fields (with defaults)
    stripe_usage_record_id: str | None = None
    source_usage_count: int | None = None
    previous_window_end: datetime | None = None

    @property
    def window_duration_seconds(self) -> float:
        """Calculate the duration of the usage window in seconds."""
        return (self.window_end - self.window_start).total_seconds()

    @property
    def is_standard_hourly(self) -> bool:
        """Check if this is a standard hourly reporting window."""
        return self.window_duration_seconds == 3600

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Convert to DynamoDB item format.

        Returns:
            Dictionary with DynamoDB-compatible field names and types
        """
        return {
            "api_key_id": self.api_key_id,
            "window_end_timestamp": int(self.window_end.timestamp()),
            "window_start_iso": self.window_start.isoformat(),
            "window_end_iso": self.window_end.isoformat(),
            "units_reported": self.units_reported,
            "stripe_customer_id": self.stripe_customer_id,
            "stripe_subscription_item_id": self.stripe_subscription_item_id,
            "usage_plan_id": self.usage_plan_id,
            "stripe_idempotency_key": self.stripe_idempotency_key,
            "stripe_response": self.stripe_response,
            "stripe_usage_record_id": self.stripe_usage_record_id,
            "reported_at_iso": self.reported_at.isoformat(),
            "reported_by": self.reported_by_request_id,
            "lambda_function_version": self.lambda_function_version,
            "library_version": self.library_version,
            "report_date": self.window_end.date().isoformat(),
            "ttl_timestamp": int((self.reported_at + timedelta(days=90)).timestamp()),
        }
