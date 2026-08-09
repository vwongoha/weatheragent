# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Import Weather Broker
import sys
sys.path.insert(0, './mcp_server_weather')

from weather_broker import WeatherBroker
from datetime import datetime, timedelta

# Initialize the weather broker
broker = WeatherBroker()

print("✅ Weather Broker initialized successfully!")

# COMMAND ----------

# DBTITLE 1,1. Current Weather Conditions
# Test 1: Get current weather for any location
location = "San Francisco"  # Change this to any city!

weather = broker.get_current_weather(location)

print(f"\n🌡️ CURRENT WEATHER: {weather['location']}")
print("=" * 60)
print(f"🌡️  Temperature: {weather['temperature']}°F (feels like {weather['feels_like']}°F)")
print(f"☁️  Conditions: {weather['conditions']}")
print(f"💧 Humidity: {weather['humidity']}%")
print(f"🌬️  Wind: {weather['wind']['speed']} mph (gusts: {weather['wind']['gusts']} mph)")
print(f"☁️  Cloud Cover: {weather['cloud_cover']}%")
print(f"🌧️  Precipitation: {weather['precipitation']} inches")
print(f"🕒 Updated: {weather['timestamp']}")
print(f"📍 Coordinates: {weather['coordinates']['latitude']}, {weather['coordinates']['longitude']}")

# COMMAND ----------

# DBTITLE 1,2. Multi-Day Forecast
# Test 2: Get weather forecast
location = "New York"
days = 5

forecast = broker.get_forecast(location, days)

print(f"\n📅 {days}-DAY FORECAST: {forecast['location']}")
print("=" * 60)

for day in forecast['forecast']:
    print(f"\n📆 {day['date']}")
    print(f"  {day['conditions']}")
    print(f"  🌡️ Temp: {day['temperature']['low']}°F - {day['temperature']['high']}°F")
    print(f"  💧 Precipitation: {day['precipitation']['probability']}% chance, {day['precipitation']['total']}\"")
    print(f"  🌬️ Wind: {day['wind']['max_speed']} mph (gusts: {day['wind']['max_gusts']} mph)")
    print(f"  🌅 Sunrise: {day['sunrise'].split('T')[1]} | 🌇 Sunset: {day['sunset'].split('T')[1]}")

# COMMAND ----------

# DBTITLE 1,3. Umbrella Prediction (Smart Reasoning)
# Test 3: Should you bring an umbrella?
location = "Seattle"
date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Tomorrow

prediction = broker.predict_umbrella_needed(location, date)

print(f"\n☔ UMBRELLA PREDICTION: {prediction['location']}")
print("=" * 60)
print(f"📆 Date: {prediction['date']}")
print(f"\n{'\u2705 BRING UMBRELLA' if prediction['umbrella_needed'] else '❌ NO UMBRELLA NEEDED'}")
print(f"🎯 Confidence: {prediction['confidence'].upper()}")

print(f"\n🧠 Reasoning:")
for reason in prediction['reasons']:
    print(f"  • {reason}")

print(f"\n🌤️ Weather Summary:")
print(f"  Conditions: {prediction['weather_summary']['conditions']}")
print(f"  Temperature: {prediction['weather_summary']['temperature_low']}°F - {prediction['weather_summary']['temperature_high']}°F")
print(f"  Rain chance: {prediction['weather_summary']['precipitation_probability']}%")

# COMMAND ----------

# DBTITLE 1,4. Travel Recommendation (Scoring System)
# Test 4: Is it a good day to travel?
location = "Miami"
date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

recommendation = broker.get_travel_recommendation(location, date)

print(f"\n✈️ TRAVEL RECOMMENDATION: {recommendation['location']}")
print("=" * 60)
print(f"📆 Date: {recommendation['date']}")

# Color code the score
score = recommendation['score']
if score >= 80:
    emoji = "💚"
elif score >= 60:
    emoji = "💛"
elif score >= 40:
    emoji = "🧡"
else:
    emoji = "❤️"

print(f"\n{emoji} {recommendation['recommendation'].upper()} (Score: {score}/100)")
print(f"📝 {recommendation['summary']}")

print(f"\n📊 Factors Considered:")
for factor in recommendation['factors']:
    print(f"  • {factor}")

print(f"\n🌤️ Weather Details:")
print(f"  Conditions: {recommendation['weather_details']['conditions']}")
print(f"  Temperature: {recommendation['weather_details']['temperature_range']}")
print(f"  Rain chance: {recommendation['weather_details']['precipitation_probability']}%")
print(f"  Wind gusts: {recommendation['weather_details']['wind_gusts']} mph")

# COMMAND ----------

# DBTITLE 1,5. Severe Weather Alerts
# Test 5: Check for severe weather
location = "Chicago"

alerts = broker.get_severe_weather_alerts(location)

print(f"\n⚠️ SEVERE WEATHER ALERTS: {alerts['location']}")
print("=" * 60)
print(f"🚨 Total Alerts: {alerts['alert_count']}")
print(f"🌩️ Severe Weather: {'YES' if alerts['has_severe_weather'] else 'NO'}")

if alerts['has_severe_weather']:
    print(f"\n📅 Alerts by Day:")
    for day_alert in alerts['alerts_by_day']:
        print(f"\n  📆 {day_alert['date']}")
        for alert in day_alert['alerts']:
            severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡"
            print(f"    {severity_emoji} [{alert['severity'].upper()}] {alert['type']}")
            print(f"       {alert['description']}")
