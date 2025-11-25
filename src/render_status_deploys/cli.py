"""CLI entry point."""

import logging
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .client import RenderClient

logger = logging.getLogger(__name__)
console = Console()


def format_timestamp(ts: str | None) -> str:
    """Format ISO timestamp to human-readable format in local timezone.

    Args:
        ts: ISO format timestamp

    Returns:
        Formatted timestamp or 'N/A'
    """
    if not ts:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        tz_name = local_dt.strftime("%Z")
        return local_dt.strftime(f"%Y-%m-%d %H:%M:%S {tz_name}")
    except (ValueError, AttributeError):
        return ts


def get_status_color(status: str) -> str:
    """Get color for status.

    Args:
        status: Deploy or job status

    Returns:
        Rich color code
    """
    status_lower = status.lower()
    if status_lower in ("live", "succeeded", "success"):
        return "green"
    if status_lower in ("building", "deploying", "running"):
        return "yellow"
    if status_lower in ("build_failed", "failed", "canceled"):
        return "red"
    return "white"


def build_services_output(client: RenderClient) -> Table | tuple[Table, Table]:
    """Build service tables for display.

    Args:
        client: Render API client

    Returns:
        Table or tuple of (services_table, cron_table)
    """
    try:
        services = client.get_services()
    except Exception as e:
        error_table = Table(show_header=False)
        error_table.add_row(f"[red]Error fetching services: {e}[/red]")
        return error_table

    if not services:
        empty_table = Table(show_header=False)
        empty_table.add_row("[yellow]No services found[/yellow]")
        return empty_table

    # Create services table
    table = Table(title="Render Services", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="blue")
    table.add_column("Status", style="white")
    table.add_column("Latest Deploy", style="white")
    table.add_column("Updated", style="white")

    for service in services:
        service_type = service.get("type", "N/A")
        name = service.get("name", "N/A")
        service_id = service.get("id", "")

        # Get latest deploy
        latest_status = "N/A"
        latest_deploy_time = "N/A"
        if service_type != "cron_job":
            try:
                deploys = client.get_deploys(service_id, limit=1)
                if deploys:
                    latest = deploys[0]
                    status = latest.get("status", "N/A")
                    color = get_status_color(status)
                    latest_status = f"[bold {color}]{status}[/bold {color}]"
                    latest_deploy_time = format_timestamp(latest.get("createdAt"))
            except Exception as e:
                logger.warning(f"Failed to fetch deploys for {name}: {e}")
                latest_status = "[red]Error[/red]"

        updated_at = format_timestamp(service.get("updatedAt"))

        table.add_row(
            name,
            service_type,
            latest_status,
            latest_deploy_time,
            updated_at,
        )

    # Display cron jobs separately
    cron_services = [s for s in services if s.get("type") == "cron_job"]
    if cron_services:
        cron_table = Table(title="Cron Jobs", show_header=True, header_style="bold magenta")
        cron_table.add_column("Name", style="cyan", no_wrap=True)
        cron_table.add_column("Schedule", style="blue")
        cron_table.add_column("Last Run", style="white")
        cron_table.add_column("Status", style="white")

        for service in cron_services:
            name = service.get("name", "N/A")
            service_id = service.get("id", "")
            schedule = service.get("serviceDetails", {}).get("schedule", "N/A")

            # Use lastSuccessfulRunAt from serviceDetails
            last_run_ts = service.get("serviceDetails", {}).get("lastSuccessfulRunAt")
            last_run = format_timestamp(last_run_ts) if last_run_ts else "N/A"

            # Jobs endpoint doesn't return historical data, so just show "succeeded" if we have a last run
            job_status = "[bold green]succeeded[/bold green]" if last_run_ts else "N/A"

            cron_table.add_row(name, schedule, last_run, job_status)

        return (table, cron_table)

    return table


def display_services(client: RenderClient) -> None:
    """Display all services with latest deploy status.

    Args:
        client: Render API client
    """
    output = build_services_output(client)
    if isinstance(output, tuple):
        console.print(output[0])
        console.print("\n")
        console.print(output[1])
    else:
        console.print(output)


def generate_display(client: RenderClient):
    """Generate display output with timestamp.

    Args:
        client: Render API client

    Returns:
        Rich renderable group
    """
    from rich.console import Group
    from rich.text import Text

    output = build_services_output(client)
    now = datetime.now().astimezone()
    tz_name = now.strftime("%Z")
    timestamp = now.strftime(f"%Y-%m-%d %H:%M:%S {tz_name}")
    timestamp_text = Text(f"Last updated: {timestamp} (Ctrl+C to quit)", style="dim")

    if isinstance(output, tuple):
        return Group(timestamp_text, Text(""), output[0], Text(""), output[1])
    else:
        return Group(timestamp_text, Text(""), output)


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Render.com services")
    parser.add_argument("--once", action="store_true", help="Run once and exit (no live updates)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load .env file
    load_dotenv()

    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        console.print("[red]Error: RENDER_API_KEY not found in environment or .env file[/red]")
        sys.exit(1)

    with RenderClient(api_key) as client:
        if args.once:
            # Single run mode
            now = datetime.now().astimezone()
            tz_name = now.strftime("%Z")
            timestamp = now.strftime(f"%Y-%m-%d %H:%M:%S {tz_name}")
            console.print(f"[dim]Last updated: {timestamp}[/dim]\n")
            display_services(client)
        else:
            # Live update mode
            try:
                with Live(generate_display(client), refresh_per_second=1, console=console) as live:
                    while True:
                        time.sleep(10)
                        live.update(generate_display(client))
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped[/yellow]")


if __name__ == "__main__":
    main()
