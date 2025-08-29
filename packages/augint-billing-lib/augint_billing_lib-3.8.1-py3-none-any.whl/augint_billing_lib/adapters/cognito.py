"""AWS Cognito adapter implementation.

This module provides the concrete implementation of the CognitoPort interface,
managing user lookups and API key discovery in AWS Cognito and API Gateway.

The adapter handles:
    - User lookups by email in Cognito User Pool
    - API key discovery for Cognito users
    - Automatic retries for transient failures
    - Error handling for missing users

Example:
    Basic Cognito operations::

        import boto3
        from augint_billing_lib.adapters.cognito import CognitoAdapter

        # Create adapter
        cognito_client = boto3.client('cognito-idp')
        apigw_client = boto3.client('apigateway')
        adapter = CognitoAdapter(
            cognito_client=cognito_client,
            apigw_client=apigw_client,
            user_pool_id="us-east-1_abc123"
        )

        # Find user by email
        user_id = adapter.find_user_by_email("user@example.com")
        if user_id:
            # List their API keys
            keys = adapter.list_api_keys_for_user(user_id)
"""

from __future__ import annotations

import botocore
from mypy_boto3_apigateway import APIGatewayClient
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient

from ..logging import log_event
from ..utils_retry import retry


class CognitoAdapter:
    """AWS Cognito user operations adapter.

    Implements the CognitoPort interface for discovering users
    and their API keys from AWS Cognito and API Gateway.

    Attributes:
        cognito: Boto3 Cognito IDP client for user operations
        apigw: Boto3 API Gateway client for key discovery
        user_pool_id: Cognito User Pool ID to search
    """

    def __init__(
        self,
        cognito_client: CognitoIdentityProviderClient,
        apigw_client: APIGatewayClient,
        user_pool_id: str,
    ) -> None:
        """Initialize the Cognito adapter.

        Args:
            cognito_client: Boto3 Cognito IDP client
            apigw_client: Boto3 API Gateway client
            user_pool_id: Cognito User Pool ID (e.g., 'us-east-1_abc123')
        """
        self.cognito = cognito_client
        self.apigw = apigw_client
        self.user_pool_id = user_pool_id

    @retry((botocore.exceptions.ClientError,), tries=3)
    def find_user_by_email(self, email: str) -> str | None:
        """Find a Cognito user by their email address.

        Searches the configured User Pool for a user with the given email.
        Returns the user's sub (UUID) if found.

        Args:
            email: Email address to search for

        Returns:
            Cognito User ID (sub attribute) if found, None otherwise

        Example:
            Find user and get their ID::

                user_id = adapter.find_user_by_email("john@example.com")
                if user_id:
                    print(f"Found user: {user_id}")
                else:
                    print("User not found")
        """
        try:
            # Search for user by email
            response = self.cognito.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'email = "{email}"',
                Limit=1,
            )

            users = response.get("Users", [])
            if not users:
                log_event("info", "cognito_user_not_found", email=email)
                return None

            # Extract the sub attribute (user ID)
            user = users[0]
            attributes = user.get("Attributes", [])
            for attr in attributes:
                if attr.get("Name") == "sub":
                    user_id = attr.get("Value")
                    log_event("info", "cognito_user_found", email=email, user_id=user_id)
                    return user_id

            log_event("warning", "cognito_user_missing_sub", email=email)
            return None

        except self.cognito.exceptions.InvalidParameterException:
            # Invalid filter format or user pool
            log_event("error", "cognito_invalid_search", email=email)
            return None
        except Exception as e:
            log_event("error", "cognito_search_failed", email=email, error=str(e))
            raise

    @retry((botocore.exceptions.ClientError,), tries=3)
    def list_api_keys_for_user(self, cognito_user_id: str) -> list[str]:
        """List all API keys associated with a Cognito user.

        Searches API Gateway for API keys that have the Cognito user ID
        in their description or name. This assumes keys are created with
        a consistent naming pattern that includes the Cognito user ID.

        Args:
            cognito_user_id: Cognito User ID (sub attribute)

        Returns:
            List of API key IDs (values) associated with the user

        Example:
            Get all keys for a user::

                keys = adapter.list_api_keys_for_user("abc-123-def")
                for key in keys:
                    print(f"Found API key: {key}")
        """
        found_keys = []

        try:
            # Paginate through all API keys
            paginator = self.apigw.get_paginator("get_api_keys")
            page_iterator = paginator.paginate(
                includeValues=True, PaginationConfig={"PageSize": 500}
            )

            for page in page_iterator:
                items = page.get("items", [])
                for key in items:
                    # Check if this key belongs to the user
                    # Look in description and name for the Cognito user ID
                    description = key.get("description", "")
                    name = key.get("name", "")
                    tags = key.get("tags", {})

                    # Check multiple fields where user ID might be stored
                    if (
                        cognito_user_id in description
                        or cognito_user_id in name
                        or tags.get("cognitoUserId") == cognito_user_id
                        or tags.get("userId") == cognito_user_id
                    ):
                        # Get the actual API key value
                        key_value = key.get("value")
                        if key_value:
                            found_keys.append(key_value)
                            log_event(
                                "info",
                                "api_key_found_for_user",
                                cognito_user_id=cognito_user_id,
                                key_id=key.get("id"),
                            )

            log_event(
                "info",
                "api_keys_discovered",
                cognito_user_id=cognito_user_id,
                count=len(found_keys),
            )
            return found_keys

        except Exception as e:
            log_event(
                "error",
                "api_key_discovery_failed",
                cognito_user_id=cognito_user_id,
                error=str(e),
            )
            raise
