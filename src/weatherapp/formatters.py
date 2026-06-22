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

    # Print title panel
    title_text = Text()
    title_text.append("Forecast \u2014 ", style="bold yellow")
    title_text.append(_location_title(response), style="bold yellow")
    console.print()
    console.print(Panel(title_text, border_style="blue", expand=False))
    console.print()

    # Iterate through each forecast day
    for day_forecast in response.forecast.forecastday:
        day = day_forecast.day
        date_str = day_forecast.date
        
        # Build daily summary table
        daily_table = Table(show_header=False, box=None, pad_edge=False, expand=False)
        daily_table.add_column("Field", style="bold cyan", no_wrap=True)
        daily_table.add_column("Value", style="white")

        # Condition
        condition_text = day.condition.text if day.condition else ""
        condition_icon = day.condition.icon if day.condition else ""
        daily_table.add_row("Condition", condition_text)
        if condition_icon:
            daily_table.add_row("Icon", condition_icon)

        # Temperature range
        daily_table.add_row(
            "High",
            f"{day.maxtemp_c:.1f} \u00b0C / {day.maxtemp_f:.1f} \u00b0F",
        )
        daily_table.add_row(
            "Low",
            f"{day.mintemp_c:.1f} \u00b0C / {day.mintemp_f:.1f} \u00b0F",
        )
        daily_table.add_row(
            "Avg",
            f"{day.avgtemp_c:.1f} \u00b0C / {day.avgtemp_f:.1f} \u00b0F",
        )

        # Humidity
        daily_table.add_row("Avg Humidity", f"{day.avghumidity:.0f}%")

        # Wind
        daily_table.add_row(
            "Max Wind",
            f"{day.maxwind_kph:.1f} kph / {day.maxwind_mph:.1f} mph",
        )

        # Precipitation
        if day.totalprecip_mm > 0 or day.totalprecip_in > 0:
            daily_table.add_row(
                "Precipitation",
                f"{day.totalprecip_mm:.1f} mm / {day.totalprecip_in:.2f} in",
            )

        # UV Index
        daily_table.add_row("UV Index", f"{day.uv}")

        # Rain/Snow chance
        if day.daily_chance_of_rain > 0:
            daily_table.add_row("Chance of Rain", f"{day.daily_chance_of_rain}%")
        if day.daily_chance_of_snow > 0:
            daily_table.add_row("Chance of Snow", f"{day.daily_chance_of_snow}%")

        # Astro data if available
        if day_forecast.astro:
            astro = day_forecast.astro
            if astro.sunrise and astro.sunset:
                daily_table.add_row(
                    "Sunrise/Sunset",
                    f"{astro.sunrise} / {astro.sunset}",
                )
            if astro.moon_phase:
                moon_info = astro.moon_phase
                if astro.moon_illumination:
                    moon_info += f" ({astro.moon_illumination}%)"
                daily_table.add_row("Moon", moon_info)

        # Print daily panel
        daily_panel = Panel(
            daily_table,
            title=f"[bold green]{date_str}[/bold green]",
            border_style="green",
            expand=False,
        )
        console.print(daily_panel)

        # Build hourly forecast table
        if day_forecast.hour:
            hourly_table = Table(
                show_header=True,
                box=None,
                pad_edge=False,
                expand=False,
                header_style="bold magenta",
            )
            hourly_table.add_column("Time", style="cyan", no_wrap=True)
            hourly_table.add_column("Temp", justify="right")
            hourly_table.add_column("Condition", style="yellow")
            hourly_table.add_column("Wind", justify="right")
            hourly_table.add_column("Humid", justify="right")
            hourly_table.add_column("UV", justify="right")

            # Show a subset of hourly data (every 3 hours to keep it readable)
            step = 3
            for hour in day_forecast.hour[::step]:
                time_str = hour.time.split()[1] if " " in hour.time else hour.time
                temp_str = f"{hour.temp_c:.1f}\u00b0C"
                condition_str = hour.condition.text if hour.condition else ""
                wind_str = f"{hour.wind_kph:.0f} kph {hour.wind_dir}"
                humid_str = f"{hour.humidity}%"
                uv_str = f"{hour.uv}"

                hourly_table.add_row(
                    time_str,
                    temp_str,
                    condition_str,
                    wind_str,
                    humid_str,
                    uv_str,
                )

            hourly_panel = Panel(
                hourly_table,
                title="[bold magenta]Hourly Breakdown (every 3 hours)[/bold magenta]",
                border_style="magenta",
                expand=False,
            )
            console.print(hourly_panel)

        console.print()
