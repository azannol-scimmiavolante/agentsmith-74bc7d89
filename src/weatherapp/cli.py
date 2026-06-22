"""Click-based command-line interface for WeatherApp."""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .client import WeatherClient
from .config import DEFAULT_CITY
from .exceptions import WeatherError
from .formatters import format_current, format_forecast

console = Console()
error_console = Console(stderr=True)


def _render_error(err: WeatherError) -> None:
    """Render a WeatherError as a Rich panel to stderr.
    
    Args:
        err: The WeatherError to display
    """
    body = Text()
    body.append(err.message, style="bold red")
    if err.hint:
        body.append("\n\n")
        body.append(err.hint, style="yellow")
    error_console.print(
        Panel(
            body,
            title="[bold red]Weather Error[/bold red]",
            border_style="red",
            expand=False,
        )
    )


@click.group(help="WeatherApp - current conditions and forecasts from the comfort of your shell.")
def weather() -> None:
    """Top-level command group for weather commands."""
    pass


@weather.command("now")
@click.argument("city", required=False, default=None)
def now(city: str | None) -> None:
    """Show current weather for CITY (defaults to London).
    
    Args:
        city: The city name to get weather for. If None, uses DEFAULT_CITY.
    """
    target = city or DEFAULT_CITY
    try:
        client = WeatherClient()
        response = client.get_current(target)
        format_current(response)
    except WeatherError as err:
        _render_error(err)
        sys.exit(1)


@weather.command("forecast")
@click.argument("city", required=False, default=None)
@click.option(
    "--days",
    type=click.IntRange(1, 7),
    default=5,
    show_default=True,
    help="Number of forecast days (1-7).",
)
def forecast(city: str | None, days: int) -> None:
    """Show a multi-day forecast for CITY (defaults to London).
    
    Args:
        city: The city name to get weather for. If None, uses DEFAULT_CITY.
        days: Number of days to forecast (1-7).
    """
    target = city or DEFAULT_CITY
    try:
        client = WeatherClient()
        response = client.get_forecast(target, days=days)
        format_forecast(response)
    except WeatherError as err:
        _render_error(err)
        sys.exit(1)


if __name__ == "__main__":
    weather()
