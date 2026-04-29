"""3 metrikli kursun (bullet) gösterge grafiği."""

from __future__ import annotations

import plotly.graph_objects as go

from dashapp.data_loader import load_merged
from dashapp.theme import TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total, safe_first


def figure(
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
) -> dict:
    """PM2.5, 100k başına ölüm oranı ve yüzdelik ölüm bullet grafiği.

    Parameters
    ----------
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları.
    """
    merged = load_merged()
    df = filter_total(merged, country=iso)
    if df.empty:
        return go.Figure().to_dict()

    max_year = int(df["Year"].max())
    max_yeareksi = max(max_year - 1, df["Year"].min())

    in_range = df[df["Year"] >= 2010]
    mean_fact = in_range["FactValueNumeric"].mean()
    mean_perc = in_range["Percentage of cause-specific deaths out of total deaths"].mean()
    mean_pop = in_range[in_range["Year"] <= max_year]["Death rate per 100 000 population"].mean()

    rows = {
        yr: df[df["Year"] == yr]
        for yr in (max_year, max_yeareksi)
    }

    def val(year: int, col: str) -> float:
        return safe_first(rows[year][col], default=0)

    fig = go.Figure()

    # PM2.5
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        number={"suffix": "μm"},
        value=val(max_year, "FactValueNumeric"),
        delta={"reference": val(max_yeareksi, "FactValueNumeric"),
               "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
        domain={"x": [0.25, 1], "y": [0.13, 0.3]},
        gauge={
            "shape": "bullet",
            "axis": {"tickangle": 0, "tickwidth": 0.2, "tickfont": dict(size=8, color="rgba(255,255,255,0.50)"), "range": [0, 65]},
            "threshold": {"line": {"color": "blue", "width": 1}, "thickness": 0.5, "value": mean_fact},
            "steps": [
                {"range": [0, 20], "color": "#9ade5d"},
                {"range": [20, 35], "color": "#f0f259"},
                {"range": [35, 50], "color": "#e7a847"},
                {"range": [50, 65], "color": "#d3382e"},
            ],
            "bar": {"color": "rgba(255,255,255,0.70)", "thickness": 0.1},
        },
    ))

    # 100k başına ölüm
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        number={"font": dict(size=14)},
        value=val(max_year, "Death rate per 100 000 population"),
        delta={"reference": val(max_yeareksi, "Death rate per 100 000 population"),
               "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
        domain={"x": [0.25, 1], "y": [0.43, 0.6]},
        gauge={
            "shape": "bullet",
            "axis": {"tickangle": 0, "tickwidth": 0.2, "tickfont": dict(size=8, color="rgba(255,255,255,0.50)"), "range": [0, 120]},
            "threshold": {"line": {"color": "blue", "width": 1}, "thickness": 0.5, "value": mean_pop},
            "steps": [
                {"range": [0, 30], "color": "#9ade5d"},
                {"range": [30, 60], "color": "#f0f259"},
                {"range": [60, 90], "color": "#e7a847"},
                {"range": [90, 120], "color": "#d3382e"},
            ],
            "bar": {"color": "rgba(255,255,255,0.70)", "thickness": 0.1},
        },
    ))

    # Yüzdelik ölüm
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=val(max_year, "Percentage of cause-specific deaths out of total deaths"),
        number={"prefix": "%"},
        delta={"reference": val(max_yeareksi, "Percentage of cause-specific deaths out of total deaths"),
               "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
        domain={"x": [0.25, 1], "y": [0.73, 0.9]},
        gauge={
            "shape": "bullet",
            "axis": {"tickangle": 0, "tickwidth": 0.2, "tickfont": dict(size=8, color="rgba(255,255,255,0.50)"), "range": [0, 12]},
            "threshold": {"line": {"color": "blue", "width": 1}, "thickness": 0.5, "value": mean_perc},
            "steps": [
                {"range": [0, 3], "color": "#9ade5d"},
                {"range": [3, 6], "color": "#f0f259"},
                {"range": [6, 9], "color": "#e7a847"},
                {"range": [9, 12], "color": "#d3382e"},
            ],
            "bar": {"color": "rgba(255,255,255,0.70)", "thickness": 0.1},
        },
    ))

    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        width=width * 0.17,
        height=height * 0.24,
        annotations=[
            dict(text="<span style='font-size:8;color:rgba(255,255,255,0.75)'><b>SYH'a bağlı<br>Yüzdelik<br>Ölüm</b></span>", x=0.03, y=0.9, showarrow=False, xref="paper", yref="paper"),
            dict(text="<span style='font-size:8;color:rgba(255,255,255,0.75)'><b>100 000<br>kişide<br>ölüm</b></span>", x=0.07, y=0.5, showarrow=False, xref="paper", yref="paper"),
            dict(text="<span style='font-size:8;color:rgba(255,255,255,0.75)'><b>pm2.5<br>Seviyesi</b></span>", x=0.06, y=0.15, showarrow=False, xref="paper", yref="paper"),
        ],
    )
    return fig.to_dict()
