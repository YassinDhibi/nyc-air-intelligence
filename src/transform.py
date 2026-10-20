from __future__ import annotations
import pandas as pd

PM = "Daily Mean PM2.5 Concentration"
AQI = "Daily AQI Value"

def clean_pollution(df: pd.DataFrame) -> pd.DataFrame:
    required = {"Date", "Site ID", PM, AQI, "Local Site Name", "County", "Site Latitude", "Site Longitude"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Colonnes pollution manquantes: {sorted(missing)}")
    out = df.copy()
    out["date"] = pd.to_datetime(out["Date"], errors="coerce")
    out["site_id"] = out["Site ID"].astype("string")
    out["pm25"] = pd.to_numeric(out[PM], errors="coerce")
    out["aqi"] = pd.to_numeric(out[AQI], errors="coerce")
    out = out.dropna(subset=["date", "site_id", "pm25"]).drop_duplicates()
    out = out[(out.pm25 >= 0) & (out.pm25 <= 1000)]
    return out[["date", "site_id", "pm25", "aqi", "Local Site Name", "County", "Site Latitude", "Site Longitude"]].rename(columns={"Local Site Name":"station", "County":"county", "Site Latitude":"latitude", "Site Longitude":"longitude"})

def clean_weather(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {"time":"date", "temperature_2m_mean":"temperature", "precipitation_sum":"precipitation", "wind_speed_10m_max":"wind_speed"}
    out = df.rename(columns=aliases).copy()
    required = {"date", "temperature", "precipitation", "wind_speed"}
    missing = required.difference(out.columns)
    if missing:
        raise ValueError(f"Colonnes météo manquantes: {sorted(missing)}")
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for col in required - {"date"}:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna(subset=["date", "temperature"]).drop_duplicates("date")

def build_daily(pollution: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    daily = pollution.groupby("date", as_index=False).agg(pm25_mean=("pm25","mean"), pm25_max=("pm25","max"), aqi_mean=("aqi","mean"), stations=("site_id","nunique"))
    result = daily.merge(weather, on="date", how="left")
    threshold = result.pm25_mean.mean() + 2 * result.pm25_mean.std()
    result["anomaly"] = result.pm25_mean > threshold
    result["trend_7d"] = result.pm25_mean.rolling(7, min_periods=1).mean()
    return result

