"""
Weather Service Module

Handles weather API integration and data retrieval.
Uses Open-Meteo API for current weather data (no API key required).
"""

import requests
from typing import Dict, Any
from datetime import datetime


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class CityNotFoundError(WeatherServiceError):
    """Raised when the specified city is not found."""
    pass


class NetworkError(WeatherServiceError):
    """Raised when network request fails."""
    pass


class WeatherService:
    """Service for fetching weather data from Open-Meteo API."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        """Initialize the weather service (no API key required)."""
        pass

    def get_current_weather(
        self,
        city: str,
        units: str = "metric",
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch current weather data for a city.

        Args:
            city: City name (e.g., "London" or "London,UK")
            units: Temperature units - "metric" (Celsius) or "imperial" (Fahrenheit)
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing weather data with keys:
                - city: str
                - country: str
                - temperature: float
                - feels_like: float
                - description: str
                - humidity: int (percentage)
                - wind_speed: float
                - pressure: int (hPa)
                - units: str
                - timestamp: datetime

        Raises:
            CityNotFoundError: If city is not found
            NetworkError: If network request fails
            WeatherServiceError: For other API errors
        """
        if not city or not city.strip():
            raise ValueError("City name cannot be empty")

        # Step 1: Get coordinates for the city
        latitude, longitude, city_name, country = self._get_coordinates(
            city.strip(), timeout
        )

        # Step 2: Fetch weather data using coordinates
        weather_data = self._fetch_weather(
            latitude, longitude, units, timeout
        )

        # Step 3: Format and return weather data (current + forecasts)
        result = {
            'city': city_name,
            'country': country,
            'temperature': weather_data['temperature'],
            'feels_like': weather_data['apparent_temperature'],
            'description': self._get_weather_description(weather_data['weather_code']),
            'humidity': weather_data['relative_humidity'],
            'wind_speed': weather_data['wind_speed'],
            'pressure': weather_data['surface_pressure'],
            'units': units,
            'timestamp': datetime.now()
        }
        # Include forecasts if present
        if 'hourly' in weather_data:
            result['hourly'] = weather_data['hourly']
        if 'daily' in weather_data:
            result['daily'] = weather_data['daily']
        return result

    def _get_coordinates(
        self,
        city: str,
        timeout: int
    ) -> tuple[float, float, str, str]:
        """
        Get coordinates for a city using Open-Meteo Geocoding API.

        Args:
            city: City name to search
            timeout: Request timeout in seconds

        Returns:
            Tuple of (latitude, longitude, city_name, country_code)

        Raises:
            CityNotFoundError: If city is not found
            NetworkError: If network request fails
        """
        params = {
            'name': city,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }

        try:
            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=timeout
            )

            if response.status_code != 200:
                raise WeatherServiceError(
                    f"Geocoding API returned status code {response.status_code}"
                )

            data = response.json()

            # Check if any results were found
            if not data.get('results'):
                raise CityNotFoundError(f"City '{city}' not found")

            result = data['results'][0]

            return (
                result['latitude'],
                result['longitude'],
                result['name'],
                result.get('country_code', result.get('country', 'Unknown'))
            )

        except requests.exceptions.Timeout:
            raise NetworkError(
                f"Request timed out after {timeout} seconds. "
                "Please check your internet connection."
            )
        except requests.exceptions.ConnectionError:
            raise NetworkError(
                "Failed to connect to weather service. "
                "Please check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}")
        except (KeyError, IndexError, TypeError) as e:
            raise WeatherServiceError(f"Malformed geocoding response: {str(e)}")

    def _fetch_weather(
        self,
        latitude: float,
        longitude: float,
        units: str,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Fetch weather data using coordinates from Open-Meteo Weather API.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units ("metric" or "imperial")
            timeout: Request timeout in seconds

        Returns:
            Dictionary with current weather data

        Raises:
            NetworkError: If network request fails
            WeatherServiceError: If response is malformed
        """
        # Open-Meteo uses celsius/fahrenheit parameter for temperature unit
        temp_unit = "celsius" if units == "metric" else "fahrenheit"
        wind_unit = "kmh" if units == "metric" else "mph"

        # Request current, hourly (next 24h), and daily (7d) data
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': [
                'temperature_2m',
                'apparent_temperature',
                'relative_humidity_2m',
                'weather_code',
                'surface_pressure',
                'wind_speed_10m'
            ],
            'hourly': [
                'temperature_2m',
                'apparent_temperature',
                'relative_humidity_2m',
                'weather_code',
                'wind_speed_10m',
                'precipitation_probability'
            ],
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'sunrise',
                'sunset'
            ],
            'temperature_unit': temp_unit,
            'wind_speed_unit': wind_unit,
            'timezone': 'auto',
            'forecast_days': 7
        }

        try:
            response = requests.get(
                self.WEATHER_URL,
                params=params,
                timeout=timeout
            )

            if response.status_code != 200:
                raise WeatherServiceError(
                    f"Weather API returned status code {response.status_code}"
                )

            data = response.json()
            current = data['current']

            # Convert wind speed from km/h to m/s for metric
            wind_speed = current['wind_speed_10m']
            if units == "metric":
                wind_speed = round(wind_speed / 3.6, 1)  # km/h to m/s
            else:
                wind_speed = round(wind_speed, 1)  # already in mph

            return {
                'temperature': round(current['temperature_2m'], 1),
                'apparent_temperature': round(current['apparent_temperature'], 1),
                'relative_humidity': current['relative_humidity_2m'],
                'weather_code': current['weather_code'],
                'surface_pressure': current['surface_pressure'],
                'wind_speed': wind_speed,
                'hourly': self._parse_hourly(data.get('hourly', {}), units),
                'daily': self._parse_daily(data.get('daily', {}), units)
            }

        except requests.exceptions.Timeout:
            raise NetworkError(
                f"Request timed out after {timeout} seconds. "
                "Please check your internet connection."
            )
        except requests.exceptions.ConnectionError:
            raise NetworkError(
                "Failed to connect to weather service. "
                "Please check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}")
        except (KeyError, IndexError, TypeError) as e:
            raise WeatherServiceError(f"Malformed weather response: {str(e)}")

    def _parse_hourly(self, hourly_data, units):
        """Parse hourly forecast from Open-Meteo hourly object (next ~24h)."""
        if not hourly_data or 'time' not in hourly_data:
            return []
        times = hourly_data['time']
        temps = hourly_data.get('temperature_2m', [])
        codes = hourly_data.get('weather_code', [])
        prec = hourly_data.get('precipitation_probability', [])
        result = []
        for i in range(min(len(times), 24)):
            result.append({
                'time': times[i][:16] if isinstance(times[i], str) else str(times[i]),
                'temperature': round(temps[i], 1) if i < len(temps) else None,
                'weather_code': codes[i] if i < len(codes) else 0,
                'precipitation_probability': prec[i] if i < len(prec) else 0,
                'units': units
            })
        return result

    def _parse_daily(self, daily_data, units):
        """Parse daily forecast from Open-Meteo daily object (7 days)."""
        if not daily_data or 'time' not in daily_data:
            return []
        times = daily_data['time']
        max_t = daily_data.get('temperature_2m_max', [])
        min_t = daily_data.get('temperature_2m_min', [])
        codes = daily_data.get('weather_code', [])
        result = []
        for i in range(len(times)):
            result.append({
                'date': times[i],
                'max_temp': round(max_t[i], 1) if i < len(max_t) else None,
                'min_temp': round(min_t[i], 1) if i < len(min_t) else None,
                'weather_code': codes[i] if i < len(codes) else 0,
                'units': units
            })
        return result

    @staticmethod
    def _get_weather_description(weather_code: int) -> str:
        """
        Convert Open-Meteo weather code to human-readable description.

        WMO Weather interpretation codes (WW):
        https://open-meteo.com/en/docs

        Args:
            weather_code: WMO weather code

        Returns:
            Human-readable weather description
        """
        weather_descriptions = {
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

        return weather_descriptions.get(weather_code, "Unknown")

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return round(celsius * 9/5 + 32, 1)

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return round((fahrenheit - 32) * 5/9, 1)

    @staticmethod
    def format_temperature(temp: float, units: str) -> str:
        """
        Format temperature with appropriate unit symbol.

        Args:
            temp: Temperature value
            units: "metric" or "imperial"

        Returns:
            Formatted temperature string (e.g., "20.5°C" or "68.9°F")
        """
        unit_symbol = "°C" if units == "metric" else "°F"
        return f"{temp}{unit_symbol}"


if __name__ == "__main__":
    # Example usage
    try:
        service = WeatherService()
        weather = service.get_current_weather("London", units="metric")

        print(f"Weather in {weather['city']}, {weather['country']}:")
        print(f"Temperature: {service.format_temperature(weather['temperature'], weather['units'])}")
        print(f"Feels like: {service.format_temperature(weather['feels_like'], weather['units'])}")
        print(f"Description: {weather['description']}")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind speed: {weather['wind_speed']} m/s")
        print(f"Pressure: {weather['pressure']} hPa")
        print("\nWeather data by Open-Meteo.com")

    except WeatherServiceError as e:
        print(f"Weather service error: {e}")
