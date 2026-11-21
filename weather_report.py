"""
Lab Assignment 1: Working with a Public REST API Using Python

Fetches current weather data from the OpenWeatherMap API,
parses the JSON response, stores it in a custom class,
and prints a formatted summary.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

API_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherReport:
    """Stores and organizes weather data retrieved from the API."""

    def __init__(self, city, country, temperature, feels_like, humidity,
                 pressure, description, wind_speed, sunrise, sunset):
        self.city = city
        self.country = country
        self.temperature = temperature
        self.feels_like = feels_like
        self.humidity = humidity
        self.pressure = pressure
        self.description = description
        self.wind_speed = wind_speed
        self.sunrise = sunrise
        self.sunset = sunset

    @classmethod
    def from_json(cls, data):
        """Build a WeatherReport from the parsed JSON response."""
        tz = timezone(timedelta(seconds=data.get("timezone", 0)))

        def to_local_time(ts):
            return datetime.fromtimestamp(ts, tz).strftime("%H:%M")

        return cls(
            city=data["name"],
            country=data["sys"]["country"],
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            description=data["weather"][0]["description"].title(),
            wind_speed=data["wind"]["speed"],
            sunrise=to_local_time(data["sys"]["sunrise"]),
            sunset=to_local_time(data["sys"]["sunset"]),
        )

    def display(self):
        """Print a formatted summary."""
        line = "=" * 40
        print(line)
        print(f"  Weather Report: {self.city}, {self.country}")
        print(line)
        print(f"  Conditions   : {self.description}")
        print(f"  Temperature  : {self.temperature:.1f} °C")
        print(f"  Feels like   : {self.feels_like:.1f} °C")
        print(f"  Humidity     : {self.humidity} %")
        print(f"  Pressure     : {self.pressure} hPa")
        print(f"  Wind speed   : {self.wind_speed} m/s")
        print(f"  Sunrise      : {self.sunrise} (local)")
        print(f"  Sunset       : {self.sunset} (local)")
        print(line)


def fetch_weather(city, api_key):
    """Call the API and return the parsed JSON as a dict."""
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()  # raises an error for 4xx/5xx responses
    return response.json()


def main():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        sys.exit("Error: OPENWEATHER_API_KEY not found. Check your .env file.")

    city = input("Enter a city name: ").strip() or "Cairo"

    try:
        data = fetch_weather(city, api_key)
        report = WeatherReport.from_json(data)
        report.display()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            print("Error: Invalid API key (new keys may take time to activate).")
        elif err.response.status_code == 404:
            print(f"Error: City '{city}' not found.")
        else:
            print(f"HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
    except (KeyError, IndexError) as err:
        print(f"Unexpected response format, missing field: {err}")


if __name__ == "__main__":
    main()
