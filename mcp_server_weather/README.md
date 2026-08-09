# Weather MCP Server

A comprehensive Model Context Protocol (MCP) server that provides weather data and intelligent recommendations using the Open-Meteo API. Built with FastMCP and designed to be deployed as a Databricks App.

## Features

This MCP server exposes 7 powerful weather tools that provide comprehensive weather intelligence through a Model Context Protocol interface.

## Available Tools

### 1. `get_current_weather`
Retrieve real-time weather conditions for any location.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates

**Returns:**
* Current temperature, feels-like temperature
* Weather conditions and description
* Humidity, wind speed, and wind direction
* Cloud coverage and visibility
* Timestamp of observation

**Example:**
```json
{"location": "San Francisco, CA"}
```

### 2. `get_forecast`
Get detailed weather forecasts up to 16 days ahead.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates
* `days` (integer, optional): Number of forecast days (1-16), defaults to 7

**Returns:**
* Daily high/low temperatures
* Precipitation probability and amount
* Wind speed and direction
* Sunrise and sunset times
* Weather conditions for each day

**Example:**
```json
{"location": "New York", "days": 5}
```

### 3. `predict_umbrella_needed`
Intelligent umbrella recommendation based on precipitation analysis.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates
* `date` (string, optional): Target date (YYYY-MM-DD), defaults to today

**Returns:**
* Umbrella recommendation (Yes/No/Maybe)
* Confidence level (high/medium/low)
* Reasoning behind the recommendation
* Weather summary for the specified date

**Example:**
```json
{"location": "London", "date": "2024-12-25"}
```

### 4. `get_travel_recommendation`
Assess travel conditions and provide recommendations.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates
* `date` (string, optional): Target date (YYYY-MM-DD), defaults to today

**Returns:**
* Travel recommendation (Excellent/Good/Fair/Poor/Not Recommended)
* Numerical score (0-100)
* Contributing factors (temperature, precipitation, wind, visibility)
* Summary and detailed weather conditions

**Example:**
```json
{"location": "Paris, France", "date": "2024-12-31"}
```

### 5. `get_severe_weather_alerts`
Detect and report potential severe weather conditions.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates

**Returns:**
* Severe weather alerts for the next 3 days
* Severity levels (high/medium)
* Types of alerts: extreme temperatures, heavy precipitation, high winds, severe weather codes
* Date-organized alert summaries

**Example:**
```json
{"location": "Miami, FL"}
```

### 6. `get_historical_weather`
Retrieve and analyze historical weather data.

**Parameters:**
* `location` (string, required): City name, zip code, or "lat,lon" coordinates
* `start_date` (string, required): Start date (YYYY-MM-DD)
* `end_date` (string, required): End date (YYYY-MM-DD)

**Returns:**
* Daily historical records
* Temperature statistics (min, max, average)
* Precipitation totals and patterns
* Summary statistics for the period

**Example:**
```json
{"location": "Seattle", "start_date": "2024-01-01", "end_date": "2024-01-31"}
```

### 7. `compare_weather`
Compare weather conditions across multiple locations simultaneously.

**Parameters:**
* `locations` (string, required): Comma-separated list of locations
* `date` (string, optional): Target date (YYYY-MM-DD) for forecast comparison, defaults to current weather

**Returns:**
* Weather data for all specified locations
* Extremes identification (warmest, coldest, rainiest, windiest)
* Side-by-side comparison data

**Example:**
```json
{"locations": "New York,London,Tokyo,Sydney", "date": "2024-12-25"}
```

## Project Structure

```
mcp_server_weather/
├── app.py               # FastMCP server with tool definitions
├── weather_broker.py    # Weather data broker (existing)
├── requirements.txt     # Python dependencies
├── app.yaml            # Databricks App configuration
└── README.md           # This file
```

## Weather API & Authentication

### Open-Meteo API

