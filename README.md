# NYC Air Intelligence

Projet de 3ème LIG-BI conforme au brief **Analyse intelligente de données** : collecte multi-source, ETL modulaire, MongoDB, analyse Pandas et dashboard Streamlit.

## Architecture

`CSV pollution + JSON météo + XLSX stations → validation et nettoyage Pandas → MongoDB → agrégations → dashboard Streamlit`

Collections : `pollution`, `weather`, `daily_analysis`. Les fichiers bruts restent dans `data/raw/`; les sorties nettoyées sont écrites dans `data/processed/`.

## Lancement

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d
python scripts/run_etl.py
streamlit run app.py
```

Le dashboard contient 4 KPI, 5 graphiques, des filtres temporels et PM2.5, deux agrégations MongoDB, un formulaire validé, une détection d'anomalies et un export CSV.

## Conformité au cahier des charges

| Exigence | Réalisation |
|---|---|
| Plus de 2 types de fichiers | 3 formats réellement lus par l'ETL : `pollution_nyc_2024.csv`, `weather_nyc_2024.json` et `stations_nyc.xlsx` |
| ETL modulaire | `src/extract.py`, `src/transform.py`, `scripts/run_etl.py` |
| MongoDB | 3 collections, insertion, requêtes, index et 2 agrégations |
| Pandas | conversion, `dropna`, dédoublonnage, filtrage, `groupby`, fusion et statistiques |
| 3 KPI minimum | 4 KPI : moyenne, pic, AQI moyen et anomalies |
| 3 graphiques minimum | 5 graphiques Plotly |
| Interface | filtres, formulaire validé et export CSV Streamlit |
| Anomalie/tendance | seuil statistique moyenne + 2 écarts-types et moyenne mobile 7 jours |
| Bonus | alerte automatique configurable lorsqu'un seuil PM2.5 est dépassé |

## Données

- Pollution : mesures AQS quotidiennes de New York pour 2024.
- Météo : réponse Open-Meteo Archive API conservée en JSON, coordonnées de New York, année 2024.
- Stations : référentiel Excel distinct avec identifiant, latitude, longitude, nom et comté ; il enrichit les mesures de pollution pendant l'ETL.

## Tests

```powershell
pytest -q
```