else:
    print("\n✅ No severe weather expected in the next 3 days!")

# COMMAND ----------

# DBTITLE 1,6. Historical Weather Data
# Test 6: Get historical weather data
location = "Los Angeles"
days_back = 7

end_date = datetime.now().date()
start_date = end_date - timedelta(days=days_back)

history = broker.get_historical_weather(
    location,
    start_date.isoformat(),
    end_date.isoformat()
)

print(f"\n📈 HISTORICAL WEATHER: {history['location']}")
print("=" * 60)
print(f"📅 Period: {history['period']['start']} to {history['period']['end']}")

stats = history['statistics']
print(f"\n🌡️ Temperature Statistics:")
print(f"  Average High: {stats['temperature']['avg_high']:.1f}°F")
print(f"  Average Low: {stats['temperature']['avg_low']:.1f}°F")
print(f"  Max High: {stats['temperature']['max_high']}°F")
print(f"  Min Low: {stats['temperature']['min_low']}°F")

print(f"\n💧 Precipitation Statistics:")
print(f"  Total: {stats['precipitation']['total']:.2f} inches")
print(f"  Daily Average: {stats['precipitation']['avg_daily']:.2f} inches")
print(f"  Days with Precipitation: {stats['precipitation']['days_with_precip']}")

print(f"\n📅 Daily History (last 3 days):")
for day in history['history'][-3:]:
    print(f"  {day['date']}: {day['conditions']}, {day['temperature']['low']}°F-{day['temperature']['high']}°F")

# COMMAND ----------

# DBTITLE 1,7. Compare Weather Across Cities
# Test 7: Compare weather across multiple cities
cities = ["San Francisco", "New York", "Miami", "Chicago", "Seattle", "Austin"]

comparison = broker.compare_weather(cities)

print(f"\n🌍 WEATHER COMPARISON ACROSS CITIES")
print("=" * 60)
print(f"🕒 Timestamp: {comparison['timestamp']}\n")

print("🎯 Current Conditions:")
for loc in comparison['locations']:
    if 'error' not in loc:
        temp_emoji = "🔥" if loc['temperature'] > 80 else "❄️" if loc['temperature'] < 50 else "🌡️"
        print(f"  {temp_emoji} {loc['location'][:30]:30s} | {loc['temperature']:5.1f}°F | {loc['conditions']:20s} | {loc['humidity']}% humidity")

if comparison['extremes']['warmest']:
    print(f"\n🏆 EXTREMES:")
    print(f"  🔥 Warmest: {comparison['extremes']['warmest']['location']} ({comparison['extremes']['warmest']['temperature']}°F)")
    print(f"  ❄️  Coldest: {comparison['extremes']['coldest']['location']} ({comparison['extremes']['coldest']['temperature']}°F)")
    print(f"  💧 Most Humid: {comparison['extremes']['most_humid']['location']} ({comparison['extremes']['most_humid']['humidity']}%)")
    print(f"  🌬️  Windiest: {comparison['extremes']['windiest']['location']} ({comparison['extremes']['windiest']['wind_speed']} mph)")

# COMMAND ----------

# DBTITLE 1,8. Test with Coordinates
# Test 8: Use coordinates instead of city names
# Example: Paris, France coordinates
lat_lon = "48.8566,2.3522"

weather = broker.get_current_weather(lat_lon)

print(f"\n📍 WEATHER BY COORDINATES")
print("=" * 60)
print(f"🌍 Location: {weather['location']}")
print(f"📍 Coordinates: {weather['coordinates']['latitude']}, {weather['coordinates']['longitude']}")
print(f"\n🌡️ Temperature: {weather['temperature']}°F")
print(f"☁️  Conditions: {weather['conditions']}")
print(f"💧 Humidity: {weather['humidity']}%")

print("\n✨ Try these famous locations:")
print("  🗼 Eiffel Tower: 48.8584,2.2945")
print("  🗽 Statue of Liberty: 40.6892,-74.0445")
print("  🏯 Tokyo Tower: 35.6586,139.7454")
print("  🏛️ Sydney Opera House: -33.8568,151.2153")

# COMMAND ----------

# DBTITLE 1,9. Interactive: Test Your Own Location
# Test 9: Customize and test your own location!
# Change these variables to test different scenarios

test_location = "London"  # 👈 CHANGE THIS
test_days = 3             # 👈 CHANGE THIS (1-16)

print(f"\n🎯 CUSTOM WEATHER TEST")
print("=" * 60)

# Current weather
print(f"\n1️⃣ CURRENT WEATHER:")
current = broker.get_current_weather(test_location)
print(f"   {current['temperature']}°F, {current['conditions']}")

# Forecast
print(f"\n2️⃣ {test_days}-DAY FORECAST:")
forecast = broker.get_forecast(test_location, test_days)
for day in forecast['forecast']:
    print(f"   {day['date']}: {day['temperature']['low']}°F-{day['temperature']['high']}°F, {day['conditions']}")

# Umbrella check
print(f"\n3️⃣ UMBRELLA NEEDED TODAY?")
umbrella = broker.predict_umbrella_needed(test_location)
print(f"   {'\u2705 YES' if umbrella['umbrella_needed'] else '❌ NO'} ({umbrella['confidence']} confidence)")

# Travel recommendation
print(f"\n4️⃣ TRAVEL CONDITIONS:")
travel = broker.get_travel_recommendation(test_location)
print(f"   {travel['recommendation']} (Score: {travel['score']}/100)")

print(f"\n✅ All tests completed for {current['location']}!")