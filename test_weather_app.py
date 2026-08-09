"""Test Weather App - Demonstrates all weather broker capabilities

This app tests all the weather broker functions including:
- Current weather conditions
- Multi-day forecasts
- Umbrella predictions
- Travel recommendations
- Severe weather alerts
- Historical weather data
- Weather comparisons across cities
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the mcp_server_weather directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_server_weather'))

from weather_broker import (
    WeatherBroker,
    get_current_weather,
    get_forecast,
    predict_umbrella_needed,
    get_travel_recommendation
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent))


def test_current_weather(broker: WeatherBroker, location: str):
    """Test current weather conditions."""
    print_section(f"Current Weather: {location}")
    try:
        weather = broker.get_current_weather(location)
        print(f"Location: {weather['location']}")
        print(f"Temperature: {weather['temperature']}°F (Feels like: {weather['feels_like']}°F)")
        print(f"Conditions: {weather['conditions']}")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind: {weather['wind']['speed']} mph (gusts: {weather['wind']['gusts']} mph)")
        print(f"Cloud Cover: {weather['cloud_cover']}%")
        print(f"Precipitation: {weather['precipitation']} inches")
        print(f"Timestamp: {weather['timestamp']}")
    except Exception as e:
        print(f"Error: {e}")


def test_forecast(broker: WeatherBroker, location: str, days: int = 5):
    """Test weather forecast."""
    print_section(f"Weather Forecast: {location} ({days} days)")
    try:
        forecast = broker.get_forecast(location, days)
        print(f"Location: {forecast['location']}\n")
        
        for day in forecast['forecast']:
            print(f"Date: {day['date']}")
            print(f"  Conditions: {day['conditions']}")
            print(f"  Temperature: {day['temperature']['low']}°F - {day['temperature']['high']}°F")
            print(f"  Feels Like: {day['feels_like']['low']}°F - {day['feels_like']['high']}°F")
            print(f"  Precipitation: {day['precipitation']['probability']}% chance, {day['precipitation']['total']} inches")
            print(f"  Wind: Max {day['wind']['max_speed']} mph (gusts: {day['wind']['max_gusts']} mph)")
            print(f"  Sunrise: {day['sunrise']} | Sunset: {day['sunset']}")
            print()
    except Exception as e:
        print(f"Error: {e}")


def test_umbrella_prediction(broker: WeatherBroker, location: str, date: str = None):
    """Test umbrella prediction."""
    date_str = date or "today"
    print_section(f"Umbrella Prediction: {location} ({date_str})")
    try:
        prediction = broker.predict_umbrella_needed(location, date)
        print(f"Location: {prediction['location']}")
        print(f"Date: {prediction['date']}")
        print(f"\nUmbrella Needed: {'YES' if prediction['umbrella_needed'] else 'NO'}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"\nReasons:")
        for reason in prediction['reasons']:
            print(f"  - {reason}")
        print(f"\nWeather Summary:")
        print(f"  Conditions: {prediction['weather_summary']['conditions']}")
        print(f"  Temperature: {prediction['weather_summary']['temperature_low']}°F - {prediction['weather_summary']['temperature_high']}°F")
        print(f"  Precipitation: {prediction['weather_summary']['precipitation_probability']}% chance, {prediction['weather_summary']['precipitation_total']} inches")
    except Exception as e:
        print(f"Error: {e}")


def test_travel_recommendation(broker: WeatherBroker, location: str, date: str = None):
    """Test travel recommendation."""
    date_str = date or "today"
    print_section(f"Travel Recommendation: {location} ({date_str})")
    try:
        recommendation = broker.get_travel_recommendation(location, date)
        print(f"Location: {recommendation['location']}")
        print(f"Date: {recommendation['date']}")
        print(f"\nRecommendation: {recommendation['recommendation']} (Score: {recommendation['score']}/100)")
        print(f"Summary: {recommendation['summary']}")
        print(f"\nFactors Considered:")
        for factor in recommendation['factors']:
            print(f"  - {factor}")
        print(f"\nWeather Details:")
        print(f"  Conditions: {recommendation['weather_details']['conditions']}")
        print(f"  Temperature: {recommendation['weather_details']['temperature_range']}")
        print(f"  Precipitation: {recommendation['weather_details']['precipitation_probability']}%")
        print(f"  Wind Gusts: {recommendation['weather_details']['wind_gusts']} mph")
    except Exception as e:
        print(f"Error: {e}")


def test_severe_weather_alerts(broker: WeatherBroker, location: str):
    """Test severe weather alerts."""
    print_section(f"Severe Weather Alerts: {location}")
    try:
        alerts = broker.get_severe_weather_alerts(location)
        print(f"Location: {alerts['location']}")
        print(f"Total Alerts: {alerts['alert_count']}")
        print(f"Has Severe Weather: {'YES' if alerts['has_severe_weather'] else 'NO'}")
        
        if alerts['has_severe_weather']:
            print(f"\nAlerts by Day:")
            for day_alert in alerts['alerts_by_day']:
                print(f"\n  Date: {day_alert['date']}")
                for alert in day_alert['alerts']:
                    print(f"    [{alert['severity'].upper()}] {alert['type']}: {alert['description']}")
        else:
            print("\nNo severe weather expected in the next 3 days.")
    except Exception as e:
        print(f"Error: {e}")


def test_historical_weather(broker: WeatherBroker, location: str, days_back: int = 7):
    """Test historical weather data."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    print_section(f"Historical Weather: {location} ({start_date} to {end_date})")
    try:
        history = broker.get_historical_weather(
            location,
            start_date.isoformat(),
            end_date.isoformat()
        )
        print(f"Location: {history['location']}")
        print(f"Period: {history['period']['start']} to {history['period']['end']}\n")
        
        print("Statistics:")
        stats = history['statistics']
        print(f"  Temperature:")
        print(f"    Average High: {stats['temperature']['avg_high']:.1f}°F")
        print(f"    Average Low: {stats['temperature']['avg_low']:.1f}°F")
        print(f"    Max High: {stats['temperature']['max_high']}°F")
        print(f"    Min Low: {stats['temperature']['min_low']}°F")
        print(f"  Precipitation:")
        print(f"    Total: {stats['precipitation']['total']:.2f} inches")
        print(f"    Average Daily: {stats['precipitation']['avg_daily']:.2f} inches")
        print(f"    Days with Precip: {stats['precipitation']['days_with_precip']}")
        
        print(f"\nDaily History (last 3 days shown):")
        for day in history['history'][-3:]:
            print(f"  {day['date']}: {day['conditions']}, {day['temperature']['low']}°F-{day['temperature']['high']}°F, {day['precipitation']}\" precip")
    except Exception as e:
        print(f"Error: {e}")


