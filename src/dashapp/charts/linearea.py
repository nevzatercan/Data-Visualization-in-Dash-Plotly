"""Bölgelere göre PM2.5 trendi alan grafiği (line area)."""

from __future__ import annotations

import plotly.express as px

from dashapp.data_loader import load_air
from dashapp.theme import CHART_MARGIN, TRANSPARENT_LAYOUT

_COLOR_PALETTE = {
    "Afrika":          "rgba(251, 113, 133, 0.85)",   # rose-400
    "Güney Doğu Asya": "rgba( 56, 189, 248, 0.85)",   # sky-400
    "Avrupa":          "rgba( 52, 211, 153, 0.85)",   # emerald-400
    "Amerika":         "rgba(251, 191,  36, 0.85)",   # amber-400
    "Ortadoğu":        "rgba(167, 139, 250, 0.85)",   # violet-400
    "Batı Pasifik":    "rgba( 45, 212, 191, 0.85)",   # teal-400
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
        legend=dict(font=dict(size=10), orientation="v", title_text=""),
        xaxis_tickangle=45,
        xaxis_title="Yıl",
        yaxis_title="PM2.5 Seviyesi",
        margin=CHART_MARGIN,
    )
    return fig.to_dict()
