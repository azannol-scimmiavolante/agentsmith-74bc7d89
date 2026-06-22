"""HTTP client for weatherapi.com."""

from __future__ import annotations

from typing import Any

import requests

from .config import BASE_URL, WEATHER_API_KEY
from .exceptions import WeatherError
from .models import WeatherResponse


class WeatherClient:
    """Thin wrapper around the weatherapi.com REST API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize the WeatherClient.
        
        Args:
            api_key: The weatherapi.com API key. If None, reads from config.
            base_url: The base URL for the API. If None, uses config default.
            timeout: Request timeout in seconds.
            
        Raises:
            WeatherError: If no API key is available.
        """
        self.api_key = api_key if api_key is not None else WEATHER_API_KEY
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.timeout = timeout
        if not self.api_key:
            raise WeatherError(
                "WEATHER_API_KEY is not set.",
                hint="Copy .env.example to .env and set WEATHER_API_KEY to your weatherapi.com key.",
            )

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute an HTTP request to the weather API.

        Args:
            endpoint: The API endpoint path (e.g., 'current.json')
            params: Query parameters to include in the request

        Returns:
            The JSON response as a dictionary

        Raises:
            WeatherError: If the request fails or returns an error status
        """
        url = f"{self.base_url}/{endpoint}"
        full_params = {"key": self.api_key, **params}

        try:
            response = requests.get(url, params=full_params, timeout=self.timeout)
        except requests.Timeout as exc:
            raise WeatherError(
                "Request to the weather service timed out.",
                hint="Check your internet connection and try again.",
            ) from exc
        except requests.ConnectionError as exc:
            raise WeatherError(
                "Could not connect to the weather service.",
                hint="Check your internet connection or try again later.",
            ) from exc
        except requests.RequestException as exc:
            raise WeatherError(
                f"Network error while contacting the weather service: {exc}",
                hint="Try again in a few moments.",
            ) from exc

        # Handle authentication errors
        if response.status_code == 401 or response.status_code == 403:
            raise WeatherError(
                "Invalid or unauthorized weather API key.",
                hint="Verify WEATHER_API_KEY in your .env file matches a valid weatherapi.com key.",
            )

        # Handle bad requests (e.g., city not found)
        if response.status_code == 400:
            api_message = "Bad request"
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    api_message = error_data["error"]["message"]
            except Exception:
                pass
            raise WeatherError(
                f"Invalid request: {api_message}",
                hint="Check the city name spelling or try a more specific location (e.g., 'Paris, FR').",
            )

        # Handle other HTTP errors
        if not response.ok:
            raise WeatherError(
                f"Weather service returned an error (HTTP {response.status_code}).",
                hint="Try again later or check the weatherapi.com service status.",
            )

        try:
            return response.json()
        except requests.JSONDecodeError as exc:
            raise WeatherError(
                "Received invalid data from weather service.",
                hint="Try again in a few moments.",
            ) from exc

    def get_current(self, city: str) -> WeatherResponse:
        """Fetch current weather conditions for a city.

        Args:
            city: The city name or location query

        Returns:
            A WeatherResponse with current conditions populated

        Raises:
            WeatherError: If the request fails or the response is invalid
        """
        data = self._request("current.json", {"q": city, "aqi": "no"})
        try:
            return WeatherResponse(**data)
        except Exception as exc:
            raise WeatherError(
                "Failed to parse weather data from the service.",
                hint="The service may have returned unexpected data. Try again later.",
            ) from exc

    def get_forecast(self, city: str, days: int = 5) -> WeatherResponse:
        """Fetch weather forecast for a city.

        Args:
            city: The city name or location query
            days: Number of forecast days (1-7)

        Returns:
            A WeatherResponse with forecast data populated

        Raises:
            WeatherError: If the request fails or the response is invalid
        """
        if not 1 <= days <= 7:
            raise WeatherError(
                f"Invalid number of forecast days: {days}",
                hint="Forecast days must be between 1 and 7.",
            )
        data = self._request("forecast.json", {"q": city, "days": days, "aqi": "no", "alerts": "no"})
        try:
            return WeatherResponse(**data)
        except Exception as exc:
            raise WeatherError(
                "Failed to parse forecast data from the service.",
                hint="The service may have returned unexpected data. Try again later.",
            ) from exc
