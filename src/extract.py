from __future__ import annotations
import requests
import pandas as pd

WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_weather_2024() -> pd.DataFrame:
    params = {"latitude":40.7128,"longitude":-74.0060,"start_date":"2024-01-01","end_date":"2024-12-31","daily":"temperature_2m_mean,precipitation_sum,wind_speed_10m_max","timezone":"America/New_York"}
    response = requests.get(WEATHER_URL, params=params, timeout=60)
    response.raise_for_status()
    return pd.DataFrame(response.json()["daily"])

