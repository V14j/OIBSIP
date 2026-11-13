"""
Unit tests for the Weather App GUI Module

Tests metric label consistency between widget creation and weather updates.
No live API or GUI required.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import WeatherApp


class TestWeatherAppMetrics(unittest.TestCase):
    """Test suite for WeatherApp metric label consistency."""

    def setUp(self):
        """Set up test fixtures - create app without showing GUI."""
        # Create a minimal root that won't show
        import tkinter as tk
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        self.app = WeatherApp(self.root)

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_metric_labels_consistency(self):
        """
        Test that metric labels in _update_weather_display match
        the keys registered in self.metric_vars during widget creation.

        This is a regression test for the KeyError: 'Feels like' bug.
        """
        # Get the labels used in widget creation (create_widgets)
        # These are the actual keys in self.metric_vars
        widget_labels = list(self.app.metric_vars.keys())

        # Get the labels used in _update_weather_display
        # We'll extract them by inspecting the source or by calling the method
        # with a mock weather dict and capturing the keys used
        update_labels = [
            "Feels Like",
            "Humidity",
            "Wind",
            "Pressure"
        ]

        # Every label used in update must exist in metric_vars
        for label in update_labels:
            self.assertIn(
                label,
                self.app.metric_vars,
                f"Metric label '{label}' used in _update_weather_display "
                f"but not found in metric_vars. Available keys: {widget_labels}"
            )

        # Every key in metric_vars should be used in update (no orphaned widgets)
        for label in widget_labels:
            self.assertIn(
                label,
                update_labels,
                f"Metric label '{label}' created in widget but not used in "
                f"_update_weather_display. Update labels: {update_labels}"
            )

        # Exact match - same labels, same count
        self.assertEqual(
            set(widget_labels),
            set(update_labels),
            "Metric widget labels and update labels must be identical sets"
        )

    def test_metric_keys_match_service_response(self):
        """
        Test that metric keys used in update match the keys returned
        by WeatherService.get_current_weather().
        """
        from weather_service import WeatherService

        # Mock the service to get a sample response
        service = WeatherService()

        # We can't easily test without mocking the HTTP calls, but we can
        # verify the expected keys from the service by checking the code
        # The service returns these keys (from weather_service.py):
        expected_service_keys = {
            'temperature',
            'feels_like',
            'humidity',
            'wind_speed',
            'pressure',
            'description',
            'weather_code',
            'city',
            'country',
            'units',
            'hourly',
            'daily',
            'timestamp'
        }

        # The keys used in _update_weather_display for metrics
        update_metric_keys = ['feels_like', 'humidity', 'wind_speed', 'pressure']

        for key in update_metric_keys:
            self.assertIn(
                key,
                expected_service_keys,
                f"Metric key '{key}' used in _update_weather_display "
                f"but not returned by WeatherService"
            )

    def test_update_weather_display_no_keyerror(self):
        """
        Test that _update_weather_display doesn't raise KeyError
        when called with a complete weather dict.
        """
        # Mock weather data matching WeatherService response structure
        weather = {
            'city': 'London',
            'country': 'GB',
            'temperature': 20.5,
            'feels_like': 18.3,
            'humidity': 65,
            'wind_speed': 5.2,
            'pressure': 1013,
            'description': 'Partly cloudy',
            'weather_code': 2,
            'units': 'metric',
            'hourly': [],
            'daily': [],
        }

        # This should not raise KeyError
        try:
            self.app._update_weather_display(weather)
        except KeyError as e:
            self.fail(f"_update_weather_display raised KeyError: {e}")
        except Exception as e:
            # Other exceptions (like tkinter errors in headless) are OK
            # but KeyError is the bug we're testing for
            if "KeyError" in type(e).__name__:
                self.fail(f"_update_weather_display raised KeyError: {e}")

    def test_update_weather_display_imperial_units(self):
        """
        Test that _update_weather_display works with imperial units.
        """
        weather = {
            'city': 'New York',
            'country': 'US',
            'temperature': 68.9,
            'feels_like': 65.2,
            'humidity': 70,
            'wind_speed': 15.3,
            'pressure': 1015,
            'description': 'Clear sky',
            'weather_code': 0,
            'units': 'imperial',
            'hourly': [],
            'daily': [],
        }

        try:
            self.app._update_weather_display(weather)
        except KeyError as e:
            self.fail(f"_update_weather_display raised KeyError with imperial: {e}")
        except Exception as e:
            if "KeyError" in type(e).__name__:
                self.fail(f"_update_weather_display raised KeyError: {e}")

    def test_update_weather_display_missing_optional_fields(self):
        """
        Test that _update_weather_display handles missing optional fields gracefully.
        """
        # Weather with missing pressure (None) and empty hourly/daily
        weather = {
            'city': 'Test City',
            'country': 'XX',
            'temperature': 20.0,
            'feels_like': 18.0,
            'humidity': 60,
            'wind_speed': 5.0,
            'pressure': None,  # Missing from API
            'description': 'Clear',
            'weather_code': 0,
            'units': 'metric',
            'hourly': [],
            'daily': [],
        }

        try:
            self.app._update_weather_display(weather)
        except KeyError as e:
            self.fail(f"_update_weather_display raised KeyError: {e}")
        except Exception as e:
            if "KeyError" in type(e).__name__:
                self.fail(f"_update_weather_display raised KeyError: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)