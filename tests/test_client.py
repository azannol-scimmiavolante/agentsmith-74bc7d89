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
                        "temp_c": 10.0 + i * 0.5,
                        "temp_f": 50.0 + i * 0.9,
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
                        "humidity": 72,
                        "cloud": 10,
                        "feelslike_c": 9.0,
                        "feelslike_f": 48.2,
                        "windchill_c": 8.5,
                        "windchill_f": 47.3,
                        "heatindex_c": 10.0,
                        "heatindex_f": 50.0,
                        "dewpoint_c": 5.0,
                        "dewpoint_f": 41.0,
                        "will_it_rain": 0,
                        "chance_of_rain": 0,
                        "will_it_snow": 0,
                        "chance_of_snow": 0,
                        "vis_km": 10.0,
                        "vis_miles": 6.0,
                        "gust_mph": 7.0,
                        "gust_kph": 11.0,
                        "uv": 1.0,
                    }
                    for i in range(24)
                ],
            }
        ]
    },
}


class TestWeatherClient(unittest.TestCase):
    """Test cases for the WeatherClient class."""

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
        self.assertEqual(result.forecast.forecastday[0].date, "2023-11-14")
        self.assertEqual(result.forecast.forecastday[0].day.maxtemp_c, 12.0)
        self.assertEqual(result.forecast.forecastday[0].day.mintemp_c, 5.0)
        self.assertEqual(len(result.forecast.forecastday[0].hour), 24)

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("forecast.json", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["key"], "test_key")
        self.assertEqual(call_args[1]["params"]["q"], "London")
        self.assertEqual(call_args[1]["params"]["days"], 1)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_401(self, mock_get: MagicMock) -> None:
        """Test that get_current raises WeatherError on 401 (unauthorized)."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "API key invalid"}}
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="invalid_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(context.exception))
        self.assertIn("API key", context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_403(self, mock_get: MagicMock) -> None:
        """Test that get_current raises WeatherError on 403 (forbidden)."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": {"message": "Access denied"}}
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="forbidden_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Invalid or unauthorized", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_400(self, mock_get: MagicMock) -> None:
        """Test that get_current raises WeatherError on 400 (bad request, e.g., city not found)."""
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
            client.get_current("InvalidCityName123")

        self.assertIn("No matching location found", str(context.exception))
        self.assertIn("city name", context.exception.hint.lower())

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_raises_on_400(self, mock_get: MagicMock) -> None:
        """Test that get_forecast raises WeatherError on 400."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Parameter q is missing."}
        }
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_forecast("", days=3)

        self.assertIn("Parameter q is missing", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_timeout(self, mock_get: MagicMock) -> None:
        """Test that get_current raises WeatherError on request timeout."""
        # Arrange
        mock_get.side_effect = requests.Timeout("Request timed out")

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("timed out", str(context.exception).lower())
        self.assertIn("internet connection", context.exception.hint.lower())

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_connection_error(self, mock_get: MagicMock) -> None:
        """Test that get_current raises WeatherError on connection error."""
        # Arrange
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Could not connect", str(context.exception))
        self.assertIn("internet connection", context.exception.hint.lower())

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_on_generic_request_exception(
        self, mock_get: MagicMock
    ) -> None:
        """Test that get_current raises WeatherError on generic request exceptions."""
        # Arrange
        mock_get.side_effect = requests.RequestException("Something went wrong")

        client = WeatherClient(api_key="test_key")

        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        self.assertIn("Network error", str(context.exception))

    def test_client_raises_on_missing_api_key(self) -> None:
        """Test that WeatherClient raises WeatherError when no API key is provided."""
        # Act & Assert
        with self.assertRaises(WeatherError) as context:
            WeatherClient(api_key="")

        self.assertIn("WEATHER_API_KEY is not set", str(context.exception))
        self.assertIn(".env", context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_custom_timeout(self, mock_get: MagicMock) -> None:
        """Test that custom timeout is passed to requests.get."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key", timeout=5.0)

        # Act
        client.get_current("London")

        # Assert
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["timeout"], 5.0)

    @patch("weatherapp.client.requests.get")
    def test_get_current_with_custom_base_url(self, mock_get: MagicMock) -> None:
        """Test that custom base URL is used in requests."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        custom_url = "https://custom.api.com/v1"
        client = WeatherClient(api_key="test_key", base_url=custom_url)

        # Act
        client.get_current("London")

        # Assert
        call_args = mock_get.call_args
        self.assertIn("custom.api.com", call_args[0][0])

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_with_multiple_days(self, mock_get: MagicMock) -> None:
        """Test that get_forecast correctly passes the days parameter."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
        mock_get.return_value = mock_response

        client = WeatherClient(api_key="test_key")

        # Act
        client.get_forecast("Tokyo", days=7)

        # Assert
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"]["days"], 7)
        self.assertEqual(call_args[1]["params"]["q"], "Tokyo")


if __name__ == "__main__":
    unittest.main()
