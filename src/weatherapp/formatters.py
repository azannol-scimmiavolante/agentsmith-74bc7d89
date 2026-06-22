"""Rich-based formatters for weather data display."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import WeatherResponse

console = Console()


def _location_title(response: WeatherResponse) -> str:
    """Build a human-readable location title from the response."""
    loc = response.location
    parts = [loc.name]
    if getattr(loc, "region", None):
        parts.append(loc.region)
    if getattr(loc, "country", None):
        parts.append(loc.country)
    label = ", ".join(p for p in parts if p)
    if getattr(loc, "localtime", None):
        label = f"{label} \u2014 {loc.localtime}"
    return label


def format_current(response: WeatherResponse) -> None:
    """Render the current conditions for a WeatherResponse as a Rich Panel.
    
    Args:
        response: The weather response containing current conditions
        
    Raises:
        ValueError: If the response has no current conditions
    """
    current = response.current
    if current is None:
        raise ValueError("WeatherResponse has no current conditions to format")

    condition_text = current.condition.text if current.condition else ""
    condition_icon = current.condition.icon if current.condition else ""

    table = Table(show_header=False, box=None, pad_edge=False, expand=False)
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Condition", f"{condition_text}")
    if condition_icon:
        table.add_row("Icon", condition_icon)
    table.add_row(
        "Temperature",
        f"{current.temp_c:.1f} \u00b0C / {current.temp_f:.1f} \u00b0F",
    )
    if (
        getattr(current, "feelslike_c", None) is not None
        and getattr(current, "feelslike_f", None) is not None
    ):
        table.add_row(
            "Feels like",
            f"{current.feelslike_c:.1f} \u00b0C / {current.feelslike_f:.1f} \u00b0F",
        )
    table.add_row("Humidity", f"{current.humidity}%")
    table.add_row(
        "Wind",
        f"{current.wind_kph:.1f} kph / {current.wind_mph:.1f} mph ({current.wind_dir})",
    )
    if getattr(current, "pressure_mb", None) is not None:
        table.add_row(
            "Pressure",
            f"{current.pressure_mb:.0f} mb / {current.pressure_in:.2f} in",
        )
    table.add_row("UV Index", f"{current.uv}")

    panel = Panel(
        table,
        title=f"[bold yellow]Current weather \u2014 {_location_title(response)}[/bold yellow]",
        border_style="blue",
        expand=False,
    )
    console.print(panel)


def format_forecast(response: WeatherResponse) -> None:
    """Render daily + hourly forecast for a WeatherResponse as Rich Panels.
    
    Args:
        response: The weather response containing forecast data
        
    Raises:
        ValueError: If the response has no forecast data
    """
    if not response.forecast or not response.forecast.forecastday:
        raise ValueError("WeatherResponse has no forecast data to format")

    # Display location and date range
    location_label = _location_title(response)
    num_days = len(response.forecast.forecastday)
    title = f"[bold yellow]{num_days}-Day Forecast \u2014 {location_label}[/bold yellow]"
    
    # Build a daily summary table
    daily_table = Table(title="Daily Summary", box=None, expand=False)
    daily_table.add_column("Date", style="bold cyan", no_wrap=True)
    daily_table.add_column("Condition", style="white")
    daily_table.add_column("High / Low", style="white", justify="right")
    daily_table.add_column("Precip", style="white", justify="right")
    daily_table.add_column("Humidity", style="white", justify="right")
    daily_table.add_column("UV", style="white", justify="right")

    for day_forecast in response.forecast.forecastday:
        day = day_forecast.day
        condition_text = day.condition.text if day.condition else ""
        high_low = f"{day.maxtemp_c:.1f}\u00b0C / {day.mintemp_c:.1f}\u00b0C"
        precip = f"{day.totalprecip_mm:.1f} mm"
        humidity = f"{day.avghumidity:.0f}%"
        uv = f"{day.uv}"
        
        daily_table.add_row(
            day_forecast.date,
            condition_text,
            high_low,
            precip,
            humidity,
            uv,
        )

    console.print(Panel(daily_table, title=title, border_style="blue", expand=False))
    console.print()

    # Display hourly breakdown for each day
    for day_forecast in response.forecast.forecastday:
        hourly_title = f"[bold green]Hourly Forecast for {day_forecast.date}[/bold green]"
        
        hourly_table = Table(box=None, expand=False)
        hourly_table.add_column("Time", style="bold cyan", no_wrap=True)
        hourly_table.add_column("Condition", style="white")
        hourly_table.add_column("Temp", style="white", justify="right")
        hourly_table.add_column("Wind", style="white", justify="right")
        hourly_table.add_column("Humidity", style="white", justify="right")
        hourly_table.add_column("Rain", style="white", justify="right")

        for hour in day_forecast.hour:
            # Extract just the time portion (HH:MM)
            time_str = hour.time.split()[1] if " " in hour.time else hour.time
            condition_text = hour.condition.text if hour.condition else ""
            temp = f"{hour.temp_c:.1f}\u00b0C"
            wind = f"{hour.wind_kph:.0f} kph {hour.wind_dir}"
            humidity = f"{hour.humidity}%"
            rain_chance = f"{hour.chance_of_rain}%"

            hourly_table.add_row(
                time_str,
                condition_text,
                temp,
                wind,
                humidity,
                rain_chance,
            )

        console.print(Panel(hourly_table, title=hourly_title, border_style="green", expand=False))
        console.print()
