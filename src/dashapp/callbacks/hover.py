"""Hover callback'i — fare harita üzerindeyken radar grafiği gösterilir."""
from __future__ import annotations

import dash
from dash import Input, Output, State

import dashapp.charts.radar as _radar_chart
from dashapp.layout.stores import parse_viewport


def register(app: dash.Dash) -> None:

    @app.callback(
        [Output("hovered_location", "style"),
         Output("gül", "figure"),
         Output("hover-store", "data")],
        [Input("Harita", "hoverData"),
         Input("secilenyıl", "value")],
        [State("viewport-store", "data"),
         State("hover-store", "data")],
    )
    def display_hover_data(hoverData, option_slctd, vp, hover_data):
        width, height = parse_viewport(vp)
        last_iso3 = (hover_data or {}).get("last_iso3", "")

        if hoverData is None:
            return {"display": "none"}, {"data": []}, {"last_iso3": ""}

        # Choroplethmap hover olayı "location" anahtarı taşır.
        # Scattermap (lat/lon tabanlı) "skip" ile bastırıldı ama ekstra guard.
        location = hoverData["points"][0].get("location")
        if not location:
            return dash.no_update, dash.no_update, dash.no_update

        if location == last_iso3:
            return dash.no_update, dash.no_update, dash.no_update

        fig_dict = _radar_chart.figure(location, option_slctd, width=width, height=height)
        if fig_dict is None:
            return {"display": "none"}, {"data": []}, {"last_iso3": ""}

        # radar.py ürettiği grafik boyutları (figure() içindeki formülle eşleşmeli)
        chart_w = int(width * 0.25)
        chart_h = int(height * 0.33)

        bbox = hoverData["points"][0].get("bbox") or {}
        has_data = any(t.get("type") == "barpolar" for t in fig_dict.get("data", []))

        # Tooltip konumu — bbox yoksa ekranın sağ üstüne sabitle
        if "x1" in bbox:
            left_px = int(bbox["x1"]) + 10
            # Ekran sağından taşmasın
            left_px = min(left_px, int(width) - chart_w - 16)
            left_str, right_str = f"{left_px}px", "auto"
        else:
            left_str, right_str = "auto", "20px"

        if "y1" in bbox:
            top_px = int(bbox["y1"]) + 10
            # Ekran altından taşmasın
            top_px = min(top_px, int(height) - chart_h - 16)
            top_str = f"{top_px}px"
        else:
            top_str = "80px"

        base = {
            "position": "fixed",
            "top": top_str,
            "left": left_str,
            "right": right_str,
            "display": "block",
            "padding": "0",          # padding yok — grafik tam doldurur
            "overflow": "hidden",    # taşmayı kes
            "z-index": 9999,
            "border-radius": "14px",
            "width": f"{chart_w}px",
            "height": f"{chart_h}px",
        }
        style = {
            **base,
            "background": "rgba(10, 18, 36, 0.92)",
            "backdrop-filter": "blur(28px) saturate(1.6)",
            "-webkit-backdrop-filter": "blur(28px) saturate(1.6)",
            "border": "1px solid rgba(56, 130, 246, 0.20)",
            "box-shadow": "0 8px 32px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.30) inset",
        }
        return style, fig_dict, {"last_iso3": location}
