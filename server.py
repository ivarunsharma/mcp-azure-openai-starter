"""
Basic MCP Server — exposes simple tools: calculator + weather lookup
Run this via: python server.py (the client will start it automatically via stdio)
"""

import httpx
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

mcp = FastMCP("BasicMCP")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city (uses OpenWeatherMap API)."""
    api_key = os.getenv("weather_api_key")
    if not api_key:
        return "Weather API key not found in .env"

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        return f"{city}: {temp}°C, {desc}, humidity {humidity}%"
    except httpx.HTTPStatusError as e:
        return f"Error fetching weather: {e.response.status_code}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
