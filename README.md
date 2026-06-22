# WeatherApp CLI

A command-line weather application that fetches current conditions and forecasts from [weatherapi.com](https://www.weatherapi.com/), with rich terminal output.

## Features

- Current weather conditions for any city
- Multi-day forecasts (1-7 days) with hourly breakdowns
- Beautiful terminal output using Rich tables and panels
- Temperature in both Celsius and Fahrenheit
- Humidity, wind speed, UV index, and condition descriptions
- User-friendly error messages for network issues, invalid API keys, and unknown cities

## Installation

### Prerequisites

- Python 3.11 or higher
- A free API key from [weatherapi.com](https://www.weatherapi.com/)

### Install from source

```bash
git clone <repository-url>
cd weatherapp
pip install -e .
```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your weatherapi.com API key:

   ```
   WEATHER_API_KEY=your_actual_api_key_here
   ```

## Usage

After installation, the `weatherapp` command is available in your shell.

### Current conditions

```bash
# Default city (London)
weatherapp now

# Specific city
weatherapp now "New York"
weatherapp now Tokyo
weatherapp now Paris
```

### Forecast

```bash
# 5-day forecast (default) for London
weatherapp forecast

# 3-day forecast for a specific city
weatherapp forecast Berlin --days 3

# 7-day forecast
weatherapp forecast "San Francisco" --days 7
```

The `--days` option accepts values from 1 to 7.

## Examples

```bash
$ weatherapp now London
# Displays current temperature, humidity, wind, UV index, condition

$ weatherapp forecast Tokyo --days 3
# Displays a 3-day forecast with daily highs/lows and hourly breakdowns
```

## Development

### Run tests

```bash
pip install pytest
pytest tests/
```

### Project structure

```
src/weatherapp/
  __init__.py
  __main__.py       # Module entrypoint
  cli.py            # Click CLI commands
  client.py         # WeatherClient HTTP client
  config.py         # Environment configuration
  exceptions.py     # WeatherError exception class
  formatters.py     # Rich-based output formatters
  models.py         # Pydantic data models
tests/
  test_client.py    # Client unit tests
```

## Troubleshooting

- **"WEATHER_API_KEY not set"** — Ensure your `.env` file exists in the working directory and contains a valid key.
- **"Invalid API key"** — Verify your key at [weatherapi.com](https://www.weatherapi.com/my/).
- **"City not found"** — Check spelling and try a more specific name (e.g. `"Paris, FR"`).
- **Network timeouts** — Check your internet connection and try again.

## License

MIT
