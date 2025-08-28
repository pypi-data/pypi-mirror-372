"""Core billing service orchestration.

This module contains the main business logic for the billing system, orchestrating
interactions between Stripe, AWS API Gateway, and the customer repository. The
BillingService class is the central coordinator that implements the billing workflows.

The service handles three main workflows:
    1. Stripe event processing - React to payment events and update plan status
    2. Usage reporting - Report API usage to Stripe for metered billing
    3. Plan management - Direct promotion/demotion of customers

Example:
    Basic service usage::

        from augint_billing_lib.service import BillingService
        from augint_billing_lib.adapters import (
            StripeAdapter, DynamoDBRepoAdapter,
            APIGatewayUsageAdapter, APIGatewayAdminAdapter
        )

        # Create service with all dependencies
        service = BillingService(
            repo=DynamoDBRepoAdapter(table_name="billing-links"),
            stripe=StripeAdapter(api_key="sk_test_..."),
            usage=APIGatewayUsageAdapter(),
            plan_admin=APIGatewayAdminAdapter()
        )

        # Handle a Stripe webhook event
        result = service.handle_stripe_event({
            "type": "payment_method.attached",
            "data": {"object": {"customer": "cus_123"}}
        })

        # Report usage for the last hour
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        reports = service.reconcile_usage_window(hour_ago, now)
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from .logging import log_event, log_metric
from .models import UsageReport
from .ports import (
    CustomerRepoPort,
    PlanAdminPort,
    StripePort,
    UsageReportAuditPort,
    UsageSourcePort,
)

# Get version without circular import
__version__ = "2.6.1"


class BillingService:
    """Orchestrates billing operations between Stripe and AWS services.

    The BillingService is the core business logic component that coordinates
    all billing operations. It processes Stripe events, manages plan transitions,
    reports usage, and handles customer promotions/demotions.

    The service is designed to be:
        - Stateless - All state is stored in the repository
        - Idempotent - Safe to retry operations
        - Testable - Dependencies injected via ports
        - Cloud-agnostic - No direct AWS/Stripe dependencies

    Attributes:
        repo: Customer repository for persisting link data
        stripe: Stripe operations port for payment processing
        usage: Optional usage source for API Gateway metrics
        plan_admin: Optional plan administration for moving API keys
    """

    def __init__(
        self,
        repo: CustomerRepoPort,
        stripe: StripePort,
        usage: UsageSourcePort | None = None,
        plan_admin: PlanAdminPort | None = None,
        audit: UsageReportAuditPort | None = None,
    ):
        """Initialize the billing service with required dependencies.

        Args:
            repo: Customer repository for data persistence
            stripe: Stripe port for payment operations
            usage: Optional port for fetching usage data (required for reconcile_usage_window)
            plan_admin: Optional port for API key plan management
                (required for apply_plan_move_for_customer)
            audit: Optional port for usage report audit trail
        """
        self.repo = repo
        self.stripe = stripe
        self.usage = usage
        self.plan_admin = plan_admin
        self.audit = audit

    # --- Event handling ---
    def handle_stripe_event(self, evt: dict[str, Any]) -> dict[str, Any]:
        """Process a Stripe webhook event and determine the target plan.

        This method is the main entry point for processing Stripe events. It analyzes
        the event type and customer payment status to determine whether the customer
        should be on the free or metered plan.

        Supported events:
            - payment_method.attached: Customer adds a payment method
            - setup_intent.succeeded: Payment setup completed
            - customer.subscription.created/updated: Subscription changes
            - invoice.payment_failed: Payment failure

        Args:
            evt: Stripe event dictionary, either raw or wrapped in EventBridge format

        Returns:
            Dictionary containing:
                - target_plan: 'free', 'metered', or None if no action needed
                - stripe_customer_id: Customer ID from the event
                - subscription_item_id: ID for usage reporting (metered plan only)
                - reason: Event type or reason for the decision

        Example:
            Processing a payment method attachment::

                result = service.handle_stripe_event({
                    "type": "payment_method.attached",
                    "data": {
                        "object": {
                            "customer": "cus_123",
                            "type": "card"
                        }
                    }
                })
                # Returns: {
                #     "target_plan": "metered",
                #     "stripe_customer_id": "cus_123",
                #     "subscription_item_id": "si_abc",
                #     "reason": "payment_method.attached"
                # }
        """
        detail = evt.get("detail", evt)
        etype = detail.get("type")
        data = detail.get("data") or {}
        obj = data.get("object") or {}
        customer_id = obj.get("customer") or data.get("object", {}).get("customer")

        if not customer_id:
            log_event("warning", "stripe_event_missing_customer", event_type=etype or "unknown")
            return {"target_plan": None, "reason": "no_customer_in_event"}

        if etype in (
            "payment_method.attached",
            "setup_intent.succeeded",
            "customer.subscription.created",
            "customer.subscription.updated",
        ):
            if self.stripe.has_default_payment_method(customer_id):
                sub_item_id = self.stripe.ensure_metered_subscription(customer_id)
                log_event(
                    "info",
                    "promote_to_metered",
                    customer_id=customer_id,
                    sub_item=sub_item_id,
                    reason=etype,
                )
                return {
                    "target_plan": "metered",
                    "stripe_customer_id": customer_id,
                    "subscription_item_id": sub_item_id,
                    "reason": etype,
                }
            log_event("info", "stay_free_no_default_pm", customer_id=customer_id, reason=etype)
            return {
                "target_plan": "free",
                "stripe_customer_id": customer_id,
                "subscription_item_id": None,
                "reason": "no_default_pm",
            }

        if etype == "invoice.payment_failed":
            log_event("warning", "demote_to_free_payment_failed", customer_id=customer_id)
            return {
                "target_plan": "free",
                "stripe_customer_id": customer_id,
                "subscription_item_id": None,
                "reason": etype,
            }

        log_event("info", "event_ignored", event_type=etype)
        return {"target_plan": None, "reason": f"ignored:{etype}"}

    # --- Usage reporting ---
    def reconcile_usage_window(self, since: datetime, until: datetime) -> list[dict[str, Any]]:
        """Report usage to Stripe for all metered customers within a time window.

        This method fetches API usage data for all customers on metered plans and
        reports it to Stripe for billing. It's designed to be called periodically
        (typically hourly) to sync usage data.

        The method:
            1. Scans for all customers on metered plans
            2. Fetches their API usage from API Gateway
            3. Prevents double-billing from overlapping windows
            4. Detects and fills gaps in usage windows
            5. Reports non-zero usage to Stripe with idempotency
            6. Returns a summary of all reports made

        Args:
            since: Start of the usage window (inclusive)
            until: End of the usage window (exclusive)

        Returns:
            List of usage reports, each containing:
                - api_key_id: The API key that generated usage
                - customer_id: Stripe customer ID
                - units: Number of units reported
                - window_start: Start of the actual window reported
                - window_end: End of the actual window reported

        Raises:
            AssertionError: If usage port is not configured

        Example:
            Report usage for the last hour::

                from datetime import datetime, timedelta

                now = datetime.utcnow()
                hour_ago = now - timedelta(hours=1)

                reports = service.reconcile_usage_window(hour_ago, now)
                # Returns: [
                #     {
                #         "api_key_id": "key_123",
                #         "customer_id": "cus_456",
                #         "units": 1500,
                #         "window_start": "2024-01-15T09:00:00",
                #         "window_end": "2024-01-15T10:00:00"
                #     }
                # ]
        """
        assert self.usage is not None, "UsageSourcePort required"
        reports = []
        for link in self.repo.scan_metered():
            # Determine the actual window start
            # Use the last processed window end, or fallback to 'since' for first run
            window_start = link.last_usage_window_end or since

            # Skip if we've already processed this or a later window
            if link.last_usage_window_end and link.last_usage_window_end >= until:
                log_event(
                    "info",
                    "usage_window_already_processed",
                    api_key=link.api_key_id,
                    requested_window=f"{since.isoformat()}-{until.isoformat()}",
                    last_processed=link.last_usage_window_end.isoformat(),
                    action="skipped",
                )
                continue

            # Check for gaps and log warning
            if link.last_usage_window_end and window_start > since:
                gap_seconds = (window_start - since).total_seconds()
                if gap_seconds > 300:  # More than 5 minutes gap
                    log_event(
                        "warning",
                        "usage_window_gap_detected",
                        api_key=link.api_key_id,
                        gap_start=since.isoformat(),
                        gap_end=window_start.isoformat(),
                        gap_seconds=gap_seconds,
                    )

            # Fetch usage for the EXACT window we need
            used = self.usage.get_usage(
                link.usage_plan_id,
                link.api_key_id,
                window_start,  # Not 'since' - use actual window start!
                until,
            )

            if used is None:
                log_event(
                    "warning",
                    "no_usage_data_available",
                    api_key=link.api_key_id,
                    window=f"{window_start.isoformat()}-{until.isoformat()}",
                )
                continue

            if used > 0 and link.metered_subscription_item_id:
                # Create deterministic idempotency key based on window
                # This ensures retries of the same window won't double-bill
                idempotency_key = (
                    f"{link.api_key_id}:{window_start.isoformat()}:{until.isoformat()}"
                )

                try:
                    # Report to Stripe
                    timestamp = int(until.replace(tzinfo=UTC).timestamp())
                    stripe_response = self.stripe.report_usage(
                        link.metered_subscription_item_id, used, timestamp, idempotency_key
                    )

                    # Record to audit trail if available
                    if self.audit:
                        try:
                            audit_report = UsageReport(
                                api_key_id=link.api_key_id,
                                window_start=window_start,
                                window_end=until,
                                units_reported=used,
                                stripe_customer_id=link.stripe_customer_id,
                                stripe_subscription_item_id=link.metered_subscription_item_id,
                                usage_plan_id=link.usage_plan_id,
                                stripe_idempotency_key=idempotency_key,
                                stripe_response=stripe_response,
                                stripe_usage_record_id=stripe_response.get("id"),
                                reported_at=datetime.now(UTC),
                                reported_by_request_id=os.environ.get("AWS_REQUEST_ID", "unknown"),
                                lambda_function_version=os.environ.get(
                                    "AWS_LAMBDA_FUNCTION_VERSION", "unknown"
                                ),
                                library_version=__version__,
                                source_usage_count=used,
                                previous_window_end=link.last_usage_window_end,
                            )
                            self.audit.record_usage_report(audit_report)
                        except Exception as e:
                            # Audit failure should not stop billing
                            log_event(
                                "error",
                                "audit_trail_failed",
                                api_key=link.api_key_id,
                                error=str(e),
                            )

                    # Update state ONLY after successful reporting
                    link.last_usage_window_end = until
                    link.last_usage_window_units = used
                    link.last_usage_window_idem_key = idempotency_key
                    link.last_reported_usage_ts = datetime.now(UTC)

                    # Save immediately to prevent race conditions
                    self.repo.save(link)

                    reports.append(
                        {
                            "api_key_id": link.api_key_id,
                            "customer_id": link.stripe_customer_id,
                            "units": used,
                            "window_start": window_start.isoformat(),
                            "window_end": until.isoformat(),
                        }
                    )

                    log_event(
                        "info",
                        "usage_reported_successfully",
                        api_key=link.api_key_id,
                        units=used,
                        window=f"{window_start.isoformat()}-{until.isoformat()}",
                        idempotency_key=idempotency_key,
                    )

                except Exception as e:
                    # Don't update state if reporting failed
                    log_event(
                        "error",
                        "usage_reporting_failed",
                        api_key=link.api_key_id,
                        window=f"{window_start.isoformat()}-{until.isoformat()}",
                        error=str(e),
                    )
                    # Re-raise to trigger Lambda retry
                    raise

        log_metric("UsageReports", len(reports), dims={"WindowHours": "1"})
        return reports

    # Optional in-lib plan move if admin is wired
    def apply_plan_move_for_customer(
        self,
        customer_id: str,
        target: str,
        sub_item_id: str | None,
        free_plan_id: str,
        metered_plan_id: str,
    ) -> int:
        """Apply a plan change for all API keys belonging to a customer.

        This method moves all of a customer's API keys between usage plans
        and updates their link records. It's typically called after processing
        a Stripe event to apply the plan change in API Gateway.

        Args:
            customer_id: Stripe customer ID
            target: Target plan ('free' or 'metered')
            sub_item_id: Subscription item ID for metered plan, None for free
            free_plan_id: API Gateway usage plan ID for free tier
            metered_plan_id: API Gateway usage plan ID for metered tier

        Returns:
            Number of API keys moved

        Note:
            Requires plan_admin port to be configured. Returns 0 if not available.

        Example:
            Apply a promotion to metered plan::

                moved = service.apply_plan_move_for_customer(
                    customer_id="cus_123",
                    target="metered",
                    sub_item_id="si_456",
                    free_plan_id="FREE_10K",
                    metered_plan_id="METERED"
                )
                # Returns: 2 (if customer has 2 API keys)
        """
        if not self.plan_admin:
            return 0
        moved = 0
        for link in self.repo.get_by_customer(customer_id):
            target_plan_id = metered_plan_id if target == "metered" else free_plan_id
            self.plan_admin.move_key_to_plan(link.api_key_id, target_plan_id)
            link.plan = "metered" if target == "metered" else "free"
            link.usage_plan_id = "METERED" if target == "metered" else "FREE_10K"
            if sub_item_id and target == "metered":
                link.metered_subscription_item_id = sub_item_id
            self.repo.save(link)
            moved += 1
        return moved
