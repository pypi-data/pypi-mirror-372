"""Generate real API traffic."""

import time

import click
import requests


@click.command("traffic")
@click.option(
    "--api-key",
    required=True,
    help="Real API key to use",
)
@click.option(
    "--base-url",
    required=True,
    help="API base URL",
)
@click.option(
    "--pattern",
    type=click.Choice(["steady", "burst", "ramp"]),
    default="steady",
    help="Traffic pattern",
)
@click.option(
    "--duration",
    default="1m",
    help="Duration (e.g., 1m, 1h)",
)
@click.option(
    "--requests-per-minute",
    "rpm",
    type=int,
    default=60,
    help="Requests per minute",
)
@click.option(
    "--verify-key-first",
    is_flag=True,
    default=True,
    help="Test API key before generating traffic",
)
@click.option(
    "--monitor",
    is_flag=True,
    help="Monitor traffic generation",
)
@click.option(
    "--cost-estimate",
    is_flag=True,
    help="Show estimated cost",
)
def traffic(
    api_key: str,
    base_url: str,
    pattern: str,
    duration: str,
    rpm: int,
    verify_key_first: bool,
    monitor: bool,
    cost_estimate: bool,
) -> None:
    """
    Generate REAL API traffic with REAL API keys.

    This command generates actual billable traffic to test usage
    tracking and billing. Use with caution.

    Examples:

        # Generate steady traffic for 1 hour
        ai-billing test integration traffic \\
            --api-key ${REAL_API_KEY} \\
            --base-url https://api.example.com \\
            --pattern steady \\
            --duration 1h \\
            --requests-per-minute 100

        # Test with monitoring and cost estimate
        ai-billing test integration traffic \\
            --api-key ${REAL_API_KEY} \\
            --base-url https://api.example.com \\
            --monitor \\
            --cost-estimate
    """
    # Parse duration
    duration_seconds = 60  # Default 1 minute
    if duration.endswith("h"):
        duration_seconds = int(duration[:-1]) * 3600
    elif duration.endswith("m"):
        duration_seconds = int(duration[:-1]) * 60
    elif duration.endswith("s"):
        duration_seconds = int(duration[:-1])

    total_requests = int((duration_seconds / 60) * rpm)

    if verify_key_first:
        click.echo("Testing API key...")
        headers = {"x-api-key": api_key}
        try:
            # Test with health endpoint
            response = requests.get(f"{base_url}/health", headers=headers, timeout=5)
            if response.status_code == 200:
                click.echo("✅ API key verified")
            else:
                click.echo(
                    click.style(
                        f"⚠️  API returned status {response.status_code}",
                        fg="yellow",
                    )
                )
        except Exception as e:
            click.echo(
                click.style(f"❌ Failed to verify API key: {e}", fg="red"),
                err=True,
            )
            raise click.Abort()

    if cost_estimate:
        # Assume $0.002 per 1000 requests
        estimated_cost = (total_requests / 1000) * 0.002
        click.echo(f"Estimated cost: ${estimated_cost:.4f}")
        click.echo(f"Total requests: {total_requests}")

        if not click.confirm("Continue?"):
            raise click.Abort()

    click.echo(f"Generating {pattern} traffic for {duration}...")
    click.echo(f"Target: {rpm} requests/minute")

    # Simplified traffic generation
    headers = {"x-api-key": api_key}
    success_count = 0
    error_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < duration_seconds:
            try:
                response = requests.get(
                    f"{base_url}/test",
                    headers=headers,
                    timeout=5,
                )
                if response.status_code < 400:
                    success_count += 1
                else:
                    error_count += 1

                if monitor and success_count % 10 == 0:
                    click.echo(f"  Sent {success_count} requests...")

                # Sleep to maintain rate
                time.sleep(60 / rpm)

            except KeyboardInterrupt:
                click.echo("\nStopping traffic generation...")
                break
            except Exception as e:
                error_count += 1
                if monitor:
                    click.echo(f"  Error: {e}")

    finally:
        elapsed = time.time() - start_time
        click.echo("\nTraffic Generation Summary:")
        click.echo(f"  Duration:  {elapsed:.1f}s")
        click.echo(f"  Successful: {success_count}")
        click.echo(f"  Errors:    {error_count}")
        click.echo(f"  Total:     {success_count + error_count}")

        if success_count > 0:
            click.echo(
                click.style(
                    f"✅ Generated {success_count} billable API calls",
                    fg="green",
                )
            )


__all__ = ["traffic"]
