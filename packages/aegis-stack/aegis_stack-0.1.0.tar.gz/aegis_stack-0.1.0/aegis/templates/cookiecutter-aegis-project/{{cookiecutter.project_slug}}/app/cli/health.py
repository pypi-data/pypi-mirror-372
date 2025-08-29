"""
Health monitoring CLI commands.

Command-line interface for system health checking and monitoring via API endpoints.
"""

import asyncio
import json
import sys
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
import typer

from app.core.config import settings
from app.core.constants import CLI, APIEndpoints, Defaults
from app.core.log import setup_logging
from app.services.system.models import (
    ComponentStatusType,
    DetailedHealthResponse,
    HealthResponse,
)
from app.services.system.ui import get_status_icon, get_status_color_name

app = typer.Typer(name="health", help="System health monitoring commands")
console = Console()


def _get_status_icon_and_color(status: ComponentStatusType) -> tuple[str, str]:
    """Get the appropriate icon and color for a component status (shared mapping)."""
    return get_status_icon(status), get_status_color_name(status)


async def get_health_data(
    endpoint: str = APIEndpoints.HEALTH_BASIC,
) -> HealthResponse | DetailedHealthResponse:
    """Get health data from the API endpoint with Pydantic validation."""
    base_url = getattr(settings, "API_BASE_URL", "http://localhost:8000")
    url = f"{base_url}{endpoint}"

    timeout = httpx.Timeout(Defaults.API_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            json_data = response.json()

            # Validate response with appropriate Pydantic model
            if endpoint == APIEndpoints.HEALTH_DETAILED:
                return DetailedHealthResponse.model_validate(json_data)
            else:
                return HealthResponse.model_validate(json_data)

        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to API server at {base_url}. "
                "Make sure the application is running with "
                "'make run-local' or 'make run-dev'."
            ) from None
        except httpx.TimeoutException:
            raise TimeoutError(
                f"API request to {url} timed out after {Defaults.API_TIMEOUT} seconds."
            ) from None
        except httpx.HTTPStatusError as e:
            # Handle structured error responses from health endpoint
            if e.response.status_code == 503:
                try:
                    error_data = e.response.json()
                    if "detail" in error_data and isinstance(
                        error_data["detail"], dict
                    ):
                        detail = error_data["detail"]
                        message = detail.get("message", "System is unhealthy")
                        unhealthy_components = detail.get("unhealthy_components", [])
                        health_percentage = detail.get("health_percentage", 0)

                        error_msg = f"{message}"
                        if unhealthy_components:
                            components_str = ", ".join(unhealthy_components)
                            error_msg += f" (Unhealthy: {components_str})"
                        if health_percentage is not None:
                            error_msg += f" - Health: {health_percentage:.1f}%"

                        raise RuntimeError(error_msg) from None
                except (ValueError, KeyError, TypeError):
                    # Fall back to generic error message if JSON parsing fails
                    pass

            raise RuntimeError(
                f"API returned error {e.response.status_code}: {e.response.text}"
            ) from None


async def is_system_healthy() -> bool:
    """Quick check if system is healthy via API."""
    try:
        health_data = await get_health_data(APIEndpoints.HEALTH_BASIC)
        return health_data.healthy
    except Exception:
        return False


