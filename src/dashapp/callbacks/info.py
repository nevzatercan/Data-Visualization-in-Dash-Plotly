"""Bilgi modali callback'i — info_circle1/2 açar, kapat butonları kapatır."""
from __future__ import annotations

import dash
from dash import Input, Output, State

import dashapp.charts.linearea as _linearea_chart
import dashapp.charts.sunburst as _sunburst_chart
from dashapp.layout.stores import parse_viewport


def register(app: dash.Dash) -> None:

    @app.callback(
        [Output("modal-info1", "opened"),
         Output("BolgeHaritasi", "src"),
         Output("sunburst", "figure"),
         Output("linearea", "figure"),
         Output("modal-info2", "opened")],
        [Input("closeButton2", "n_clicks"),
         Input("closeButton3", "n_clicks"),
         Input("info_circle1", "n_clicks"),
         Input("info_circle2", "n_clicks")],
        [State("viewport-store", "data")],
        prevent_initial_call=True,
    )
    def toggle_info_div(_c2, _c3, _i1, _i2, vp):
        width, height = parse_viewport(vp)
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        prop_id = ctx.triggered[0]["prop_id"]
        _closed = (False, "", {"data": []}, {"data": []}, False)

        if prop_id in ("closeButton2.n_clicks", "closeButton3.n_clicks"):
            return _closed
        if prop_id == "info_circle1.n_clicks":
            return (
                True,
                "assets/img/maps.png",
                _sunburst_chart.figure(width=width, height=height),
                _linearea_chart.figure(width=width, height=height),
                False,
            )
        if prop_id == "info_circle2.n_clicks":
            return False, "", {"data": []}, {"data": []}, True
        raise dash.exceptions.PreventUpdate
