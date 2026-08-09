#!/bin/bash
# Deployment script for Weather MCP Server Databricks App

set -e  # Exit on error

APP_NAME="weather-mcp-server"
SOURCE_PATH="/Workspace/Users/vwongoha@gmail.com/weatheragent/mcp_server_weather"

echo "====================================="
echo "Weather MCP Server Deployment Script"
echo "====================================="
echo ""

# Check if databricks CLI is available
if ! command -v databricks &> /dev/null; then
    echo "Error: databricks CLI not found. Please install it first."
    echo "Install: pip install databricks-cli"
    exit 1
fi

echo "Step 1: Checking if app exists..."
if databricks apps get $APP_NAME &> /dev/null; then
    echo "  App '$APP_NAME' already exists"
    echo ""
    echo "Step 2: Deploying updated code..."
    databricks apps deploy $APP_NAME --source-code-path $SOURCE_PATH
    echo "  ✓ Deployment successful"
else
    echo "  App does not exist yet"
    echo ""
    echo "Step 2: Creating new app..."
    databricks apps create $APP_NAME
    echo "  ✓ App created"
    echo ""
    echo "Step 3: Deploying code..."
    databricks apps deploy $APP_NAME --source-code-path $SOURCE_PATH
    echo "  ✓ Deployment successful"
fi

echo ""
echo "Step 4: Starting the app..."
databricks apps start $APP_NAME
echo "  ✓ App started"

echo ""
echo "Step 5: Getting app status..."
databricks apps get $APP_NAME

echo ""
echo "====================================="
echo "✓ Deployment Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "  1. Check logs: databricks apps logs $APP_NAME"
echo "  2. Get app URL: databricks apps get $APP_NAME"
echo "  3. Stop app: databricks apps stop $APP_NAME"
echo ""