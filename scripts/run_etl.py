from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import RAW_DIR, PROCESSED_DIR
from src.extract import (
    fetch_weather_2024,
    load_pollution_csv,
    load_station_reference_excel,
    load_weather_json,
    save_weather_json,
)
from src.transform import clean_pollution, clean_weather, enrich_pollution_with_stations, build_daily
from src.database import replace_collection, ensure_indexes

def records(df):
    return df.where(pd.notna(df), None).to_dict("records")

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True); PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pollution_raw = load_pollution_csv(RAW_DIR / "pollution_nyc_2024.csv")
    stations_raw = load_station_reference_excel(RAW_DIR / "stations_nyc.xlsx")
    pollution = enrich_pollution_with_stations(clean_pollution(pollution_raw), stations_raw)
    weather_json = RAW_DIR / "weather_nyc_2024.json"
    save_weather_json(fetch_weather_2024(), weather_json)
    weather_raw = load_weather_json(weather_json)
    weather = clean_weather(weather_raw)
    daily = build_daily(pollution, weather)
    pollution.to_csv(PROCESSED_DIR / "pollution_clean.csv", index=False)
    weather.to_csv(PROCESSED_DIR / "weather_clean.csv", index=False)
    daily.to_csv(PROCESSED_DIR / "daily_analysis.csv", index=False)
    print("Formats lus: CSV (pollution), JSON (météo), XLSX (référentiel stations)")
    for frame in (pollution, weather, daily):
        for col in frame.select_dtypes(include=["datetime64[ns]"]).columns:
            frame[col] = frame[col].dt.to_pydatetime()
    print("MongoDB:", replace_collection("pollution", records(pollution)), replace_collection("weather", records(weather)), replace_collection("daily_analysis", records(daily)))
    ensure_indexes()

if __name__ == "__main__": main()

