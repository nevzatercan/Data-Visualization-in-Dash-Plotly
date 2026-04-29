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

        bbox = hoverData["points"][0].get("bbox") or {}
        has_data = any(t.get("type") == "barpolar" for t in fig_dict.get("data", []))

        # bbox, Choroplethmap hover olayından gelir; eksikse ekrana sabitlenir.
        top = f"{bbox['y1'] + 10}px" if "y1" in bbox else "80px"
        left = f"{bbox['x1'] + 10}px" if "x1" in bbox else "auto"
        right = "20px" if "x1" not in bbox else "auto"

        base = {
            "position": "fixed",
            "top": top,
            "left": left,
            "right": right,
            "padding": "10px",
            "display": "block",
            "z-index": 9999,
        }
        style = (
            {**base,
             "background": "rgba(10, 18, 36, 0.90)",
             "backdrop-filter": "blur(28px) saturate(1.6)",
             "-webkit-backdrop-filter": "blur(28px) saturate(1.6)",
             "border": "1px solid rgba(56, 130, 246, 0.18)",
             "border-radius": "14px",
             "box-shadow": "0 8px 32px rgba(0,0,0,0.50)",
             "width": "20%", "height": "250px"}
            if has_data
            else {**base,
                  "background": "rgba(10, 18, 36, 0.88)",
                  "border": "1px solid rgba(56, 130, 246, 0.18)",
                  "border-radius": "14px"}
        )
        return style, fig_dict, {"last_iso3": location}
