"""Visual identity shared with the NYC Air Intelligence motion reel."""
from base64 import b64encode
from functools import lru_cache
from html import escape
from math import cos, sin, pi
from pathlib import Path

import streamlit as st

INK, CREAM, LIME, CORAL = '#111615', '#F0F0E6', '#D5FF53', '#FF755A'
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def stylesheet():
    font = b64encode((ROOT / 'assets/fonts/SpaceGrotesk.ttf').read_bytes()).decode()
    css = (ROOT / 'assets/dashboard.css').read_text(encoding='utf-8')
    return f'<style>@font-face{{font-family:SpaceGrotesk;src:url(data:font/ttf;base64,{font}) format("truetype");font-weight:300 700;font-display:swap;}}{css}</style>'


@lru_cache(maxsize=1)
def wireform():
    paths = []
    for j in range(36):
        v = j / 36 * 2 * pi
        points = []
        for i in range(81):
            u = i / 80 * 2 * pi
            x, y, z = (128 + 38*cos(v))*cos(u), (128 + 38*cos(v))*sin(u), 38*sin(v)
            x, z = x*cos(.8) + z*sin(.8), -x*sin(.8) + z*cos(.8)
            y, z = y*cos(.9) + z*sin(.9), -y*sin(.9) + z*cos(.9)
            scale = 700 / (700-z)
            points.append(f'{"M" if i == 0 else "L"}{220+x*scale:.1f},{210+y*scale:.1f}')
        color = CREAM if j % 7 == 0 else LIME
        paths.append(f'<path d="{" ".join(points)}" stroke="{color}" opacity="{.8 if j%7==0 else .4}"/>')
    return '<svg viewBox="0 0 440 440" fill="none" aria-hidden="true"><circle cx="220" cy="210" r="196" stroke="#F0F0E6" opacity=".15" stroke-dasharray="2 10"/><g class="wireform">' + ''.join(paths) + '</g></svg>'


def brand_header():
    st.markdown(stylesheet(), unsafe_allow_html=True)
    st.markdown(f'''<div class="masthead"><span><i></i> NYC / AIR INTELLIGENCE</span><span>NEW YORK CITY · 2024</span></div>
<section class="hero"><div class="hero-copy"><div class="eyebrow">01 — THE INVISIBLE CITY</div>
<h1>MAKE THE<br>INVISIBLE <em>VISIBLE.</em></h1><p>La qualité de l’air, sous un nouveau regard.<br>Explorez une année de pollution et de météo à New York.</p>
<div class="hero-tags"><span>PM2.5</span><span>MÉTÉO</span><span>DATA INTELLIGENCE</span></div></div>
<div class="hero-art">{wireform()}<div class="coordinates">40.7128° N / 74.0060° W</div></div></section>''', unsafe_allow_html=True)


def section(number, title, subtitle):
    st.markdown(f'<div class="section-title"><span>{escape(number)}</span><div><h2>{escape(title)}</h2><p>{escape(subtitle)}</p></div></div>', unsafe_allow_html=True)


def metric_cards(view):
    values = [('PM2.5 MOYEN', f'{view.pm25_mean.mean():.1f}' if len(view) else '—', 'µg/m³ · moyenne quotidienne', 'cream'),
              ('PIC PM2.5', f'{view.pm25_max.max():.1f}' if len(view) else '—', 'µg/m³ · observation maximale', 'lime'),
              ('AQI MOYEN', f'{view.aqi_mean.mean():.0f}' if len(view) else '—', 'indice de qualité de l’air', 'cream'),
              ('ANOMALIES', str(int(view.anomaly.sum())), 'jours statistiquement inhabituels', 'coral')]
    cards = ''.join(f'<div class="stat-card {color}"><div class="eyebrow">{title}</div><strong>{value}</strong><small>{detail}</small></div>' for title, value, detail, color in values)
    st.markdown(f'<div class="stats">{cards}</div>', unsafe_allow_html=True)


def chart_style(fig, height=340):
    fig.update_layout(template='plotly_dark', paper_bgcolor=INK, plot_bgcolor=INK,
                      font=dict(family='SpaceGrotesk, Arial, sans-serif', color=CREAM, size=12),
                      colorway=[LIME, CORAL, CREAM], height=height,
                      margin=dict(l=12, r=20, t=55, b=20),
                      title=dict(font=dict(size=19)),
                      legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02, x=0),
                      hoverlabel=dict(bgcolor='#1B2320', font_color=CREAM),
                      modebar=dict(bgcolor=INK, color='#9EA99D', activecolor=LIME))
    fig.update_xaxes(gridcolor='rgba(240,240,230,.07)', zeroline=False, title_font_size=12)
    fig.update_yaxes(gridcolor='rgba(240,240,230,.09)', zeroline=False, title_font_size=12)
    return fig
