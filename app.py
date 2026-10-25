from __future__ import annotations
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from src.database import db, monthly_aggregation, county_aggregation
from src.presentation import brand_header, section, metric_cards, chart_style, LIME, CORAL, CREAM

st.set_page_config(page_title="NYC Air Intelligence", page_icon="🌍", layout="wide")
brand_header()

try:
    database = db()
    daily = pd.DataFrame(list(database.daily_analysis.find({}, {"_id":0})))
except Exception as exc:
    st.error(f"MongoDB indisponible. Lancez Docker puis l'ETL. Détail: {exc}")
    st.stop()

if daily.empty:
    st.info("Aucune donnée disponible. Lancez l'ETL pour charger les observations.")
    st.stop()
daily["date"] = pd.to_datetime(daily.date)
daily = daily.sort_values("date")

def as_date(value, fallback: date) -> date:
    """Convert Streamlit's transient date-picker values to a date."""
    while isinstance(value, (tuple, list)):
        if not value:
            return fallback
        value = value[0]
    return value if isinstance(value, date) else fallback

with st.sidebar:
    st.markdown('<div class="sidebar-brand">NYC AIR<br><span>INTELLIGENCE.</span></div>', unsafe_allow_html=True)
    st.caption("EXPLORATEUR / 2024")
    st.header("Votre point de vue.")
    selected_period = st.date_input("Période", (date(2024,1,1), date(2024,12,31)))
    if isinstance(selected_period, (tuple, list)):
        if len(selected_period) == 2:
            start = as_date(selected_period[0], date(2024, 1, 1))
            end = as_date(selected_period[1], start)
        elif len(selected_period) == 1:
            start = end = as_date(selected_period[0], date(2024, 1, 1))
        else:
            start, end = date(2024, 1, 1), date(2024, 12, 31)
    else:
        start = end = as_date(selected_period, date(2024, 1, 1))
    max_pm = st.slider("PM2.5 maximal", 5, 200, 200)
    alert_threshold = st.slider("Seuil d'alerte PM2.5", 5, 100, 25)
    st.markdown('<div class="sidebar-note">Concentrations en µg/m³.<br>Les filtres s’appliquent à la vue d’ensemble et à l’export CSV. Les agrégations couvrent toute la base.</div>', unsafe_allow_html=True)
mask = (daily.date.dt.date >= start) & (daily.date.dt.date <= end) & (daily.pm25_mean <= max_pm)
view = daily.loc[mask].copy()

metric_cards(view)

if view.empty:
    st.info("Aucun jour ne correspond à ces filtres. Élargissez la période ou augmentez le PM2.5 maximal.")
elif view.pm25_max.max() >= alert_threshold:
    st.warning(f"Alerte pollution : un pic de {view.pm25_max.max():.1f} µg/m³ dépasse le seuil de {alert_threshold} µg/m³.")
else:
    st.success("Aucune alerte de pollution pour la sélection actuelle.")

