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
                        "temp_c": 8.0 + i * 0.5,
                        "temp_f": 46.4 + i * 0.9,
                        "is_day": 1 if 6 <= i <= 18 else 0,
                        "condition": {
                            "text": "Clear",
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
                        "cloud": 10,
                        "feelslike_c": 7.0 + i * 0.5,
                        "feelslike_f": 44.6 + i * 0.9,
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
    """Test suite for WeatherClient."""

    @patch("weatherapp.client.requests.get")
    def test_get_current_success(self, mock_get: MagicMock) -> None:
        """Test that get_current returns a valid WeatherResponse on success."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act
        result = client.get_current("London")

        # Assert
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

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("current.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], "test_key")
        self.assertEqual(call_args[1]["params"]["q"], "London")

    @patch("weatherapp.client.requests.get")
    def test_get_current_401_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 401 response raises WeatherError with appropriate message."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="invalid_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        error = context.exception
        self.assertIn("Invalid or unauthorized", error.message)
        self.assertIn("API key", error.message)
        self.assertIsNotNone(error.hint)
        self.assertIn("WEATHER_API_KEY", error.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_403_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 403 response raises WeatherError with appropriate message."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="forbidden_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        error = context.exception
        self.assertIn("Invalid or unauthorized", error.message)
        self.assertIn("API key", error.message)

    @patch("weatherapp.client.requests.get")
    def test_get_current_400_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 400 response (e.g., city not found) raises WeatherError."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("InvalidCityXYZ123")

        error = context.exception
        self.assertIn("No matching location found", error.message)
        self.assertIsNotNone(error.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_timeout_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a timeout raises WeatherError with timeout message."""
        # Arrange
        mock_get.side_effect = requests.Timeout("Connection timed out")

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        error = context.exception
        self.assertIn("timed out", error.message)
        self.assertIsNotNone(error.hint)
        self.assertIn("internet connection", error.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_connection_error_raises_weather_error(
        self, mock_get: MagicMock
    ) -> None:
        """Test that a connection error raises WeatherError."""
        # Arrange
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        error = context.exception
        self.assertIn("Could not connect", error.message)
        self.assertIsNotNone(error.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_success(self, mock_get: MagicMock) -> None:
        """Test that get_forecast returns a valid WeatherResponse with forecast data."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act
        result = client.get_forecast("London", days=1)

        # Assert
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
        self.assertIsNotNone(day.astro)
        self.assertEqual(day.astro.sunrise, "07:15 AM")

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("forecast.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], "test_key")
        self.assertEqual(call_args[1]["params"]["q"], "London")
        self.assertEqual(call_args[1]["params"]["days"], 1)

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_401_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 401 response in get_forecast raises WeatherError."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="invalid_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_forecast("London", days=3)

        error = context.exception
        self.assertIn("Invalid or unauthorized", error.message)

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_400_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 400 response in get_forecast raises WeatherError."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid city name."}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_forecast("InvalidCity", days=5)

        error = context.exception
        self.assertIn("Invalid city name", error.message)

    def test_client_initialization_without_api_key_raises_error(self) -> None:
        """Test that WeatherClient raises WeatherError if no API key is provided."""
        # Act & Assert
        with patch("weatherapp.client.WEATHER_API_KEY", None):
            with self.assertRaises(WeatherError) as context:
                WeatherClient()

            error = context.exception
            self.assertIn("WEATHER_API_KEY is not set", error.message)
            self.assertIsNotNone(error.hint)
            self.assertIn(".env", error.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_500_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test that a 500 server error raises WeatherError."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        error = context.exception
        self.assertIn("HTTP 500", error.message)


if __name__ == "__main__":
    unittest.main()
