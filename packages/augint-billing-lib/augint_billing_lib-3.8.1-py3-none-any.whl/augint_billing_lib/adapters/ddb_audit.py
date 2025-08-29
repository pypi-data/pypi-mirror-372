"""DynamoDB adapter for usage report audit trail.

This module implements the UsageReportAuditPort interface using DynamoDB
for persistent storage of usage reports.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from ..logging import log_event
from ..models import UsageReport
from ..utils_retry import retry


class DdbAuditRepo:
    """DynamoDB implementation of UsageReportAuditPort.

    Stores usage reports in a DynamoDB table with the following structure:
    - Partition Key: api_key_id
    - Sort Key: window_end_timestamp (epoch seconds)
    - GSI: stripe_customer_id (for customer queries)

    The table uses TTL to automatically delete old records after 90 days.
    """

    def __init__(self, table_name: str | None = None):
        """Initialize the audit repository.

        Args:
            table_name: DynamoDB table name. If not provided, uses
                       {STACK_NAME}-usage-audit from environment.
        """
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = table_name or self._get_table_name()
        self.table = self.dynamodb.Table(self.table_name)
        log_event("info", "ddb_audit_repo_initialized", table_name=self.table_name)

    def _get_table_name(self) -> str:
        """Get the audit table name from environment."""
        stack_name = os.environ.get("STACK_NAME")
        if not stack_name:
            raise ValueError("STACK_NAME environment variable not set")
        return f"{stack_name}-usage-audit"

    @retry((ClientError,), tries=3)
    def record_usage_report(self, report: UsageReport) -> None:
        """Record a usage report to the audit trail.

        Uses conditional put to ensure idempotency - the same report
        (identified by api_key_id + window_end) can only be written once.
        """
        try:
            item = report.to_dynamodb_item()

            # Use conditional put for idempotency
            self.table.put_item(
                Item=item,
                ConditionExpression=(
                    "attribute_not_exists(api_key_id) AND "
                    "attribute_not_exists(window_end_timestamp)"
                ),
            )

            log_event(
                "info",
                "audit_report_recorded",
                api_key=report.api_key_id,
                window_end=report.window_end.isoformat(),
                units=report.units_reported,
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                # Report already exists - this is fine (idempotent)
                log_event(
                    "debug",
                    "audit_report_already_exists",
                    api_key=report.api_key_id,
                    window_end=report.window_end.isoformat(),
                )
            else:
                log_event(
                    "error",
                    "audit_report_failed",
                    api_key=report.api_key_id,
                    error=str(e),
                )
                raise

    @retry((ClientError,), tries=3)
    def get_reports_for_window(
        self, api_key_id: str, window_start: datetime, window_end: datetime
    ) -> list[UsageReport]:
        """Retrieve all reports for a specific usage window."""
        try:
            # Query by api_key_id and window_end_timestamp range
            response = self.table.query(
                KeyConditionExpression=Key("api_key_id").eq(api_key_id)
                & Key("window_end_timestamp").between(
                    int(window_start.timestamp()), int(window_end.timestamp())
                )
            )

            reports = []
            for item in response.get("Items", []):
                reports.append(self._item_to_report(item))

            # Handle pagination if needed
            while "LastEvaluatedKey" in response:
                response = self.table.query(
                    KeyConditionExpression=Key("api_key_id").eq(api_key_id)
                    & Key("window_end_timestamp").between(
                        int(window_start.timestamp()), int(window_end.timestamp())
                    ),
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    reports.append(self._item_to_report(item))

            return reports

        except Exception as e:
            log_event(
                "error",
                "audit_query_failed",
                api_key=api_key_id,
                error=str(e),
            )
            raise

    @retry((ClientError,), tries=3)
    def get_reports_for_customer(
        self, customer_id: str, since: datetime, until: datetime | None = None
    ) -> list[UsageReport]:
        """Retrieve all reports for a customer in a time range."""
        if until is None:
            until = datetime.now(UTC)

        try:
            # Use GSI to query by customer
            response = self.table.query(
                IndexName="gsi_stripe_customer",
                KeyConditionExpression=Key("stripe_customer_id").eq(customer_id),
                FilterExpression=Key("window_end_timestamp").between(
                    int(since.timestamp()), int(until.timestamp())
                ),
            )

            reports = []
            for item in response.get("Items", []):
                reports.append(self._item_to_report(item))

            # Handle pagination
            while "LastEvaluatedKey" in response:
                response = self.table.query(
                    IndexName="gsi_stripe_customer",
                    KeyConditionExpression=Key("stripe_customer_id").eq(customer_id),
                    FilterExpression=Key("window_end_timestamp").between(
                        int(since.timestamp()), int(until.timestamp())
                    ),
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    reports.append(self._item_to_report(item))

            # Sort by window_end
            reports.sort(key=lambda r: r.window_end)
            return reports

        except Exception as e:
            log_event(
                "error",
                "audit_customer_query_failed",
                customer_id=customer_id,
                error=str(e),
            )
            raise

    def find_gaps(
        self, api_key_id: str, expected_interval: timedelta = timedelta(hours=1)
    ) -> list[tuple[datetime, datetime]]:
        """Find gaps in usage reporting.

        Analyzes sequential reports to identify missing windows.
        """
        try:
            # Get all reports for this API key
            response = self.table.query(
                KeyConditionExpression=Key("api_key_id").eq(api_key_id),
                ScanIndexForward=True,  # Sort ascending by window_end
            )

            reports = []
            for item in response.get("Items", []):
                reports.append(self._item_to_report(item))

            # Handle pagination
            while "LastEvaluatedKey" in response:
                response = self.table.query(
                    KeyConditionExpression=Key("api_key_id").eq(api_key_id),
                    ScanIndexForward=True,
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    reports.append(self._item_to_report(item))

            if len(reports) < 2:
                return []  # Need at least 2 reports to find gaps

            gaps = []
            for i in range(1, len(reports)):
                prev_report = reports[i - 1]
                curr_report = reports[i]

                # Expected next window start
                expected_start = prev_report.window_end

                # If there's a gap between prev window end and current window start
                if curr_report.window_start > expected_start + expected_interval:
                    gaps.append((expected_start, curr_report.window_start))

            log_event(
                "info",
                "audit_gaps_found",
                api_key=api_key_id,
                gap_count=len(gaps),
            )

            return gaps

        except Exception as e:
            log_event(
                "error",
                "audit_gap_analysis_failed",
                api_key=api_key_id,
                error=str(e),
            )
            raise

    def _item_to_report(self, item: Mapping[str, object]) -> UsageReport:
        """Convert a DynamoDB item to a UsageReport."""
        # Type narrowing with explicit conversions
        return UsageReport(
            api_key_id=str(item["api_key_id"]),
            window_start=datetime.fromisoformat(str(item["window_start_iso"])),
            window_end=datetime.fromisoformat(str(item["window_end_iso"])),
            units_reported=int(str(item["units_reported"])),
            stripe_customer_id=str(item["stripe_customer_id"]),
            stripe_subscription_item_id=str(item["stripe_subscription_item_id"]),
            usage_plan_id=str(item["usage_plan_id"]),
            stripe_idempotency_key=str(item["stripe_idempotency_key"]),
            stripe_response=item.get("stripe_response", {})
            if isinstance(item.get("stripe_response"), dict)
            else {},  # type: ignore[arg-type]
            stripe_usage_record_id=str(item["stripe_usage_record_id"])
            if item.get("stripe_usage_record_id")
            else None,
            reported_at=datetime.fromisoformat(str(item["reported_at_iso"])),
            reported_by_request_id=str(item["reported_by"]),
            lambda_function_version=str(item["lambda_function_version"]),
            library_version=str(item["library_version"]),
            source_usage_count=int(str(item["source_usage_count"]))
            if item.get("source_usage_count") is not None
            else None,
            previous_window_end=(
                datetime.fromisoformat(str(item["previous_window_end_iso"]))
                if "previous_window_end_iso" in item
                else None
            ),
        )