overview, sources, observations = st.tabs(["Vue d’ensemble", "Agrégations", "Observations & export"])
with overview:
    section("02", "A YEAR OF AIR. IN ONE VIEW.", f"{len(view)} jours sélectionnés · Pollution PM2.5 et météo à New York")
    if not view.empty:
        trend = px.line(view, x="date", y=["pm25_mean", "trend_7d"],
                        color_discrete_sequence=[LIME, CREAM],
                        labels={"date":"", "value":"PM2.5 · µg/m³", "variable":""})
        for trace in trend.data:
            trace.name = {"pm25_mean":"Moyenne quotidienne", "trend_7d":"Tendance sur 7 jours"}[trace.name]
            trace.line.width = 2
            if trace.name.startswith("Tendance"):
                trace.line.dash = "dot"
        flagged = view.loc[view.anomaly.astype(bool)]
        trend.add_scatter(x=flagged.date, y=flagged.pm25_mean, mode="markers", name="Anomalie",
                          marker=dict(color=CORAL, size=7), hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f} µg/m³<extra>Anomalie</extra>")
        trend.update_layout(hovermode="x unified")
        st.plotly_chart(chart_style(trend, 390), use_container_width=True, theme=None)
        st.caption("Anomalie statistique : moyenne quotidienne supérieure à la moyenne globale + 2 écarts-types. Ce repère est distinct du seuil d’alerte réglable.")
        section("03", "DETECT. UNDERSTAND. ACT.", "Température, distribution et signaux inhabituels.")
        left, right = st.columns(2)
        scatter_view = view.assign(signal=view.anomaly.map({False:"Habituel", True:"Anomalie"}))
        scatter = px.scatter(scatter_view, x="temperature", y="pm25_mean", color="signal",
                             color_discrete_map={"Habituel":LIME, "Anomalie":CORAL},
                             title="Température & pollution", labels={"temperature":"Température · °C", "pm25_mean":"PM2.5 · µg/m³", "signal":""})
        scatter.update_traces(marker=dict(size=7, opacity=.75))
        left.plotly_chart(chart_style(scatter), use_container_width=True, theme=None)
        histogram = px.histogram(view, x="pm25_mean", nbins=30, color_discrete_sequence=[LIME],
                                 title="Distribution du PM2.5", labels={"pm25_mean":"PM2.5 · µg/m³"})
        histogram.update_layout(bargap=.15, yaxis_title="Nombre de jours")
        right.plotly_chart(chart_style(histogram), use_container_width=True, theme=None)

with sources:
    section("04", "EVERY RECORD. CONNECTED.", "Agrégations MongoDB · ensemble des données, indépendamment des filtres.")
    monthly = pd.DataFrame(monthly_aggregation()).rename(columns={"_id":"month"})
    county = pd.DataFrame(county_aggregation()).rename(columns={"_id":"county"})
    left, right = st.columns(2)
    if not monthly.empty:
        fig = px.bar(monthly, x="month", y="pm25", color_discrete_sequence=[LIME], title="Rythme mensuel",
                     labels={"month":"Mois", "pm25":"PM2.5 moyen · µg/m³"})
        fig.update_xaxes(tickmode="array", tickvals=list(range(1,13)), ticktext=["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"])
        left.plotly_chart(chart_style(fig), use_container_width=True, theme=None)
    if not county.empty:
        county["county"] = county["county"].fillna("Non renseigné")
        fig = px.bar(county.sort_values("pm25"), x="pm25", y="county", orientation="h", color_discrete_sequence=[CORAL],
                     title="Les comtés de New York", labels={"county":"", "pm25":"PM2.5 moyen · µg/m³"})
        right.plotly_chart(chart_style(fig), use_container_width=True, theme=None)

with observations:
    section("05", "DATA IN. INSIGHT OUT.", "Ajoutez une observation ou emportez votre sélection.")
    with st.form("add_observation", clear_on_submit=True):
        st.subheader("Ajouter une observation")
        left, right = st.columns(2)
        obs_date = left.date_input("Date", date(2024,1,1))
        site = right.text_input("Identifiant station", max_chars=20)
        pm25 = left.number_input("PM2.5", 0.0, 1000.0, 10.0)
        aqi = right.number_input("AQI", 0, 500, 50)
        submitted = st.form_submit_button("Valider et ajouter")
    if submitted:
        if not site.strip():
            st.error("L'identifiant station est obligatoire.")
        else:
            database.pollution.insert_one({"date":pd.Timestamp(obs_date).to_pydatetime(),"site_id":site.strip(),"pm25":pm25,"aqi":aqi,"source":"formulaire"})
            st.success("Observation validée et ajoutée à MongoDB.")
    st.caption("L’ajout est enregistré dans pollution sans recalculer les analyses quotidiennes. Attention : l’ETL reconstruit les collections depuis les fichiers sources et remplace les ajouts manuels.")
    st.download_button("Exporter la sélection CSV ↗", view.to_csv(index=False).encode(), "analyse_nyc_2024.csv", "text/csv")
    st.dataframe(view, use_container_width=True, hide_index=True)

st.markdown('<div class="footer"><span>NYC AIR INTELLIGENCE / YASSIN DHIBI</span><span>PYTHON · MONGODB · STREAMLIT</span><span>DATA IN MOTION. INSIGHT IN FOCUS.</span></div>', unsafe_allow_html=True)

