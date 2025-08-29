"""AWS operations commands."""

import click

from augint_billing_lib.cli.aws.apigateway_ops import apigateway_group
from augint_billing_lib.cli.aws.cloudwatch_ops import cloudwatch_group
from augint_billing_lib.cli.aws.eventbridge_ops import eventbridge_group
from augint_billing_lib.cli.aws.lambda_ops import lambda_group


@click.group(
    name="aws",
    help="""
    AWS operations commands.

    These commands provide direct access to AWS services for managing
    and monitoring the billing infrastructure.

    Commands:
    • lambda      - Lambda function operations
    • eventbridge - EventBridge rule management
    • apigateway  - API Gateway operations
    • cloudwatch  - CloudWatch logs and metrics

    These are generic AWS operations that work across stacks.
    For stack-specific operations, use 'ai-billing infra' commands.
    """,
)
def aws_group() -> None:
    """AWS command group."""


aws_group.add_command(lambda_group)
aws_group.add_command(eventbridge_group)
aws_group.add_command(apigateway_group)
aws_group.add_command(cloudwatch_group)


__all__ = ["aws_group"]
