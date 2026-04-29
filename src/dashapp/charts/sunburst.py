"""Bölgelere göre PM2.5 dağılımı sunburst grafiği."""

from __future__ import annotations

import numpy as np
import plotly.express as px

from dashapp.data_loader import load_air
from dashapp.theme import TRANSPARENT_LAYOUT


def figure(
    *,
    width: float = 1280,
    height: float = 800,
) -> dict:
    """Bölge → Ülke PM2.5 seviyesi sunburst grafiği.

    ParentLocation sütunu `load_air()` içinde zaten Türkçeye çevrilmiş.
    """
    df = load_air()

    new_color_scale = [
        (0.0, "#b3eb73"),
        (0.5, "#fbed71"),
        (0.55, "#efb35d"),
        (1.0, "#e86c75"),
    ]

    fig = px.sunburst(
        df,
        path=["ParentLocation", "Location"],
        values="NormalizationForFactValueNumeric",
        color="NormalizationForFactValueNumeric",
        color_continuous_scale=new_color_scale,
        color_continuous_midpoint=np.average(
            df["NormalizationForFactValueNumeric"],
            weights=df["NormalizationForFactValueNumeric"],
        ),
    )
    fig.update_traces(hovertemplate="", hoverinfo="none")
    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        margin=dict(l=0, r=0, t=30, b=30),
        coloraxis_showscale=False,
        showlegend=False,
        width=width * 0.315,
        height=height * 0.4,
    )
    return fig.to_dict()
