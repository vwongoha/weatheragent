"""Weather Broker - MCP Server for Open-Meteo Weather APIs

Provides comprehensive weather data including current conditions, forecasts,
historical data, alerts, and intelligent recommendations.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json


class WeatherBroker:
    """Weather data broker using Open-Meteo API."""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    def __init__(self):
        """Initialize the weather broker."""
        self.session = requests.Session()
    
    def _geocode_location(self, location: str) -> Tuple[float, float, str]:
        """Convert location string to latitude/longitude coordinates.
        
        Args:
            location: City name, zip code, or "lat,lon" string
            
        Returns:
            Tuple of (latitude, longitude, location_name)
            
        Raises:
            ValueError: If location cannot be geocoded
        """
        # Check if already lat,lon
        if ',' in location:
            try:
                parts = location.split(',')
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon, f"{lat},{lon}"
            except (ValueError, IndexError):
                pass
        
        # Geocode the location
        params = {
            'name': location,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = self.session.get(self.GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            raise ValueError(f"Location '{location}' not found")
        
        result = data['results'][0]
        return (
            result['latitude'],
            result['longitude'],
            f"{result['name']}, {result.get('admin1', '')}, {result.get('country', '')}"
        )
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather conditions for a location.
        
        Args:
            location: City name, zip code, or "lat,lon"
            
        Returns:
            Dictionary with current weather data including temperature,
            conditions, humidity, wind speed, and more
        """
        lat, lon, location_name = self._geocode_location(location)
        
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': [
                'temperature_2m',
                'relative_humidity_2m',
                'apparent_temperature',
                'precipitation',
                'weather_code',
                'cloud_cover',
                'wind_speed_10m',
                'wind_direction_10m',
                'wind_gusts_10m'
            ],
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch'
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        
        return {
            'location': location_name,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'timestamp': current['time'],
            'temperature': current['temperature_2m'],
            'feels_like': current['apparent_temperature'],
            'humidity': current['relative_humidity_2m'],
            'conditions': self._decode_weather_code(current['weather_code']),
            'weather_code': current['weather_code'],
            'precipitation': current['precipitation'],
            'cloud_cover': current['cloud_cover'],
            'wind': {
                'speed': current['wind_speed_10m'],
                'direction': current['wind_direction_10m'],
                'gusts': current['wind_gusts_10m']
            }
        }
    
    def get_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for a location.
        
        Args:
            location: City name, zip code, or "lat,lon"
            days: Number of days to forecast (1-16)
            
        Returns:
            Dictionary with daily forecast data
        """
        if days < 1 or days > 16:
            raise ValueError("Days must be between 1 and 16")
        
        lat, lon, location_name = self._geocode_location(location)
        
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'apparent_temperature_max',
                'apparent_temperature_min',
                'precipitation_sum',
                'precipitation_probability_max',
                'wind_speed_10m_max',
                'wind_gusts_10m_max',
                'sunrise',
                'sunset'
            ],
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch',
            'forecast_days': days
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        daily = data['daily']
        forecast_list = []
        
        for i in range(len(daily['time'])):
            forecast_list.append({
                'date': daily['time'][i],
                'conditions': self._decode_weather_code(daily['weather_code'][i]),
                'weather_code': daily['weather_code'][i],
                'temperature': {
                    'high': daily['temperature_2m_max'][i],
                    'low': daily['temperature_2m_min'][i]
                },
                'feels_like': {
                    'high': daily['apparent_temperature_max'][i],
                    'low': daily['apparent_temperature_min'][i]
                },
                'precipitation': {
                    'total': daily['precipitation_sum'][i],
                    'probability': daily['precipitation_probability_max'][i]
                },
                'wind': {
                    'max_speed': daily['wind_speed_10m_max'][i],
                    'max_gusts': daily['wind_gusts_10m_max'][i]
                },
                'sunrise': daily['sunrise'][i],
                'sunset': daily['sunset'][i]
            })
        
        return {
            'location': location_name,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'forecast': forecast_list
        }
    
    def predict_umbrella_needed(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Predict if an umbrella is needed for a specific date.
        
        Args:
            location: City name, zip code, or "lat,lon"
            date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Dictionary with umbrella recommendation and reasoning
        """
        forecast_data = self.get_forecast(location, days=7)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Find the matching day in forecast
        day_forecast = None
        for day in forecast_data['forecast']:
            if day['date'] == date:
                day_forecast = day
                break
        
        if day_forecast is None:
            raise ValueError(f"Date {date} not available in forecast range")
        
        # Decision logic
        precip_prob = day_forecast['precipitation']['probability']
        precip_total = day_forecast['precipitation']['total']
        weather_code = day_forecast['weather_code']
        
        umbrella_needed = False
        confidence = "low"
        reasons = []
        
        if precip_prob >= 70:
            umbrella_needed = True
            confidence = "high"
            reasons.append(f"High precipitation probability ({precip_prob}%)")
        elif precip_prob >= 40:
            umbrella_needed = True
            confidence = "medium"
            reasons.append(f"Moderate precipitation probability ({precip_prob}%)")
        else:
            reasons.append(f"Low precipitation probability ({precip_prob}%)")
        
        if precip_total > 0.1:
            umbrella_needed = True
            reasons.append(f"Expected precipitation: {precip_total} inches")
        
        # Check weather codes for rain/snow
        if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            umbrella_needed = True
            reasons.append(f"Weather conditions: {day_forecast['conditions']}")
        
        return {
            'location': forecast_data['location'],
            'date': date,
            'umbrella_needed': umbrella_needed,
            'confidence': confidence,
            'reasons': reasons,
            'weather_summary': {
                'conditions': day_forecast['conditions'],
                'precipitation_probability': precip_prob,
                'precipitation_total': precip_total,
                'temperature_high': day_forecast['temperature']['high'],
                'temperature_low': day_forecast['temperature']['low']
            }
        }
    
    def get_travel_recommendation(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get travel recommendation for a specific date.
        
        Args:
            location: City name, zip code, or "lat,lon"
            date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Dictionary with travel recommendation and reasoning
        """
        forecast_data = self.get_forecast(location, days=7)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Find the matching day in forecast
        day_forecast = None
        for day in forecast_data['forecast']:
            if day['date'] == date:
                day_forecast = day
                break
        
        if day_forecast is None:
            raise ValueError(f"Date {date} not available in forecast range")
        
        # Scoring system for travel conditions
        score = 100  # Start with perfect score
        factors = []
        
        # Temperature scoring
        temp_high = day_forecast['temperature']['high']
        temp_low = day_forecast['temperature']['low']
        
        if temp_high > 95 or temp_low < 20:
            score -= 30
            factors.append("Extreme temperatures")
        elif temp_high > 85 or temp_low < 32:
            score -= 15
            factors.append("Uncomfortable temperatures")
        else:
            factors.append("Comfortable temperatures")
        
        # Precipitation scoring
        precip_prob = day_forecast['precipitation']['probability']
        if precip_prob >= 70:
            score -= 25
            factors.append(f"High rain chance ({precip_prob}%)")
        elif precip_prob >= 40:
            score -= 10
            factors.append(f"Moderate rain chance ({precip_prob}%)")
        
        # Wind scoring
        max_wind = day_forecast['wind']['max_gusts']
        if max_wind > 40:
            score -= 20
            factors.append(f"Very windy conditions ({max_wind} mph gusts)")
        elif max_wind > 25:
            score -= 10
            factors.append(f"Windy conditions ({max_wind} mph gusts)")
        
        # Weather code severity
        weather_code = day_forecast['weather_code']
        if weather_code in [95, 96, 99]:  # Thunderstorms
            score -= 30
            factors.append("Thunderstorm risk")
        elif weather_code in [71, 73, 75, 85, 86]:  # Heavy snow
            score -= 25
            factors.append("Heavy snow conditions")
        
        # Determine recommendation
        if score >= 80:
            recommendation = "Excellent"
            summary = "Perfect conditions for travel"
        elif score >= 60:
            recommendation = "Good"
            summary = "Generally favorable travel conditions"
        elif score >= 40:
            recommendation = "Fair"
            summary = "Acceptable but not ideal travel conditions"
        elif score >= 20:
            recommendation = "Poor"
            summary = "Challenging travel conditions expected"
        else:
            recommendation = "Not Recommended"
            summary = "Hazardous travel conditions - consider postponing"
        
        return {
            'location': forecast_data['location'],
            'date': date,
            'recommendation': recommendation,
            'score': score,
            'summary': summary,
            'factors': factors,
            'weather_details': {
                'conditions': day_forecast['conditions'],
                'temperature_range': f"{day_forecast['temperature']['low']}°F - {day_forecast['temperature']['high']}°F",
                'precipitation_probability': precip_prob,
                'wind_gusts': max_wind
            }
        }
    
    def get_severe_weather_alerts(self, location: str) -> Dict[str, Any]:
        """Get severe weather alerts for a location.
        
        Note: Open-Meteo doesn't provide official alerts. This method
        analyzes forecast data to detect potentially severe conditions.
        
        Args:
            location: City name, zip code, or "lat,lon"
            
        Returns:
            Dictionary with detected severe weather conditions
        """
        forecast_data = self.get_forecast(location, days=3)
        alerts = []
        
        for day in forecast_data['forecast']:
            day_alerts = []
            
            # Temperature alerts
            if day['temperature']['high'] > 100:
                day_alerts.append({
                    'type': 'Extreme Heat',
                    'severity': 'high',
                    'description': f"Dangerous heat expected: {day['temperature']['high']}°F"
                })
            elif day['temperature']['low'] < 10:
                day_alerts.append({
                    'type': 'Extreme Cold',
                    'severity': 'high',
                    'description': f"Dangerous cold expected: {day['temperature']['low']}°F"
                })
            
            # Precipitation alerts
            if day['precipitation']['total'] > 2.0:
                day_alerts.append({
                    'type': 'Heavy Precipitation',
                    'severity': 'medium',
                    'description': f"Heavy precipitation expected: {day['precipitation']['total']} inches"
                })
            
            # Wind alerts
            if day['wind']['max_gusts'] > 50:
                day_alerts.append({
                    'type': 'High Wind',
                    'severity': 'high',
                    'description': f"Dangerous wind gusts expected: {day['wind']['max_gusts']} mph"
                })
            elif day['wind']['max_gusts'] > 35:
                day_alerts.append({
                    'type': 'Wind Advisory',
                    'severity': 'medium',
                    'description': f"Strong wind gusts expected: {day['wind']['max_gusts']} mph"
                })
            
            # Weather code based alerts
            weather_code = day['weather_code']
            if weather_code in [95, 96, 99]:
                day_alerts.append({
                    'type': 'Thunderstorm',
                    'severity': 'high',
                    'description': 'Thunderstorms expected'
                })
            elif weather_code in [75, 85, 86]:
                day_alerts.append({
                    'type': 'Heavy Snow',
                    'severity': 'high',
                    'description': 'Heavy snow expected'
                })
            
            if day_alerts:
                alerts.append({
                    'date': day['date'],
                    'alerts': day_alerts
                })
        
        return {
            'location': forecast_data['location'],
            'alert_count': sum(len(day['alerts']) for day in alerts),
            'alerts_by_day': alerts,
            'has_severe_weather': len(alerts) > 0
        }
    
    def get_historical_weather(self, location: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical weather data for a location.
        
        Args:
            location: City name, zip code, or "lat,lon"
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with historical weather data
        """
        lat, lon, location_name = self._geocode_location(location)
        
        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': start_date,
            'end_date': end_date,
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean',
                'precipitation_sum',
                'wind_speed_10m_max'
            ],
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch'
        }
        
        response = self.session.get(self.HISTORICAL_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        daily = data['daily']
        history = []
        
        for i in range(len(daily['time'])):
            history.append({
                'date': daily['time'][i],
                'conditions': self._decode_weather_code(daily['weather_code'][i]),
                'weather_code': daily['weather_code'][i],
                'temperature': {
                    'high': daily['temperature_2m_max'][i],
                    'low': daily['temperature_2m_min'][i],
                    'mean': daily['temperature_2m_mean'][i]
                },
                'precipitation': daily['precipitation_sum'][i],
                'wind_max': daily['wind_speed_10m_max'][i]
            })
        
        # Calculate statistics
        temps_high = [d['temperature']['high'] for d in history]
        temps_low = [d['temperature']['low'] for d in history]
        precip = [d['precipitation'] for d in history]
        
        return {
            'location': location_name,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'period': {'start': start_date, 'end': end_date},
            'history': history,
            'statistics': {
                'temperature': {
                    'avg_high': sum(temps_high) / len(temps_high) if temps_high else 0,
                    'avg_low': sum(temps_low) / len(temps_low) if temps_low else 0,
                    'max_high': max(temps_high) if temps_high else 0,
                    'min_low': min(temps_low) if temps_low else 0
                },
                'precipitation': {
                    'total': sum(precip),
                    'avg_daily': sum(precip) / len(precip) if precip else 0,
                    'days_with_precip': sum(1 for p in precip if p > 0)
                }
            }
        }
    
    def compare_weather(self, locations: List[str], date: Optional[str] = None) -> Dict[str, Any]:
        """Compare weather across multiple cities.
        
        Args:
            locations: List of city names, zip codes, or "lat,lon" strings
            date: Date string (YYYY-MM-DD) or None for current weather
            
        Returns:
            Dictionary with comparison data
        """
        if date is None:
            # Compare current weather
            results = []
            for location in locations:
                try:
                    weather = self.get_current_weather(location)
                    results.append({
                        'location': weather['location'],
                        'temperature': weather['temperature'],
                        'feels_like': weather['feels_like'],
                        'conditions': weather['conditions'],
                        'humidity': weather['humidity'],
                        'wind_speed': weather['wind']['speed'],
                        'precipitation': weather['precipitation']
                    })
                except Exception as e:
                    results.append({
                        'location': location,
                        'error': str(e)
                    })
            
            # Find extremes
            valid_results = [r for r in results if 'error' not in r]
            if valid_results:
                warmest = max(valid_results, key=lambda x: x['temperature'])
                coldest = min(valid_results, key=lambda x: x['temperature'])
                most_humid = max(valid_results, key=lambda x: x['humidity'])
                windiest = max(valid_results, key=lambda x: x['wind_speed'])
            else:
                warmest = coldest = most_humid = windiest = None
            
            return {
                'comparison_type': 'current',
                'timestamp': datetime.now().isoformat(),
                'locations': results,
                'extremes': {
                    'warmest': warmest,
                    'coldest': coldest,
                    'most_humid': most_humid,
                    'windiest': windiest
                }
            }
        else:
            # Compare forecast for specific date
            results = []
            for location in locations:
                try:
                    forecast = self.get_forecast(location, days=7)
                    day_forecast = None
                    for day in forecast['forecast']:
                        if day['date'] == date:
                            day_forecast = day
                            break
                    
                    if day_forecast:
                        results.append({
                            'location': forecast['location'],
                            'date': date,
                            'temperature_high': day_forecast['temperature']['high'],
                            'temperature_low': day_forecast['temperature']['low'],
                            'conditions': day_forecast['conditions'],
                            'precipitation_probability': day_forecast['precipitation']['probability'],
                            'precipitation_total': day_forecast['precipitation']['total']
                        })
                    else:
                        results.append({
                            'location': location,
                            'error': f"Date {date} not available in forecast"
                        })
                except Exception as e:
                    results.append({
                        'location': location,
                        'error': str(e)
                    })
            
            # Find extremes
            valid_results = [r for r in results if 'error' not in r]
            if valid_results:
                warmest = max(valid_results, key=lambda x: x['temperature_high'])
                coldest = min(valid_results, key=lambda x: x['temperature_low'])
                rainiest = max(valid_results, key=lambda x: x['precipitation_probability'])
            else:
                warmest = coldest = rainiest = None
            
            return {
                'comparison_type': 'forecast',
                'date': date,
                'locations': results,
                'extremes': {
                    'warmest': warmest,
                    'coldest': coldest,
                    'rainiest': rainiest
                }
            }
    
    def _decode_weather_code(self, code: int) -> str:
        """Decode WMO weather code to human-readable description.
        
        Args:
            code: WMO weather code
            
        Returns:
            Human-readable weather description
        """
        codes = {
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
        return codes.get(code, f"Unknown ({code})")


# Convenience functions for direct use
def get_current_weather(location: str) -> Dict[str, Any]:
    """Get current weather conditions."""
    broker = WeatherBroker()
    return broker.get_current_weather(location)


def get_forecast(location: str, days: int = 7) -> Dict[str, Any]:
    """Get weather forecast."""
    broker = WeatherBroker()
    return broker.get_forecast(location, days)


def predict_umbrella_needed(location: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Predict if umbrella is needed."""
    broker = WeatherBroker()
    return broker.predict_umbrella_needed(location, date)


def get_travel_recommendation(location: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Get travel recommendation."""
    broker = WeatherBroker()
    return broker.get_travel_recommendation(location, date)
