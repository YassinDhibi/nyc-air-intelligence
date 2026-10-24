from __future__ import annotations
import json
from pathlib import Path
import requests
import pandas as pd

WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_weather_2024() -> dict:
    params = {"latitude":40.7128,"longitude":-74.0060,"start_date":"2024-01-01","end_date":"2024-12-31","daily":"temperature_2m_mean,precipitation_sum,wind_speed_10m_max","timezone":"America/New_York"}
    response = requests.get(WEATHER_URL, params=params, timeout=60)
    response.raise_for_status()
    return response.json()

def load_pollution_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def save_weather_json(payload: dict, path: Path) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def load_weather_json(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "daily" not in payload:
        raise ValueError("Le fichier météo JSON ne contient pas la clé 'daily'.")
    return pd.DataFrame(payload["daily"])

def load_station_reference_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name="stations", dtype={"site_id": "string"})

