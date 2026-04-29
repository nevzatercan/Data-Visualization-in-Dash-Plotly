"""Kümülatif solunum yolu ölümleri vs COVID-19 kümülatif ölüm grafiği."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from dashapp.data_loader import load_covid, load_merged
from dashapp.theme import AXIS_STYLE, TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total, safe_first


def figure(
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
    country_name_english: str = "",
) -> dict:
    """Kümülatif solunum yolu ölümleri vs COVID kümülatif ölüm alan grafiği.

    Parameters
    ----------
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları.
    country_name_english:
        COVID veri setindeki İngilizce ülke adı.
    """
    merged = load_merged()
    covid = load_covid()

    df = filter_total(merged, country=iso)
    df = df[df["Year"] >= 2010].sort_values("Year")
    if df.empty:
        return go.Figure().to_dict()

    df = df.copy()
    df["Cumulative Deaths"] = df["Number"].cumsum()

    country_numbers = covid[covid["Name"] == country_name_english]["Deaths - cumulative total"]
    country_numbers = country_numbers.astype(int)
    if country_numbers.empty:
        country_numbers = pd.concat([pd.Series([0]), country_numbers], ignore_index=True)
    covid_total = safe_first(country_numbers, default=0)

    cum_by_year = df.set_index("Year")["Cumulative Deaths"].to_dict()
    first_matching_year = None
    for year in range(2010, 2020):
        cum = cum_by_year.get(year)
        if cum is None:
            continue
        if cum > covid_total:
            first_matching_year = year - 2010
            break

    if first_matching_year is None:
        title = "Toplam Covid ölümüne yetişemedi."
    elif first_matching_year == 0:
        title = "Toplam Covid ölümüne 1 yılda yetişti."
    else:
        title = f"Toplam Covid ölümüne {first_matching_year} yılda yetişti."

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Cumulative Deaths"],
        fill="tozeroy", mode="lines",
        fillcolor="blue", line=dict(color="blue"),
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"], y=[covid_total] * len(df),
        mode="lines", fill="tozeroy",
        fillcolor="rgba(255,0,0,0.7)",
        line=dict(color="rgba(255,0,0,0.7)", width=0),
        showlegend=False,
    ))

    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        title_text=title,
        xaxis={**AXIS_STYLE, "title": "Yıl", "tickangle": -45, "range": [df["Year"].min(), df["Year"].max()]},
        yaxis={**AXIS_STYLE, "title": "Kümülatif Ölüm Sayısı"},
        showlegend=False,
        width=width * 0.35,
        height=height * 0.24,
        margin=dict(l=0, r=15, t=25, b=10),
        annotations=[dict(
            text="Covid 19 Kümülatif Ölüm Sayısı",
            x=df["Year"].median(),
            y=float(country_numbers.median()) * 0.3 if not country_numbers.empty else 0,
            xanchor="center", yanchor="bottom",
            showarrow=False,
            font=dict(color="black", size=14),
        )],
    )
    return fig.to_dict()
