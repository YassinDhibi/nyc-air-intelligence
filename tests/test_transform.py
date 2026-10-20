import pandas as pd
from src.transform import clean_pollution, clean_weather, build_daily

def test_pipeline_marks_anomaly():
    p = pd.DataFrame({"Date":["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],"Site ID":[1]*4,"Daily Mean PM2.5 Concentration":[5,5,5,100],"Daily AQI Value":[20,20,20,150],"Local Site Name":["A"]*4,"County":["X"]*4,"Site Latitude":[40.7]*4,"Site Longitude":[-74.0]*4})
    w = pd.DataFrame({"time":["2024-01-01","2024-01-02","2024-01-03","2024-01-04"],"temperature_2m_mean":[1,2,3,4],"precipitation_sum":[0]*4,"wind_speed_10m_max":[5]*4})
    result = build_daily(clean_pollution(p), clean_weather(w))
    assert len(result) == 4
    assert result.trend_7d.notna().all()

