"""Explain system architecture."""

import click


@click.command("explain")
@click.argument(
    "topic",
    type=click.Choice(
        [
            "architecture",
            "data-flow",
            "integrations",
            "api-keys",
            "stripe-events",
            "usage-tracking",
        ]
    ),
)
def explain(topic: str) -> None:
    """
    Explain billing system architecture and concepts.

    Example:
        ai-billing test simulate explain architecture
    """
    explanations = {
        "architecture": """
BILLING SYSTEM ARCHITECTURE
===========================

The system follows a reactive, event-driven architecture:

1. USER MANAGEMENT (Not our responsibility)
   • Cognito: Manages user accounts
   • API Gateway: Creates and manages API keys
   • Your App: Handles user signup/login

2. BILLING SYSTEM (What we manage)
   • Stripe: Payment processing and billing
   • EventBridge: Receives Stripe webhooks
   • Lambda: Processes events and moves API keys
   • DynamoDB: Links API keys to Stripe customers
   • CloudWatch: Tracks API usage

3. KEY PRINCIPLES
   • We REACT to events, we don't CREATE users
   • API keys exist before billing starts
   • Stripe owns the payment UI (Customer Portal)
   • We just move keys between usage plans
        """,
        "api-keys": """
API KEY LIFECYCLE
=================

1. CREATION (Not by billing system!)
   • User signs up in YOUR application
   • Cognito creates user account
   • API Gateway generates API key
   • Key starts on FREE usage plan

2. LINKING
   • User upgrades via Stripe Customer Portal
   • We receive webhook with Stripe customer ID
   • We link API key to Stripe customer in DynamoDB

3. PLAN MOVEMENT
   • Payment success → Move to METERED plan
   • Payment failure → Move to FREE plan
   • Subscription cancel → Move to FREE plan

IMPORTANT: We NEVER create API keys, only move them!
        """,
        "stripe-events": """
STRIPE EVENT PROCESSING
========================

Key Events We Handle:

1. checkout.session.completed
   → Customer completed payment
   → Action: Promote API key to metered

2. payment_method.attached
   → Payment method added
   → Action: Mark customer as payable

3. customer.subscription.deleted
   → Subscription cancelled
   → Action: Demote API key to free

4. payment_intent.payment_failed
   → Payment failed
   → Action: Grace period, then demote

Event Flow:
Stripe → EventBridge → Lambda → DynamoDB/API Gateway
        """,
        "data-flow": """
DATA FLOW
=========

1. API USAGE
   API Call → API Gateway → CloudWatch Metrics

2. USAGE REPORTING
   CloudWatch → Lambda (hourly) → Stripe Usage Records

3. PAYMENT EVENTS
   Stripe → EventBridge → Lambda → API Gateway Plans

4. CUSTOMER LINKING
   Lambda → DynamoDB (store link)
   Lambda → API Gateway (move key)
        """,
        "integrations": """
SYSTEM INTEGRATIONS
===================

1. STRIPE
   • Manages customers and billing
   • Sends webhooks for events
   • Receives usage reports
   • Handles payment collection

2. AWS API GATEWAY
   • Manages API keys
   • Enforces usage plans
   • Tracks API usage

3. EVENTBRIDGE
   • Receives Stripe webhooks
   • Routes to Lambda functions
   • Provides event replay

4. DYNAMODB
   • Stores API key ↔ Stripe customer links
   • Tracks billing state
   • Records usage reporting timestamps

5. CLOUDWATCH
   • Aggregates API usage metrics
   • Triggers hourly sync
   • Stores Lambda logs
        """,
        "usage-tracking": """
USAGE TRACKING & REPORTING
==========================

1. COLLECTION
   • API Gateway logs every API call
   • CloudWatch aggregates by API key
   • Metrics available in near real-time

2. REPORTING SCHEDULE
   • EventBridge rule: rate(1 hour)
   • Lambda reads CloudWatch metrics
   • Reports to Stripe with idempotency

3. IDEMPOTENCY
   • Each hour has unique idempotency key
   • Format: {api_key}_{timestamp}
   • Prevents duplicate charges

4. BILLING
   • Stripe accumulates usage
   • Invoice generated monthly
   • Payment collected automatically
        """,
    }

    click.echo(explanations.get(topic, "Topic not found"))


__all__ = ["explain"]
