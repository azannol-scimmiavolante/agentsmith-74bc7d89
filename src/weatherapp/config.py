"""Configuration module for WeatherApp.

Loads environment variables from .env and exposes runtime configuration
constants used by the rest of the application.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Weather API key from environment
WEATHER_API_KEY: str | None = os.getenv("WEATHER_API_KEY")

# Default city when none is specified
DEFAULT_CITY: str = "London"

# Base URL for the weatherapi.com API
BASE_URL: str = "http://api.weatherapi.com/v1"
