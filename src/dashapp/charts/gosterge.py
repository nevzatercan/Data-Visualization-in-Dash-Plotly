"""PM2.5 seviyesi gösterge (gauge) grafiği."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from dashapp.data_loader import load_merged
from dashapp.transforms import filter_total, safe_first


def figure(
    year: int,
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
) -> dict:
    """Yarım daire PM2.5 seviyesi göstergesi.

    0-70 μg/m³ aralığında 4 kadran: Düşük / Orta / Yüksek / Çok yüksek.

    Parameters
    ----------
    year:
        Seçili yıl.
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları.
    """
    merged = load_merged()
    fact_values = filter_total(merged, year=year, country=iso)["FactValueNumeric"]

    plot_bgcolor = "rgba(0,0,0,0)"
    quadrant_colors = [plot_bgcolor, "#d3382e", "#f2a529", "#eff229", "#85e043"]
    quadrant_text = ["", "<b>Çok yüksek</b>", "<b>Yüksek</b>", "<b>Orta</b>", "<b>Düşük</b>"]
    n_quadrants = len(quadrant_colors) - 1

    current_value = safe_first(fact_values, default=0)
    min_value, max_value = 0, 70
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (
        1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value)
    )

    fig = go.Figure(
        data=[go.Pie(
            values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
            rotation=90,
            hole=0.5,
            marker_colors=quadrant_colors,
            text=quadrant_text,
            textfont=dict(size=7, color="black"),
            textinfo="text",
            hoverinfo="skip",
        )],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=0, l=0, r=30),
            width=width * 0.2,
            height=height * 0.2,
            paper_bgcolor=plot_bgcolor,
            annotations=[go.layout.Annotation(
                text=f"<b>pm2.5 seviyesi</b><br>{current_value}",
                x=0.5, xanchor="center", xref="paper",
                y=0.25, yanchor="bottom", yref="paper",
                showarrow=False,
            )],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52, y0=0.48, y1=0.52,
                    fillcolor="#333", line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle) * 0.6,
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4),
                ),
            ],
        ),
    )
    return fig.to_dict()
