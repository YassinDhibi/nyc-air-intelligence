from __future__ import annotations
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from src.database import db, monthly_aggregation, county_aggregation

st.set_page_config(page_title="NYC Air Intelligence", page_icon="🌍", layout="wide")
st.title("NYC Air Intelligence")
st.caption("Pollution PM2.5 et météo à New York — 2024")

try:
    database = db()
    daily = pd.DataFrame(list(database.daily_analysis.find({}, {"_id":0})))
except Exception as exc:
    st.error(f"MongoDB indisponible. Lancez Docker puis l'ETL. Détail: {exc}")
    st.stop()

daily["date"] = pd.to_datetime(daily.date)
with st.sidebar:
    st.header("Filtres")
    start, end = st.date_input("Période", (date(2024,1,1), date(2024,12,31)))
    max_pm = st.slider("PM2.5 maximal", 5, 200, 200)
    alert_threshold = st.slider("Seuil d'alerte PM2.5", 5, 100, 25)
mask = (daily.date.dt.date >= start) & (daily.date.dt.date <= end) & (daily.pm25_mean <= max_pm)
view = daily.loc[mask].copy()

c1,c2,c3,c4 = st.columns(4)
c1.metric("PM2.5 moyen", f"{view.pm25_mean.mean():.1f} µg/m³")
c2.metric("Pic PM2.5", f"{view.pm25_max.max():.1f} µg/m³")
c3.metric("AQI moyen", f"{view.aqi_mean.mean():.0f}")
c4.metric("Anomalies", int(view.anomaly.sum()))

if not view.empty and view.pm25_max.max() >= alert_threshold:
    st.warning(f"Alerte pollution : un pic de {view.pm25_max.max():.1f} µg/m³ dépasse le seuil de {alert_threshold} µg/m³.")
else:
    st.success("Aucune alerte de pollution pour la sélection actuelle.")

st.plotly_chart(px.line(view, x="date", y=["pm25_mean","trend_7d"], title="Évolution et tendance sur 7 jours"), use_container_width=True)
left,right = st.columns(2)
left.plotly_chart(px.scatter(view, x="temperature", y="pm25_mean", color="anomaly", title="Température et pollution"), use_container_width=True)
right.plotly_chart(px.histogram(view, x="pm25_mean", nbins=30, title="Distribution du PM2.5"), use_container_width=True)

st.subheader("Agrégations MongoDB")
monthly = pd.DataFrame(monthly_aggregation()).rename(columns={"_id":"month"})
county = pd.DataFrame(county_aggregation()).rename(columns={"_id":"county"})
left,right = st.columns(2)
left.plotly_chart(px.bar(monthly, x="month", y="pm25", title="PM2.5 moyen par mois"), use_container_width=True)
right.plotly_chart(px.bar(county, x="county", y="pm25", title="PM2.5 moyen par comté"), use_container_width=True)

st.subheader("Ajouter une observation")
with st.form("add_observation", clear_on_submit=True):
    obs_date = st.date_input("Date", date(2024,1,1)); site = st.text_input("Identifiant station", max_chars=20)
    pm25 = st.number_input("PM2.5", 0.0, 1000.0, 10.0); aqi = st.number_input("AQI", 0, 500, 50)
    submitted = st.form_submit_button("Valider et ajouter")
if submitted:
    if not site.strip(): st.error("L'identifiant station est obligatoire.")
    else:
        database.pollution.insert_one({"date":pd.Timestamp(obs_date).to_pydatetime(),"site_id":site.strip(),"pm25":pm25,"aqi":aqi,"source":"formulaire"})
        st.success("Observation validée et ajoutée à MongoDB.")

st.download_button("Exporter la sélection CSV", view.to_csv(index=False).encode(), "analyse_nyc_2024.csv", "text/csv")