@app.command("status")
def health_status(
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed component information"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show system health status (always exits 0 for inspection)."""
    setup_logging()

    try:
        endpoint = (
            APIEndpoints.HEALTH_DETAILED if detailed else APIEndpoints.HEALTH_BASIC
        )
        health_data = asyncio.run(get_health_data(endpoint))

        if json_output:
            print(json.dumps(health_data.model_dump(), indent=2))
        else:
            _display_health_status(health_data, detailed)

        # Always exit 0 for status command (informational)

    except Exception as e:
        if json_output:
            error_data = {"error": str(e), "status": "error"}
            print(json.dumps(error_data, indent=2))
        else:
            console.print(f"[red]❌ Health status failed: {e}[/red]")
        # Exit 1 only on actual errors (connection failures, etc), not unhealthy status
        sys.exit(1)


@app.command("probe")
def health_probe() -> None:
    """Health probe for monitoring - exits 1 if unhealthy (like k8s probes)."""
    setup_logging()

    try:
        healthy = asyncio.run(is_system_healthy())

        if healthy:
            console.print("[green]✅ System is healthy[/green]")
            sys.exit(0)
        else:
            console.print("[red]❌ System is unhealthy[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]💥 Health probe failed: {e}[/red]")
        sys.exit(1)


def _display_sub_components(
    sub_components: dict[str, Any], detailed: bool, level: int
) -> None:
    """Recursively display sub-components with appropriate tree indentation."""
    sub_items = list(sub_components.items())

    # Calculate tree indentation based on level
    base_indent = "   " * level

    for i, (sub_name, sub_component) in enumerate(sub_items):
        sub_icon, sub_color = _get_status_icon_and_color(sub_component.status)

        # Tree connector: ├── for middle items, └── for last item
        is_last = i == len(sub_items) - 1
        tree_connector = f"{base_indent}└── " if is_last else f"{base_indent}├── "

        sub_line = f"{tree_connector}[{sub_color}]{sub_icon} {sub_name}[/{sub_color}]"
        if detailed and sub_component.response_time_ms is not None:
            sub_line += f" ([dim]{sub_component.response_time_ms:.1f}ms[/dim])"
        sub_line += f"    {sub_component.message}"
        console.print(sub_line)

        # Recursively display sub-sub-components
        if hasattr(sub_component, "sub_components") and sub_component.sub_components:
            _display_sub_components(sub_component.sub_components, detailed, level + 1)

        # Show metadata for sub-components if detailed and available
        elif detailed and sub_component.metadata:
            metadata_str = json.dumps(sub_component.metadata, separators=(",", ":"))
            max_length = CLI.MAX_METADATA_DISPLAY_LENGTH
            if len(metadata_str) > max_length:
                metadata_str = metadata_str[: max_length - 3] + "..."
            # Adjust tree indent based on whether this is the last item
            tree_indent = f"{base_indent}    " if is_last else f"{base_indent}│   "
            console.print(f"{tree_indent}[dim]({metadata_str})[/dim]")


def _display_health_status(
    health_data: HealthResponse | DetailedHealthResponse, detailed: bool = False
) -> None:
    """Display health status with rich formatting."""

    # Extract data from Pydantic model
    overall_healthy = health_data.healthy
    components = health_data.components
    timestamp = health_data.timestamp

    # Use health percentage from API response if available (DetailedHealthResponse)
    # Otherwise calculate from top-level components (HealthResponse)
    if hasattr(health_data, "health_percentage"):
        health_percentage = health_data.health_percentage
        # For detailed response, use the component counts from API
        if hasattr(health_data, "healthy_components"):
            if hasattr(health_data, 'unhealthy_components'):
                healthy_count = len(health_data.healthy_components)
                total_count = len(health_data.healthy_components) + len(
                    health_data.unhealthy_components
                )
            else:
                # HealthResponse doesn't have detailed component lists
                healthy_count = 1 if health_data.healthy else 0
                total_count = 1
        else:
            # Fallback for detailed response without component lists
            healthy_count = sum(1 for comp in components.values() if comp.healthy)
            total_count = len(components)
    else:
        # Basic health response - count main sub-components for better overview
        if components and "aegis" in components:
            aegis_component = components["aegis"]
            if (
                hasattr(aegis_component, "sub_components")
                and aegis_component.sub_components
            ):
                healthy_count = sum(
                    1
                    for comp in aegis_component.sub_components.values()
                    if comp.healthy
                )
                total_count = len(aegis_component.sub_components)
                health_percentage = (
                    (healthy_count / total_count) * 100 if total_count > 0 else 100.0
                )
            else:
                # Fallback to aegis component only
                healthy_count = 1 if aegis_component.healthy else 0
                total_count = 1
                health_percentage = 100.0 if aegis_component.healthy else 0.0
        else:
            # No components or no aegis component
            healthy_count = 0
            total_count = 0
            health_percentage = 0.0

    overall_color = "green" if overall_healthy else "red"
    overall_icon = "✅" if overall_healthy else "❌"

    title = f"System Health - {overall_icon}"
    if overall_healthy:
        title += " Healthy"
    else:
        title += " Unhealthy"

    panel_content = [
        f"Overall Status: [bold {overall_color}]"
        + ("Healthy" if overall_healthy else "Unhealthy")
        + f"[/bold {overall_color}]",
        f"Health Percentage: [bold]"
        f"{health_percentage:.{CLI.HEALTH_PERCENTAGE_DECIMALS}f}%[/bold]",
        f"Components: {healthy_count}/" + f"{total_count} healthy",
        f"Timestamp: {timestamp}",
    ]

    console.print(
        Panel("\n".join(panel_content), title=title, border_style=overall_color)
    )

    # Component Tree Display
    console.print("\n[bold magenta]Component Tree:[/bold magenta]")

    # Sort components: unhealthy first, then by name
    sorted_components = sorted(components.items(), key=lambda x: (x[1].healthy, x[0]))

    for name, component in sorted_components:
        status_icon, status_color = _get_status_icon_and_color(component.status)

        # Display main component
        component_line = f"[{status_color}]{status_icon} {name}[/{status_color}]"
        if detailed and component.response_time_ms is not None:
            component_line += f" ([dim]{component.response_time_ms:.1f}ms[/dim])"
        component_line += f"    {component.message}"
        console.print(component_line)

        # Display sub-components with tree structure (recursive)
        if hasattr(component, "sub_components") and component.sub_components:
            _display_sub_components(component.sub_components, detailed, level=1)

        # Show metadata for main components if detailed and available
        elif detailed and component.metadata:
            metadata_str = json.dumps(component.metadata, separators=(",", ":"))
            max_length = CLI.MAX_METADATA_DISPLAY_LENGTH
            if len(metadata_str) > max_length:
                metadata_str = metadata_str[: max_length - 3] + "..."
            console.print(f"    [dim]({metadata_str})[/dim]")

    # System information (only in detailed mode)
    if detailed and isinstance(health_data, DetailedHealthResponse):
        system_info = health_data.system_info
        if system_info:
            sys_info_content = []
            for key, value in system_info.items():
                sys_info_content.append(f"{key.replace('_', ' ').title()}: {value}")

            console.print(
                Panel(
                    "\n".join(sys_info_content),
                    title="System Information",
                    border_style="blue",
                )
            )


if __name__ == "__main__":
    app()
