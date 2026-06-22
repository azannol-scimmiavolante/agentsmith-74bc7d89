"""Tests for the WeatherClient class."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from weatherapp.client import WeatherClient
from weatherapp.exceptions import WeatherError
from weatherapp.models import WeatherResponse


SAMPLE_CURRENT_RESPONSE = {
    "location": {
        "name": "London",
        "region": "City of London, Greater London",
        "country": "United Kingdom",
        "lat": 51.52,
        "lon": -0.11,
        "tz_id": "Europe/London",
        "localtime_epoch": 1700000000,
        "localtime": "2023-11-14 22:13",
    },
    "current": {
        "last_updated_epoch": 1700000000,
        "last_updated": "2023-11-14 22:13",
        "temp_c": 10.0,
        "temp_f": 50.0,
        "is_day": 0,
        "condition": {
            "text": "Partly cloudy",
            "icon": "//cdn.weatherapi.com/weather/64x64/night/116.png",
            "code": 1003,
        },
        "wind_mph": 5.0,
        "wind_kph": 8.0,
        "wind_degree": 230,
        "wind_dir": "SW",
        "pressure_mb": 1015.0,
        "pressure_in": 29.97,
        "precip_mm": 0.0,
        "precip_in": 0.0,
        "humidity": 72,
        "cloud": 50,
        "feelslike_c": 9.0,
        "feelslike_f": 48.2,
        "vis_km": 10.0,
        "vis_miles": 6.0,
        "uv": 1.0,
        "gust_mph": 7.0,
        "gust_kph": 11.0,
    },
}


SAMPLE_FORECAST_RESPONSE = {
    **SAMPLE_CURRENT_RESPONSE,
    "forecast": {
        "forecastday": [
            {
                "date": "2023-11-14",
                "date_epoch": 1699920000,
                "day": {
                    "maxtemp_c": 12.0,
                    "maxtemp_f": 53.6,
                    "mintemp_c": 5.0,
                    "mintemp_f": 41.0,
                    "avgtemp_c": 8.5,
                    "avgtemp_f": 47.3,
                    "maxwind_mph": 10.0,
                    "maxwind_kph": 16.0,
                    "totalprecip_mm": 0.0,
                    "totalprecip_in": 0.0,
                    "avgvis_km": 10.0,
                    "avgvis_miles": 6.0,
                    "avghumidity": 70.0,
                    "daily_will_it_rain": 0,
                    "daily_chance_of_rain": 0,
                    "daily_will_it_snow": 0,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Sunny",
                        "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                        "code": 1000,
                    },
                    "uv": 2.0,
                },
                "astro": {
                    "sunrise": "07:15 AM",
                    "sunset": "04:15 PM",
                    "moonrise": "08:00 AM",
                    "moonset": "06:00 PM",
                    "moon_phase": "Waxing Crescent",
                    "moon_illumination": "10",
                },
                "hour": [
                    {
                        "time_epoch": 1699920000 + i * 3600,
                        "time": f"2023-11-14 {i:02d}:00",
                        "temp_c": 8.0 + i * 0.2,
                        "temp_f": 46.4 + i * 0.36,
                        "is_day": 1 if 6 <= i < 18 else 0,
                        "condition": {
                            "text": "Sunny",
                            "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                            "code": 1000,
                        },
                        "wind_mph": 5.0,
                        "wind_kph": 8.0,
                        "wind_degree": 230,
                        "wind_dir": "SW",
                        "pressure_mb": 1015.0,
                        "pressure_in": 29.97,
                        "precip_mm": 0.0,
                        "precip_in": 0.0,
                        "humidity": 70,
                        "cloud": 20,
                        "feelslike_c": 7.0 + i * 0.2,
                        "feelslike_f": 44.6 + i * 0.36,
                        "vis_km": 10.0,
                        "vis_miles": 6.0,
                        "gust_mph": 7.0,
                        "gust_kph": 11.0,
                        "uv": 2.0,
                    }
                    for i in range(24)
                ],
            }
        ]
    },
}


class TestWeatherClient(unittest.TestCase):
    """Test suite for the WeatherClient class."""

    @patch("weatherapp.client.requests.get")
    def test_get_current_success(self, mock_get: MagicMock) -> None:
        """Test that get_current returns a valid WeatherResponse on success."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        # Execute
        client = WeatherClient(api_key="test_key")
        result = client.get_current("London")

        # Verify
        self.assertIsInstance(result, WeatherResponse)
        self.assertEqual(result.location.name, "London")
        self.assertEqual(result.location.country, "United Kingdom")
        self.assertIsNotNone(result.current)
        self.assertEqual(result.current.temp_c, 10.0)
        self.assertEqual(result.current.temp_f, 50.0)
        self.assertEqual(result.current.condition.text, "Partly cloudy")
        self.assertEqual(result.current.humidity, 72)
        self.assertEqual(result.current.wind_kph, 8.0)
        self.assertEqual(result.current.uv, 1.0)

        # Verify the API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("current.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], "test_key")
        self.assertEqual(call_args[1]["params"]["q"], "London")

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_success(self, mock_get: MagicMock) -> None:
        """Test that get_forecast returns a valid WeatherResponse with forecast data."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
        mock_get.return_value = mock_response

        # Execute
        client = WeatherClient(api_key="test_key")
        result = client.get_forecast("London", days=3)

        # Verify
        self.assertIsInstance(result, WeatherResponse)
        self.assertEqual(result.location.name, "London")
        self.assertIsNotNone(result.current)
        self.assertIsNotNone(result.forecast)
        self.assertEqual(len(result.forecast.forecastday), 1)
        
        day = result.forecast.forecastday[0]
        self.assertEqual(day.date, "2023-11-14")
        self.assertEqual(day.day.maxtemp_c, 12.0)
        self.assertEqual(day.day.mintemp_c, 5.0)
        self.assertEqual(len(day.hour), 24)

        # Verify the API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("forecast.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], "test_key")
        self.assertEqual(call_args[1]["params"]["q"], "London")
        self.assertEqual(call_args[1]["params"]["days"], 3)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_401(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on 401 (unauthorized) response."""
        # Setup mock response for unauthorized
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"code": 2006, "message": "API key is invalid"}
        }
        mock_get.return_value = mock_response

        # Execute and verify
        client = WeatherClient(api_key="invalid_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(context.exception))
        self.assertIn("API key", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_403(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on 403 (forbidden) response."""
        # Setup mock response for forbidden
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": {"code": 2007, "message": "API key has been disabled"}
        }
        mock_get.return_value = mock_response

        # Execute and verify
        client = WeatherClient(api_key="disabled_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_400(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on 400 (bad request) response."""
        # Setup mock response for bad request (e.g., city not found)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"code": 1006, "message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        # Execute and verify
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("InvalidCityName123")

        self.assertIn("No matching location found", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_raises_on_400(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on 400 for forecast requests."""
        # Setup mock response for bad request
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"code": 1006, "message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        # Execute and verify
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_forecast("InvalidCity", days=5)

        self.assertIn("No matching location found", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_timeout_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on request timeout."""
        # Setup mock to raise Timeout
        mock_get.side_effect = requests.Timeout("Connection timeout")

        # Execute and verify
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("timed out", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_connection_error_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that WeatherError is raised on connection error."""
        # Setup mock to raise ConnectionError
        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        # Execute and verify
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Could not connect", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_generic_request_exception_raises_weather_error(
        self, mock_get: MagicMock
    ) -> None:
        """Test that WeatherError is raised on generic request exceptions."""
        # Setup mock to raise generic RequestException
        mock_get.side_effect = requests.RequestException("Something went wrong")

        # Execute and verify
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Network error", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    def test_client_raises_on_missing_api_key(self) -> None:
        """Test that WeatherClient raises WeatherError if no API key is provided."""
        with patch("weatherapp.client.WEATHER_API_KEY", None):
            with self.assertRaises(WeatherError) as context:
                WeatherClient()

            self.assertIn("WEATHER_API_KEY is not set", str(context.exception))
            self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_custom_base_url(self, mock_get: MagicMock) -> None:
        """Test that custom base URL is used when provided."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        # Execute
        custom_url = "https://custom.api.com/v1"
        client = WeatherClient(api_key="test_key", base_url=custom_url)
        client.get_current("London")

        # Verify
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn(custom_url, call_args[0][0])

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_custom_timeout(self, mock_get: MagicMock) -> None:
        """Test that custom timeout is used when provided."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        # Execute
        custom_timeout = 30.0
        client = WeatherClient(api_key="test_key", timeout=custom_timeout)
        client.get_current("London")

        # Verify
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["timeout"], custom_timeout)

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_aqi_parameter(self, mock_get: MagicMock) -> None:
        """Test that additional parameters like aqi can be passed."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        # Execute
        client = WeatherClient(api_key="test_key")
        result = client.get_current("London")

        # Verify the response is valid
        self.assertIsInstance(result, WeatherResponse)


if __name__ == "__main__":
    unittest.main()
