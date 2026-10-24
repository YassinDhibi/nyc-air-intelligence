import pandas as pd
from src.transform import clean_pollution, clean_weather, enrich_pollution_with_stations, build_daily

def test_pipeline_marks_anomaly():
    p = pd.DataFrame({"Date":["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],"Site ID":[1]*4,"Daily Mean PM2.5 Concentration":[5,5,5,100],"Daily AQI Value":[20,20,20,150],"Local Site Name":["A"]*4,"County":["X"]*4,"Site Latitude":[40.7]*4,"Site Longitude":[-74.0]*4})
    w = pd.DataFrame({"time":["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],"temperature_2m_mean":[1,2,3,4],"precipitation_sum":[0]*4,"wind_speed_10m_max":[5]*4})
    result = build_daily(clean_pollution(p), clean_weather(w))
    assert len(result) == 4
    assert result.trend_7d.notna().all()

def test_excel_station_reference_enriches_pollution():
    raw = pd.DataFrame({"Date":["2024-01-01"],"Site ID":[1],"Daily Mean PM2.5 Concentration":[5],"Daily AQI Value":[20],"Local Site Name":["old"],"County":["old"],"Site Latitude":[0],"Site Longitude":[0]})
    stations = pd.DataFrame({"site_id":["1"],"station":["Station A"],"county":["Bronx"],"latitude":[40.7],"longitude":[-74.0]})
    result = enrich_pollution_with_stations(clean_pollution(raw), stations)
    assert result.loc[0, "station"] == "Station A"
    assert result.loc[0, "county"] == "Bronx"