def test_compare_weather(broker: WeatherBroker, locations: list):
    """Test weather comparison across cities."""
    print_section(f"Weather Comparison (Current)")
    try:
        comparison = broker.compare_weather(locations)
        print(f"Comparison Type: {comparison['comparison_type']}")
        print(f"Timestamp: {comparison['timestamp']}\n")
        
        print("Locations:")
        for loc in comparison['locations']:
            if 'error' in loc:
                print(f"  {loc['location']}: Error - {loc['error']}")
            else:
                print(f"  {loc['location']}: {loc['temperature']}°F, {loc['conditions']}, {loc['humidity']}% humidity")
        
        if comparison['extremes']['warmest']:
            print(f"\nExtremes:")
            print(f"  Warmest: {comparison['extremes']['warmest']['location']} ({comparison['extremes']['warmest']['temperature']}°F)")
            print(f"  Coldest: {comparison['extremes']['coldest']['location']} ({comparison['extremes']['coldest']['temperature']}°F)")
            print(f"  Most Humid: {comparison['extremes']['most_humid']['location']} ({comparison['extremes']['most_humid']['humidity']}%)")
            print(f"  Windiest: {comparison['extremes']['windiest']['location']} ({comparison['extremes']['windiest']['wind_speed']} mph)")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("#  Weather Broker Test Suite")
    print("#  Using Open-Meteo API")
    print("#"*60)
    
    # Create weather broker instance
    broker = WeatherBroker()
    
    # Test location
    test_location = "San Francisco"
    
    # Test 1: Current Weather
    test_current_weather(broker, test_location)
    
    # Test 2: Weather Forecast
    test_forecast(broker, test_location, days=5)
    
    # Test 3: Umbrella Prediction (today)
    test_umbrella_prediction(broker, test_location)
    
    # Test 4: Umbrella Prediction (future date)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    test_umbrella_prediction(broker, test_location, tomorrow)
    
    # Test 5: Travel Recommendation (today)
    test_travel_recommendation(broker, test_location)
    
    # Test 6: Travel Recommendation (future date)
    test_travel_recommendation(broker, test_location, tomorrow)
    
    # Test 7: Severe Weather Alerts
    test_severe_weather_alerts(broker, test_location)
    
    # Test 8: Historical Weather
    test_historical_weather(broker, test_location, days_back=7)
    
    # Test 9: Compare Weather Across Cities
    test_cities = ["San Francisco", "New York", "Miami", "Chicago", "Seattle"]
    test_compare_weather(broker, test_cities)
    
    # Test 10: Test with coordinates
    print_section("Testing with Coordinates (37.7749,-122.4194 = San Francisco)")
    test_current_weather(broker, "37.7749,-122.4194")
    
    print("\n" + "#"*60)
    print("#  All Tests Completed!")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
