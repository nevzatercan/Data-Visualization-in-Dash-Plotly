"""Bölgelere göre PM2.5 trendi alan grafiği (line area)."""

from __future__ import annotations

import plotly.express as px

from dashapp.data_loader import load_air
from dashapp.theme import TRANSPARENT_LAYOUT

_COLOR_PALETTE = {
    "Afrika": "#5E1675",
    "Güney Doğu Asya": "#39A7FF",
    "Avrupa": "#337357",
    "Amerika": "#FFD23F",
    "Ortadoğu": "#211951",
    "Batı Pasifik": "#FF4B91",
}


def figure(
    *,
    width: float = 1280,
    height: float = 800,
) -> dict:
    """Bölgesel PM2.5 ortalaması yıllık alan grafiği.

    ParentLocation sütunu `load_air()` içinde zaten Türkçeye çevrilmiş;
    tekrar eşleme yapılmaz.
    """
    df = load_air()
    region_mean = (
        df.groupby(["ParentLocation", "Period"], observed=True)
        .mean(numeric_only=True)
        .reset_index()
    )

    fig = px.area(
        region_mean,
        x="Period",
        y="FactValueNumericHigh",
        color="ParentLocation",
        line_group="ParentLocation",
        color_discrete_map=_COLOR_PALETTE,
        labels={"ParentLocation": "Bölgeler"},
        custom_data=["Period", "FactValueNumericHigh"],
    )
    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        width=width * 0.315,
        height=height * 0.4,
        legend=dict(font=dict(size=8)),
        xaxis_tickangle=45,
        xaxis_title="Yıl",
        yaxis_title="PM2.5 Seviyesi",
    )
    return fig.to_dict()
