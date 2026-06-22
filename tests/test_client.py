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
                        "cloud": 25,
                        "feelslike_c": 7.0 + i * 0.2,
                        "feelslike_f": 44.6 + i * 0.36,
                        "windchill_c": 7.0,
                        "windchill_f": 44.6,
                        "heatindex_c": 8.0,
                        "heatindex_f": 46.4,
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
                        "uv": 1.0 if 6 <= i < 18 else 0.0,
                    }
                    for i in range(24)
                ],
            }
        ]
    },
}


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient."""

    @patch("weatherapp.client.requests.get")
    def test_get_current_success(self, mock_get: MagicMock) -> None:
        """Test get_current returns correct WeatherResponse on success."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_CURRENT_RESPONSE
        mock_get.return_value = mock_response

        # Call the method
        client = WeatherClient(api_key="test_key")
        result = client.get_current("London")

        # Assertions
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
        args, kwargs = mock_get.call_args
        self.assertIn("current.json", args[0])
        self.assertEqual(kwargs["params"]["key"], "test_key")
        self.assertEqual(kwargs["params"]["q"], "London")

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_success(self, mock_get: MagicMock) -> None:
        """Test get_forecast returns correct WeatherResponse with forecast data."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
        mock_get.return_value = mock_response

        # Call the method
        client = WeatherClient(api_key="test_key")
        result = client.get_forecast("London", days=3)

        # Assertions
        self.assertIsInstance(result, WeatherResponse)
        self.assertEqual(result.location.name, "London")
        self.assertIsNotNone(result.current)
        self.assertIsNotNone(result.forecast)
        self.assertEqual(len(result.forecast.forecastday), 1)
        
        # Check forecast day details
        forecast_day = result.forecast.forecastday[0]
        self.assertEqual(forecast_day.date, "2023-11-14")
        self.assertEqual(forecast_day.day.maxtemp_c, 12.0)
        self.assertEqual(forecast_day.day.mintemp_c, 5.0)
        self.assertEqual(len(forecast_day.hour), 24)

        # Verify the request was made correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("forecast.json", args[0])
        self.assertEqual(kwargs["params"]["key"], "test_key")
        self.assertEqual(kwargs["params"]["q"], "London")
        self.assertEqual(kwargs["params"]["days"], 3)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_error_on_401(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on 401 Unauthorized response."""
        # Setup mock response for 401
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_get.return_value = mock_response

        # Call and assert exception
        client = WeatherClient(api_key="invalid_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("Invalid or unauthorized", str(context.exception))
        self.assertIn("API key", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_error_on_403(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on 403 Forbidden response."""
        # Setup mock response for 403
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": {"message": "Access denied"}}
        mock_get.return_value = mock_response

        # Call and assert exception
        client = WeatherClient(api_key="forbidden_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("Invalid or unauthorized", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_current_raises_error_on_400(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on 400 Bad Request response (e.g., city not found)."""
        # Setup mock response for 400
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("InvalidCityName12345")

        # Check error message contains the API error
        self.assertIn("No matching location found", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_get_forecast_raises_error_on_400(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on 400 for get_forecast."""
        # Setup mock response for 400
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Parameter q is missing."}
        }
        mock_get.return_value = mock_response

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_forecast("", days=5)

        # Check error message
        self.assertIn("Parameter q is missing", str(context.exception))

    @patch("weatherapp.client.requests.get")
    def test_timeout_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised when request times out."""
        # Setup mock to raise Timeout
        mock_get.side_effect = requests.Timeout("Connection timed out")

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("timed out", str(context.exception))
        self.assertIsNotNone(context.exception.hint)
        self.assertIn("internet connection", context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_connection_error_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on connection error."""
        # Setup mock to raise ConnectionError
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("Could not connect", str(context.exception))
        self.assertIsNotNone(context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_request_exception_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on generic request exception."""
        # Setup mock to raise generic RequestException
        mock_get.side_effect = requests.RequestException("Unknown error")

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("Network error", str(context.exception))

    def test_no_api_key_raises_weather_error(self) -> None:
        """Test WeatherError is raised when no API key is provided."""
        with self.assertRaises(WeatherError) as context:
            WeatherClient(api_key="")

        self.assertIn("WEATHER_API_KEY is not set", str(context.exception))
        self.assertIsNotNone(context.exception.hint)
        self.assertIn(".env", context.exception.hint)

    @patch("weatherapp.client.requests.get")
    def test_500_error_raises_weather_error(self, mock_get: MagicMock) -> None:
        """Test WeatherError is raised on 500 server error."""
        # Setup mock response for 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Call and assert exception
        client = WeatherClient(api_key="test_key")
        with self.assertRaises(WeatherError) as context:
            client.get_current("London")

        # Check error message
        self.assertIn("500", str(context.exception))


if __name__ == "__main__":
    unittest.main()
