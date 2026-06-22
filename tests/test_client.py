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
                        "is_day": 1 if 7 <= i < 17 else 0,
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
                        "cloud": 20,
                        "feelslike_c": 7.5 + i * 0.2,
                        "feelslike_f": 45.5 + i * 0.36,
                        "windchill_c": 7.0 + i * 0.2,
                        "windchill_f": 44.6 + i * 0.36,
                        "heatindex_c": 8.0 + i * 0.2,
                        "heatindex_f": 46.4 + i * 0.36,
                        "dewpoint_c": 4.0,
                        "dewpoint_f": 39.2,
                        "will_it_rain": 0,
                        "chance_of_rain": 0,
                        "will_it_snow": 0,
                        "chance_of_snow": 0,
                        "vis_km": 10.0,
                        "vis_miles": 6.0,
                        "gust_mph": 7.0,
                        "gust_kph": 11.0,
                        "uv": 2.0 if 7 <= i < 17 else 0.0,
                    }
                    for i in range(24)
                ],
            }
        ]
    },
}


class TestWeatherClient(unittest.TestCase):
    """Test suite for the WeatherClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_12345"
        self.base_url = "http://api.weatherapi.com/v1"

    @patch("weatherapp.client.requests.get")
    def test_get_current_returns_correct_weather_response(self, mock_get):
        """Test that get_current returns a valid WeatherResponse on success."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

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
        self.assertEqual(result.current.uv, 1.0)

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("current.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], self.api_key)
        self.assertEqual(call_args[1]["params"]["q"], "London")

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_weather_error_on_401(self, mock_get):
        """Test that get_current raises WeatherError on 401 Unauthorized."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"code": 2006, "message": "API key is invalid."}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="bad_key", base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(ctx.exception))
        self.assertIn("API key", ctx.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_weather_error_on_403(self, mock_get):
        """Test that get_current raises WeatherError on 403 Forbidden."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="forbidden_key", base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(ctx.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_weather_error_on_400(self, mock_get):
        """Test that get_current raises WeatherError on 400 Bad Request."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"code": 1006, "message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("InvalidCityXYZ123")

        self.assertIn("No matching location found", str(ctx.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_weather_error_on_timeout(self, mock_get):
        """Test that get_current raises WeatherError on request timeout."""
        # Arrange
        mock_get.side_effect = requests.Timeout("Connection timed out")

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("London")

        self.assertIn("timed out", str(ctx.exception))
        self.assertIn("internet connection", ctx.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_weather_error_on_connection_error(self, mock_get):
        """Test that get_current raises WeatherError on connection error."""
        # Arrange
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("London")

        self.assertIn("Could not connect", str(ctx.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_returns_correct_weather_response(self, mock_get):
        """Test that get_forecast returns a valid WeatherResponse with forecast data."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act
        result = client.get_forecast("London", days=3)

        # Assert
        self.assertIsInstance(result, WeatherResponse)
        self.assertEqual(result.location.name, "London")
        self.assertIsNotNone(result.current)
        self.assertIsNotNone(result.forecast)
        self.assertGreater(len(result.forecast.forecastday), 0)
        self.assertEqual(result.forecast.forecastday[0].date, "2023-11-14")
        self.assertEqual(result.forecast.forecastday[0].day.maxtemp_c, 12.0)
        self.assertEqual(len(result.forecast.forecastday[0].hour), 24)

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("forecast.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], self.api_key)
        self.assertEqual(call_args[1]["params"]["q"], "London")
        self.assertEqual(call_args[1]["params"]["days"], 3)

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_raises_weather_error_on_401(self, mock_get):
        """Test that get_forecast raises WeatherError on 401 Unauthorized."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="invalid_key", base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_forecast("London", days=5)

        self.assertIn("Invalid or unauthorized", str(ctx.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_raises_weather_error_on_400(self, mock_get):
        """Test that get_forecast raises WeatherError on 400 Bad Request."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"code": 1006, "message": "No location found"}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_forecast("NonexistentCity", days=5)

        self.assertIn("No location found", str(ctx.exception))

    def test_client_raises_error_when_no_api_key(self):
        """Test that WeatherClient raises WeatherError when no API key is provided."""
        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            WeatherClient(api_key=None, base_url=self.base_url)

        self.assertIn("WEATHER_API_KEY is not set", str(ctx.exception))
        self.assertIn(".env", ctx.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_handles_500_error(self, mock_get):
        """Test that get_current raises WeatherError on 500 server error."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act & Assert
        with self.assertRaises(WeatherError) as ctx:
            client.get_current("London")

        self.assertIn("Server error", str(ctx.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_aqi_parameter(self, mock_get):
        """Test that get_current passes through additional parameters."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key=self.api_key, base_url=self.base_url)

        # Act
        result = client.get_current("London")

        # Assert
        self.assertIsInstance(result, WeatherResponse)
        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
