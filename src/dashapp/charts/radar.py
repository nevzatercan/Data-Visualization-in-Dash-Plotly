"""Ülke vs dünya ortalaması polar radar grafiği (hover üzerinde)."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from dashapp.data_loader import load_merged, world_radar_means
from dashapp.transforms import filter_total, safe_first

_CATEGORIES = [
    "Ölüm Sayısı",
    "Yüzdelik <br> Ölüm Oranı",
    "Yaşa Standardize <br> Edilmiş Oran",
    "Max pm2.5 <br> seviyesi",
    "Min pm2.5  <br> seviyesi",
]


def _sad_face(width: float, height: float) -> dict:
    """Yetersiz veri durumunda gösterilen ağlayan yüz figürü."""
    theta = np.linspace(0, 2 * np.pi, 100)
    mouth_x = np.linspace(-0.3, 0.3, 100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=0.5 * np.cos(theta), y=0.5 * np.sin(theta), mode="lines", line=dict(color="rgba(255,255,255,0.70)")))
    fig.add_trace(go.Scatter(x=[0.3, -0.3], y=[0.3, 0.3], mode="markers", marker=dict(color="rgba(255,255,255,0.85)", size=10)))
    fig.add_trace(go.Scatter(x=mouth_x, y=0.1 * np.cos(mouth_x * 5), mode="lines", line=dict(color="rgba(255,255,255,0.70)")))
    fig.update_layout(
        title="Ne yazık ki bu ülkenin yeterli verileri paylaşılmadı.",
        title_font=dict(color="rgba(255,255,255,0.80)", size=11),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.82)"),
    )
    return fig.to_dict()


def figure(
    iso: str,
    year: int,
    *,
    width: float = 1280,
    height: float = 800,
) -> dict | None:
    """Ülke vs dünya ortalaması polar radar grafiği.

    Returns
    -------
    dict
        Grafik figürü ``to_dict()`` çıktısı.
    None
        ``iso`` boş string (hover yok) — callback'de ``{'data': []}`` kullanılır.
    """
    if not iso:
        return None

    merged = load_merged()
    radar_world = world_radar_means()

    df = filter_total(merged, year=year, country=iso)
    if df.empty:
        return _sad_face(width, height)

    country_vals = np.array([
        safe_first(df["NormalizationForNumber"], default=0) * 10,
        safe_first(df["NormalizationForPerDeath"], default=0),
        safe_first(df["NormalizationForAgeStandardizedDeathRate"], default=0),
        safe_first(df["NormalizationForFactValueNumericLow"], default=0),
        safe_first(df["NormalizationForFactValueNumericHigh"], default=0),
    ])

    if country_vals[0] == 0:
        return _sad_face(width, height)

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=radar_world.tolist(), theta=_CATEGORIES, name="Dünya Ortalaması",
        marker_color=["rgba(251,191,36,0.75)"] * 6,
        marker_line_color="rgba(255,255,255,0.10)",
        marker_line_width=0.5, opacity=0.80, width=0.97, base=0, thetaunit="radians",
    ))
    fig.add_trace(go.Barpolar(
        r=country_vals.tolist(), theta=_CATEGORIES, name="Seçilen Ülke Ortalaması",
        marker_color=["rgba(56,189,248,0.80)"] * 6,
        marker_line_color="rgba(255,255,255,0.10)",
        marker_line_width=0.5, opacity=0.80, width=0.97, base=0, thetaunit="radians",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(showline=False, showticklabels=False, linewidth=2, gridcolor="rgba(255,255,255,0.08)", gridwidth=1),
            angularaxis=dict(
                tickfont=dict(size=10, color="rgba(255,255,255,0.60)"),
                linewidth=1, linecolor="rgba(255,255,255,0.15)",
                showline=False, showticklabels=True, rotation=90,
            ),
        ),
        showlegend=True,
        legend=dict(orientation="h", font=dict(color="rgba(255,255,255,0.75)", size=10)),
        title="Dünya ve Ülke Ortalaması Radar Grafiği",
        title_font=dict(size=12, color="rgba(255,255,255,0.85)"),
        margin=dict(l=25, r=25, t=50, b=25),
        polar_bgcolor="rgba(255,255,255,0.04)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.82)"),
        width=width * 0.25,
        height=height * 0.33,
    )
    return fig.to_dict()
