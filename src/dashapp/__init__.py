"""dashapp — DSÖ ölüm + PM2.5 + COVID görselleştirme paneli.

``create_app()`` Dash uygulamasını oluşturup döndürür.
"""
from __future__ import annotations

import dash
import dash_mantine_components as dmc
from dash import dcc, html

from dashapp.callbacks import register_callbacks
from dashapp.layout.controls import make_toolbar
from dashapp.layout.info_modals import make_info_modal1, make_info_modal2
from dashapp.layout.panels import make_chart_panel, make_hover_panel, make_side_panel
from dashapp.layout.stores import make_stores
from dashapp.theme import GRAPH_CONFIG


def create_app() -> dash.Dash:
    """Dash uygulamasını oluştur, layout'u kur, callback'leri kaydet ve döndür."""
    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True

    app.layout = dmc.MantineProvider(
        html.Div([
            *make_stores(),
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
            html.Div(id="dummy-input", style={"display": "none"}),

            make_toolbar(),

            html.Div(
                dcc.Graph(
                    id="Harita",
                    figure={},
                    config={**GRAPH_CONFIG, "scrollZoom": False},
                    clear_on_unhover=True,
                ),
                style={
                    "position": "absolute",
                    "top": "0px !important",
                    "left": "0px !important",
                    "overflow-y": "hidden",
                    "margin-top": "-4.6%",
                },
            ),

            make_side_panel(),
            make_chart_panel(),
            make_hover_panel(),
            make_info_modal1(),
            make_info_modal2(),
        ])
    )

    register_callbacks(app)
    return app
