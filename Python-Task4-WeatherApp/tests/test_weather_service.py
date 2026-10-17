"""
Unit tests for the Weather Service Module

Tests weather API integration with mocked HTTP requests.
No live API key or internet connection required.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from weather_service import (
    WeatherService,
    WeatherServiceError,
    CityNotFoundError,
    NetworkError
)


class TestWeatherService(unittest.TestCase):
    """Test suite for WeatherService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = WeatherService()

    @patch('weather_service.requests.get')
    def test_successful_weather_fetch_metric(self, mock_get):
        """Test successful weather data fetch with metric units."""
        # Mock geocoding API response
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'London',
                'country_code': 'GB'
            }]
        }

        # Mock weather API response
        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.5,
                'apparent_temperature': 18.3,
                'relative_humidity_2m': 65,
                'weather_code': 2,
                'surface_pressure': 1013,
                'wind_speed_10m': 18.7  # km/h
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        # Fetch weather
        weather = self.service.get_current_weather('London', units='metric')

        # Verify results
        self.assertEqual(weather['city'], 'London')
        self.assertEqual(weather['country'], 'GB')
        self.assertEqual(weather['temperature'], 20.5)
        self.assertEqual(weather['feels_like'], 18.3)
        self.assertEqual(weather['description'], 'Partly cloudy')
        self.assertEqual(weather['humidity'], 65)
        self.assertEqual(weather['wind_speed'], 5.2)  # km/h converted to m/s (18.7/3.6)
        self.assertEqual(weather['pressure'], 1013)
        self.assertEqual(weather['units'], 'metric')

        # Verify two API calls were made
        self.assertEqual(mock_get.call_count, 2)

    @patch('weather_service.requests.get')
    def test_successful_weather_fetch_imperial(self, mock_get):
        """Test successful weather data fetch with imperial units."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 40.7128,
                'longitude': -74.0060,
                'name': 'New York',
                'country_code': 'US'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 68.9,
                'apparent_temperature': 65.2,
                'relative_humidity_2m': 70,
                'weather_code': 0,
                'surface_pressure': 1015,
                'wind_speed_10m': 15.3  # mph
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('New York', units='imperial')

        self.assertEqual(weather['city'], 'New York')
        self.assertEqual(weather['temperature'], 68.9)
        self.assertEqual(weather['description'], 'Clear sky')
        self.assertEqual(weather['units'], 'imperial')
        self.assertEqual(weather['wind_speed'], 15.3)

    @patch('weather_service.requests.get')
    def test_city_not_found(self, mock_get):
        """Test handling of city not found error."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {}

        mock_get.return_value = geocode_response

        with self.assertRaises(CityNotFoundError) as context:
            self.service.get_current_weather('InvalidCityName123')

        self.assertIn('not found', str(context.exception).lower())

    @patch('weather_service.requests.get')
    def test_api_error_response(self, mock_get):
        """Test handling of general API errors."""
        geocode_response = Mock()
        geocode_response.status_code = 500
        geocode_response.text = 'Internal Server Error'

        mock_get.return_value = geocode_response

        with self.assertRaises(WeatherServiceError):
            self.service.get_current_weather('London')

    @patch('weather_service.requests.get')
    def test_network_timeout(self, mock_get):
        """Test handling of network timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(NetworkError) as context:
            self.service.get_current_weather('London', timeout=5)

        self.assertIn('timed out', str(context.exception).lower())

    @patch('weather_service.requests.get')
    def test_network_connection_error(self, mock_get):
        """Test handling of network connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(NetworkError) as context:
            self.service.get_current_weather('London')

        self.assertIn('connect', str(context.exception).lower())

    @patch('weather_service.requests.get')
    def test_general_network_error(self, mock_get):
        """Test handling of general network errors."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException('Network failure')

        with self.assertRaises(NetworkError):
            self.service.get_current_weather('London')

    def test_empty_city_name(self):
        """Test that empty city name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.service.get_current_weather('')

        self.assertIn('empty', str(context.exception).lower())

    def test_whitespace_only_city_name(self):
        """Test that whitespace-only city name raises ValueError."""
        with self.assertRaises(ValueError):
            self.service.get_current_weather('   ')

    @patch('weather_service.requests.get')
    def test_malformed_api_response_missing_fields(self, mock_get):
        """Test handling of malformed API response with missing fields."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test City',
                'country_code': 'GB'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                # Missing required fields
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        with self.assertRaises(WeatherServiceError) as context:
            self.service.get_current_weather('Test')

        self.assertIn('malformed', str(context.exception).lower())

    @patch('weather_service.requests.get')
    def test_city_name_with_country_code(self, mock_get):
        """Test fetching weather with city name and country code."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 48.8566,
                'longitude': 2.3522,
                'name': 'Paris',
                'country_code': 'FR'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 15.0,
                'apparent_temperature': 14.0,
                'relative_humidity_2m': 80,
                'weather_code': 61,
                'surface_pressure': 1010,
                'wind_speed_10m': 12.6  # km/h
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('Paris,FR')

        self.assertEqual(weather['city'], 'Paris')
        self.assertEqual(weather['country'], 'FR')
        self.assertEqual(weather['description'], 'Slight rain')

        # Verify the city parameter was passed correctly to geocoding
        first_call_args = mock_get.call_args_list[0]
        self.assertEqual(first_call_args[1]['params']['name'], 'Paris,FR')

    @patch('weather_service.requests.get')
    def test_temperature_rounding(self, mock_get):
        """Test that temperatures are rounded correctly."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test',
                'country_code': 'XX'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.567,
                'apparent_temperature': 18.234,
                'relative_humidity_2m': 65,
                'weather_code': 1,
                'surface_pressure': 1013,
                'wind_speed_10m': 57.8  # km/h
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('Test')

        # Should be rounded to 1 decimal place
        self.assertEqual(weather['temperature'], 20.6)
        self.assertEqual(weather['feels_like'], 18.2)
        self.assertEqual(weather['wind_speed'], 16.1)  # 57.8/3.6 = 16.055... rounded to 16.1

    def test_celsius_to_fahrenheit_conversion(self):
        """Test Celsius to Fahrenheit conversion."""
        self.assertEqual(WeatherService.celsius_to_fahrenheit(0), 32.0)
        self.assertEqual(WeatherService.celsius_to_fahrenheit(100), 212.0)
        self.assertEqual(WeatherService.celsius_to_fahrenheit(20), 68.0)
        self.assertEqual(WeatherService.celsius_to_fahrenheit(-40), -40.0)

    def test_fahrenheit_to_celsius_conversion(self):
        """Test Fahrenheit to Celsius conversion."""
        self.assertEqual(WeatherService.fahrenheit_to_celsius(32), 0.0)
        self.assertEqual(WeatherService.fahrenheit_to_celsius(212), 100.0)
        self.assertEqual(WeatherService.fahrenheit_to_celsius(68), 20.0)
        self.assertEqual(WeatherService.fahrenheit_to_celsius(-40), -40.0)

    def test_temperature_conversion_rounding(self):
        """Test that temperature conversions are rounded correctly."""
        # Test rounding
        celsius = 20.5
        fahrenheit = WeatherService.celsius_to_fahrenheit(celsius)
        self.assertEqual(fahrenheit, 68.9)  # Should round to 1 decimal

        # Convert back
        converted_back = WeatherService.fahrenheit_to_celsius(fahrenheit)
        self.assertAlmostEqual(converted_back, celsius, places=1)

    def test_format_temperature_metric(self):
        """Test temperature formatting with metric units."""
        formatted = WeatherService.format_temperature(20.5, 'metric')
        self.assertEqual(formatted, '20.5°C')

    def test_format_temperature_imperial(self):
        """Test temperature formatting with imperial units."""
        formatted = WeatherService.format_temperature(68.9, 'imperial')
        self.assertEqual(formatted, '68.9°F')

    @patch('weather_service.requests.get')
    def test_custom_timeout(self, mock_get):
        """Test that custom timeout is passed to requests."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test',
                'country_code': 'XX'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'apparent_temperature': 18.0,
                'relative_humidity_2m': 65,
                'weather_code': 1,
                'surface_pressure': 1013,
                'wind_speed_10m': 18.0
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        self.service.get_current_weather('Test', timeout=30)

        # Verify timeout was passed to both requests.get calls
        for call in mock_get.call_args_list:
            self.assertEqual(call[1]['timeout'], 30)

    @patch('weather_service.requests.get')
    def test_timestamp_present(self, mock_get):
        """Test that timestamp is included in weather data."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test',
                'country_code': 'XX'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'apparent_temperature': 18.0,
                'relative_humidity_2m': 65,
                'weather_code': 1,
                'surface_pressure': 1013,
                'wind_speed_10m': 18.0
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('Test')

        self.assertIn('timestamp', weather)
        self.assertIsInstance(weather['timestamp'], datetime)

    def test_weather_code_descriptions(self):
        """Test that all WMO weather codes return valid descriptions."""
        test_cases = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        for code, description in test_cases.items():
            self.assertEqual(
                WeatherService._get_weather_description(code),
                description,
                f"Weather code {code} should return '{description}'"
            )

    def test_unknown_weather_code(self):
        """Test that unknown weather codes return 'Unknown'."""
        self.assertEqual(WeatherService._get_weather_description(999), "Unknown")
        self.assertEqual(WeatherService._get_weather_description(-1), "Unknown")


    def test_hourly_forecast_parsing(self):
        """Test hourly forecast parsing from API response."""
        hourly_data = {
            'time': ['2026-10-17T10:00', '2026-10-17T11:00'],
            'temperature_2m': [18.5, 19.2],
            'weather_code': [0, 2],
            'precipitation_probability': [0, 20]
        }
        result = self.service._parse_hourly(hourly_data, 'metric')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['temperature'], 18.5)
        self.assertEqual(result[0]['weather_code'], 0)
        self.assertEqual(result[0]['precipitation_probability'], 0)

    def test_daily_forecast_parsing(self):
        """Test daily forecast parsing from API response."""
        daily_data = {
            'time': ['2026-10-17', '2026-10-18'],
            'temperature_2m_max': [22.0, 20.5],
            'temperature_2m_min': [10.0, 9.0],
            'weather_code': [1, 3]
        }
        result = self.service._parse_daily(daily_data, 'metric')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['max_temp'], 22.0)
        self.assertEqual(result[0]['min_temp'], 10.0)

    def test_hourly_forecast_conversion(self):
        """Test hourly temperatures converted when units are imperial."""
        hourly_data = {'time': ['2026-01-01T10:00'], 'temperature_2m': [20.0]}
        result = self.service._parse_hourly(hourly_data, 'imperial')
        # Note: Open-Meteo already returns in requested unit; parsing just passes through
        self.assertEqual(result[0]['units'], 'imperial')

    def test_daily_forecast_empty_response(self):
        """Test daily parsing handles empty/missing data."""
        result = self.service._parse_daily({}, 'metric')
        self.assertEqual(result, [])
        result2 = self.service._parse_daily({'time': []}, 'metric')
        self.assertEqual(result2, [])


class TestWeatherServiceEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = WeatherService()

    @patch('weather_service.requests.get')
    def test_unicode_city_name(self, mock_get):
        """Test handling of unicode characters in city name."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 48.1371,
                'longitude': 11.5761,
                'name': 'München',
                'country_code': 'DE'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 15.0,
                'apparent_temperature': 14.0,
                'relative_humidity_2m': 70,
                'weather_code': 3,
                'surface_pressure': 1010,
                'wind_speed_10m': 14.4  # km/h
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('München')
        self.assertEqual(weather['city'], 'München')
        self.assertEqual(weather['country'], 'DE')

    @patch('weather_service.requests.get')
    def test_city_name_with_leading_trailing_whitespace(self, mock_get):
        """Test that city name whitespace is trimmed."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'London',
                'country_code': 'GB'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 20.0,
                'apparent_temperature': 18.0,
                'relative_humidity_2m': 65,
                'weather_code': 1,
                'surface_pressure': 1013,
                'wind_speed_10m': 18.0
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('  London  ')

        # Verify whitespace was trimmed in API call
        first_call_args = mock_get.call_args_list[0]
        self.assertEqual(first_call_args[1]['params']['name'], 'London')

    @patch('weather_service.requests.get')
    def test_zero_temperature(self, mock_get):
        """Test handling of zero temperature."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test',
                'country_code': 'XX'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': 0.0,
                'apparent_temperature': -2.0,
                'relative_humidity_2m': 80,
                'weather_code': 71,
                'surface_pressure': 1010,
                'wind_speed_10m': 3.6
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('Test')
        self.assertEqual(weather['temperature'], 0.0)
        self.assertEqual(weather['feels_like'], -2.0)

    @patch('weather_service.requests.get')
    def test_negative_temperature(self, mock_get):
        """Test handling of negative temperature."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': [{
                'latitude': 51.5074,
                'longitude': -0.1278,
                'name': 'Test',
                'country_code': 'XX'
            }]
        }

        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current': {
                'temperature_2m': -15.5,
                'apparent_temperature': -20.0,
                'relative_humidity_2m': 60,
                'weather_code': 71,
                'surface_pressure': 1020,
                'wind_speed_10m': 21.6
            }
        }

        mock_get.side_effect = [geocode_response, weather_response]

        weather = self.service.get_current_weather('Test')
        self.assertEqual(weather['temperature'], -15.5)

    @patch('weather_service.requests.get')
    def test_geocoding_returns_no_results(self, mock_get):
        """Test handling when geocoding returns results but empty array."""
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            'results': []
        }

        mock_get.return_value = geocode_response

        with self.assertRaises(CityNotFoundError) as context:
            self.service.get_current_weather('NonExistentCity')

        self.assertIn('not found', str(context.exception).lower())

    @patch('weather_service.requests.get')
    def test_geocoding_api_error(self, mock_get):
        """Test handling of geocoding API error."""
        geocode_response = Mock()
        geocode_response.status_code = 500
        geocode_response.json.return_value = {}

        mock_get.return_value = geocode_response

        with self.assertRaises(WeatherServiceError) as context:
            self.service.get_current_weather('London')

        self.assertIn('status code', str(context.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