This server uses the **[Open-Meteo API](https://open-meteo.com/)** as its data source.

**Key Features:**
* **No API Key Required** - Completely free access, no registration needed
* **No Authentication** - Direct HTTP GET requests without auth headers
* **Global Coverage** - Weather data for any location worldwide
* **High Data Quality** - Combines multiple weather models for accuracy
* **Generous Rate Limits** - ~10,000 requests/day on free tier
* **Comprehensive Data** - Current conditions, 16-day forecasts, and 2+ years of historical data

**Authentication Method:** None required ✓

The WeatherBroker makes direct HTTPS GET requests to `https://api.open-meteo.com/v1/` endpoints without any API keys or tokens. This simplifies deployment and eliminates the need for credential management.

## Setup & Installation

### Quick Start (Local Development)

**Step 1: Clone or navigate to the project**
```bash
cd /Workspace/Users/vwongoha@gmail.com/weatheragent/mcp_server_weather
```

**Step 2: Install Python dependencies**
```bash
pip install -r requirements.txt
```

Required packages:
* `fastmcp` - FastMCP framework for MCP server creation
* `uvicorn` - ASGI server for running the FastMCP app
* `requests` - HTTP library for API calls
* `python-dotenv` - Environment variable management (optional)

**Step 3: Run the server**
```bash
python app.py
```

The server will start on `http://0.0.0.0:8000`

**Step 4: Verify the server is running**
```bash
# Health check
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools

# Test a tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_current_weather", "arguments": {"location": "San Francisco"}}'
```

## Deployment as Databricks App (Production)

### Prerequisites

**Software Requirements:**
* Databricks CLI installed (`pip install databricks-cli`)
* Databricks CLI configured with authentication (`databricks configure --token`)
* Python 3.9 or higher

**Workspace Requirements:**
* Access to a Databricks workspace with Apps V2 enabled
* Permissions to create and deploy apps in the workspace
* The project files must be in a Databricks workspace folder

### Deployment Steps (CLI)

**Step 1: Verify your project files**
```bash
cd /Workspace/Users/vwongoha@gmail.com/weatheragent/mcp_server_weather
ls -la
```

You should see:
* `app.py` (FastMCP server)
* `weather_broker.py` (Weather data logic)
* `app.yaml` (App configuration)
* `requirements.txt` (Python dependencies)

**Step 2: Create the Databricks App**
```bash
databricks apps create weather-mcp-server
```

This registers the app in your workspace.

**Step 3: Deploy the app code**
```bash
databricks apps deploy weather-mcp-server --source-code-path .
```

This uploads your code and installs dependencies. The deployment process:
1. Packages all files in the current directory
2. Uploads to Databricks
3. Installs dependencies from `requirements.txt`
4. Builds the app container

**Step 4: Start the app**
```bash
databricks apps start weather-mcp-server
```

The app will start running and be assigned a public URL.

**Step 5: Get the app details and URL**
```bash
databricks apps get weather-mcp-server
```

Look for the `url` field in the output. Your MCP server will be accessible at:
```
https://<workspace-url>/apps/weather-mcp-server
```

**Step 6: Verify the deployment**
```bash
# Check app status
databricks apps get weather-mcp-server | grep status

# View app logs
databricks apps logs weather-mcp-server

# Test the health endpoint (replace with your actual app URL)
curl https://<workspace-url>/apps/weather-mcp-server/health
```

### Deployment Steps (UI)

Alternatively, deploy via the Databricks UI:

1. **Navigate to Apps**
   * Open your Databricks workspace
   * Click "Apps" in the left sidebar

2. **Create New App**
   * Click "Create App"
   * Name: `weather-mcp-server`

3. **Select Source**
   * Choose "Workspace folder"
   * Browse to `/Users/vwongoha@gmail.com/weatheragent/mcp_server_weather`

4. **Configure & Deploy**
   * The UI will read your `app.yaml` configuration
   * Click "Deploy"
   * Wait for the deployment to complete (2-3 minutes)

5. **Start the App**
   * Click "Start" in the app details page
   * The app URL will appear once it's running

### Post-Deployment

**Monitor Your App:**
```bash
# View real-time logs
databricks apps logs weather-mcp-server --follow

# Check resource usage
databricks apps get weather-mcp-server
```

**Update Your App:**
```bash
# Make changes to your code, then redeploy
databricks apps deploy weather-mcp-server --source-code-path .
databricks apps restart weather-mcp-server
```

**Stop/Delete Your App:**
```bash
# Stop the app (keeps the deployment)
databricks apps stop weather-mcp-server

# Delete the app completely
databricks apps delete weather-mcp-server
```

## Using the MCP Server

### Tool Examples

#### Get Current Weather
```json
{
  "tool": "get_current_weather",
  "arguments": {
    "location": "San Francisco"
  }
}
```

#### Get Forecast
```json
{
  "tool": "get_forecast",
  "arguments": {
    "location": "New York",
    "days": 5
  }
}
```

#### Predict Umbrella Needed
```json
{
  "tool": "predict_umbrella_needed",
  "arguments": {
    "location": "London",
    "date": "2024-12-25"
  }
}
```

#### Get Travel Recommendation
```json
{
  "tool": "get_travel_recommendation",
  "arguments": {
    "location": "Paris",
    "date": "2024-12-31"
  }
}
```

#### Compare Weather Across Cities
```json
{
  "tool": "compare_weather",
  "arguments": {
    "locations": "New York,London,Tokyo",
    "date": "2024-12-25"
  }
}
```

### Location Formats

The server accepts multiple location formats:
- **City name**: `"San Francisco"`, `"London"`, `"Tokyo"`
- **City with state/country**: `"New York, NY"`, `"Paris, France"`
- **Coordinates**: `"37.7749,-122.4194"` (latitude,longitude)

## API Endpoints

When deployed, the MCP server exposes HTTP endpoints:

- **POST /mcp** - MCP protocol endpoint for tool calls
- **GET /health** - Health check endpoint
- **GET /tools** - List available tools

## Configuration

### Environment Variables

- `PORT` - Server port (default: 8000)

### Resource Requirements

Configured in `app.yaml`:
- CPU: 1 core
- Memory: 512Mi

Adjust these based on your expected load.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client Layer                         │
│  (Databricks Assistant, Claude Desktop, or any MCP client)      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST /mcp
                             │ (MCP Protocol)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastMCP Server (app.py)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Exposed MCP Tools:                                        │  │
│  │  • get_current_weather                                    │  │
│  │  • get_forecast                                           │  │
│  │  • predict_umbrella_needed                                │  │
│  │  • get_travel_recommendation                              │  │
│  │  • get_severe_weather_alerts                              │  │
│  │  • get_historical_weather                                 │  │
│  │  • compare_weather                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                    Delegates to ▼                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │        WeatherBroker (weather_broker.py)                  │  │
│  │  • Geocoding (city → lat/lon)                             │  │
│  │  • API request handling                                   │  │
│  │  • Data transformation                                    │  │
│  │  • Intelligence layer (recommendations, alerts)           │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS GET
                             │ (No Auth Required)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Open-Meteo Weather API                       │
│                    https://api.open-meteo.com                   │
│  • Current weather data                                         │
│  • 16-day forecasts                                             │
│  • Historical data (2+ years)                                   │
│  • Free tier: No API key required                               │
│  • Rate limit: ~10,000 requests/day                             │
└─────────────────────────────────────────────────────────────────┘

Deployment Options:
  ┌─────────────────┐        ┌──────────────────┐
  │ Databricks App  │   OR   │ Local/Cloud Host │
  │ (Recommended)   │        │ (Docker/VM)      │
  └─────────────────┘        └──────────────────┘
```

## Data Source

This server uses the [Open-Meteo API](https://open-meteo.com/), which provides:
- Free weather data (no API key required)
- Global coverage
- High accuracy forecasts
- Historical weather data
- Real-time updates

## Error Handling

All tools return JSON responses. Errors are returned in the format:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Development

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# In another terminal, test with curl
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_current_weather", "arguments": {"location": "San Francisco"}}'
```

### Adding New Tools

1. Add the function to `weather_broker.py`
2. Expose it in `app.py` with the `@mcp.tool()` decorator
3. Document the tool in this README

## License

This project uses the Open-Meteo API which is free for non-commercial use.

## Support

For issues or questions:
- Check the [FastMCP documentation](https://github.com/jlowin/fastmcp)
- Review the [Open-Meteo API docs](https://open-meteo.com/en/docs)
- File an issue in your project repository