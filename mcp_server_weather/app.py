"""Weather MCP Server - Streamable HTTP Implementation

A FastMCP server that exposes comprehensive weather data tools via HTTP.
Designed to be deployed as a Databricks App.
"""

from fastmcp import FastMCP
from weather_broker import WeatherBroker
from typing import Optional
import json
import os

# Initialize FastMCP with streamable HTTP configuration
mcp = FastMCP("Weather Service")

# Initialize the weather broker
weather_broker = WeatherBroker()


@mcp.tool()
def get_current_weather(location: str) -> str:
    """Get current weather conditions for a location.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        
    Returns:
        JSON string with current weather data including temperature,
        conditions, humidity, wind speed, and more
    """
    try:
        result = weather_broker.get_current_weather(location)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_forecast(location: str, days: int = 7) -> str:
    """Get weather forecast for a location.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        days: Number of days to forecast (1-16), defaults to 7
        
    Returns:
        JSON string with daily forecast data including high/low temperatures,
        precipitation probability, wind conditions, sunrise/sunset
    """
    try:
        result = weather_broker.get_forecast(location, days)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def predict_umbrella_needed(location: str, date: Optional[str] = None) -> str:
    """Predict if an umbrella is needed for a specific date.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        date: Date string (YYYY-MM-DD) or None for today
        
    Returns:
        JSON string with umbrella recommendation, confidence level,
        reasoning, and weather summary
    """
    try:
        result = weather_broker.predict_umbrella_needed(location, date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_travel_recommendation(location: str, date: Optional[str] = None) -> str:
    """Get travel recommendation for a specific date based on weather conditions.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        date: Date string (YYYY-MM-DD) or None for today
        
    Returns:
        JSON string with travel recommendation (Excellent/Good/Fair/Poor/Not Recommended),
        score (0-100), summary, contributing factors, and weather details
    """
    try:
        result = weather_broker.get_travel_recommendation(location, date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_severe_weather_alerts(location: str) -> str:
    """Get severe weather alerts for a location.
    
    Analyzes forecast data to detect potentially severe conditions including
    extreme temperatures, heavy precipitation, high winds, and severe weather codes.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        
    Returns:
        JSON string with detected severe weather conditions for the next 3 days,
        organized by date with severity levels (high/medium)
    """
    try:
        result = weather_broker.get_severe_weather_alerts(location)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_historical_weather(location: str, start_date: str, end_date: str) -> str:
    """Get historical weather data for a location.
    
    Args:
        location: City name, zip code, or "lat,lon" coordinates
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON string with historical weather data and statistics including
        temperature ranges, precipitation totals, and averages
    """
    try:
        result = weather_broker.get_historical_weather(location, start_date, end_date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def compare_weather(locations: str, date: Optional[str] = None) -> str:
    """Compare weather across multiple cities.
    
    Args:
        locations: Comma-separated list of city names, zip codes, or "lat,lon" strings
                  Example: "New York,London,Tokyo" or "40.7,-74.0,51.5,-0.1,35.6,139.7"
        date: Date string (YYYY-MM-DD) or None for current weather comparison
        
    Returns:
        JSON string with comparison data including all locations and extremes
        (warmest, coldest, most humid, windiest for current; warmest, coldest,
        rainiest for forecast)
    """
    try:
        # Parse comma-separated locations
        location_list = [loc.strip() for loc in locations.split(',')]
        result = weather_broker.compare_weather(location_list, date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Run the server with streamable HTTP support
if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Convert MCP server to HTTP app with stateless mode for Databricks Apps
    # stateless_http=True is important for horizontally scaled apps
    mcp_app = mcp.http_app(stateless_http=True)
    
    # Run with uvicorn for Databricks App deployment
    import uvicorn
    uvicorn.run(
        mcp_app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )