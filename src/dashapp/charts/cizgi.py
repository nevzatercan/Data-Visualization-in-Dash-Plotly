"""PM2.5 ve ölüm oranını zaman içinde gösteren animasyonlu çizgi grafik."""

from __future__ import annotations

import plotly.graph_objects as go

from dashapp.data_loader import load_merged
from dashapp.theme import AXIS_STYLE, TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total


def figure(
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
    country_name: str = "",
) -> dict:
    """2010 sonrası PM2.5 seviyesi ve ölüm oranı animasyonlu çizgi grafiği.

    Parameters
    ----------
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları.
    country_name:
        Başlıkta gösterilecek Türkçe ülke adı.
    """
    merged = load_merged()
    df = filter_total(merged, country=iso)
    df = df[df["Year"] >= 2010].sort_values("Year")

    deaths_by_year = df.set_index("Year")["NormalizationForPerDeath"].to_dict()
    air_by_year = df.set_index("Year")["NormalizationForFactValueNumeric"].to_dict()

    years, deaths, air_quality = [], [], []
    for year in range(2010, 2020):
        if year not in deaths_by_year:
            continue
        years.append(year)
        deaths.append(deaths_by_year[year])
        air_quality.append(air_by_year[year])

    if not years:
        return go.Figure().to_dict()

    display_name = country_name or iso

    fig = go.Figure(
        frames=[
            go.Frame(data=[
                go.Scatter(x=years[:i + 1], y=deaths[:i + 1], mode="lines+markers", name="Ölüm Sayıları"),
                go.Scatter(x=years[:i + 1], y=air_quality[:i + 1], mode="lines+markers", name="PM2.5 seviyesi"),
            ])
            for i in range(len(years))
        ]
    )
    fig.add_trace(go.Scatter(x=[years[0]], y=[deaths[0]], mode="lines+markers", name="Ölüm Oranı"))
    fig.add_trace(go.Scatter(x=[years[0]], y=[air_quality[0]], mode="lines+markers", name="PM2.5 seviyesi"))

    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        xaxis={**AXIS_STYLE, "title": f"{display_name} için 2010 sonrası PM2.5 seviyesi ve ölüm oranı", "tickangle": -45},
        yaxis={**AXIS_STYLE, "title": "Normalize edilmiş veri"},
        showlegend=True,
        width=width * 0.35,
        height=height * 0.24,
        margin=dict(l=0, r=0, t=0, b=10),
        updatemenus=[{
            "buttons": [{"args": [None], "label": "Play", "method": "animate"}],
            "direction": "left",
            "pad": {"r": 0, "t": 0},
            "showactive": False,
            "bordercolor": "rgba(255,255,255,0.20)",
            "bgcolor": "rgba(13,17,30,0.72)",
            "font": {"color": "rgba(255,255,255,0.85)"},
            "type": "buttons",
            "x": 1.35, "xanchor": "right",
            "y": 0.6, "yanchor": "top",
        }],
    )
    return fig.to_dict()
