"""dashapp — DSÖ ölüm + PM2.5 + COVID görselleştirme paneli.

``create_app()`` Dash uygulamasını oluşturup döndürür.
"""
from __future__ import annotations

import os
import dash
import dash_mantine_components as dmc
from dash import dcc, html

# src/dashapp/__init__.py → ../../assets = proje kökü/assets
_ASSETS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "assets")
)

from dashapp.callbacks import register_callbacks
from dashapp.layout.controls import make_toolbar
from dashapp.layout.info_modals import make_info_modal1, make_info_modal2
from dashapp.layout.panels import make_chart_panel, make_hover_panel, make_side_panel
from dashapp.layout.stores import make_stores
from dashapp.theme import GRAPH_CONFIG

# scrollZoom devre dışı — harita yanlışlıkla zoom'lanmasın
_HARITA_CONFIG: dict = {**GRAPH_CONFIG, "scrollZoom": False}


def create_app() -> dash.Dash:
    """Dash uygulamasını oluştur, layout'u kur, callback'leri kaydet ve döndür."""
    app = dash.Dash(__name__, assets_folder=_ASSETS_FOLDER)
    app.config.suppress_callback_exceptions = True

    app.layout = dmc.MantineProvider(
        html.Div(
            [
                *make_stores(),
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content"),
                html.Div(id="dummy-input", style={"display": "none"}),

                # ── Tam viewport harita (z-index 0, en altta) ────────────────
                html.Div(
                    dcc.Graph(
                        id="Harita",
                        figure={},
                        config=_HARITA_CONFIG,
                        clear_on_unhover=True,
                        style={"width": "100%", "height": "100%"},
                    ),
                    style={
                        "position": "fixed",
                        "top": 0,
                        "left": 0,
                        "width": "100vw",
                        "height": "100vh",
                        "zIndex": 0,
                        "overflow": "hidden",
                    },
                ),

                # ── Floating toolbar (z-index 9999) ──────────────────────────
                make_toolbar(),

                # ── Paneller ve modallar ──────────────────────────────────────
                make_side_panel(),
                make_chart_panel(),
                make_hover_panel(),
                make_info_modal1(),
                make_info_modal2(),
            ],
            style={"position": "relative", "width": "100vw", "height": "100vh"},
        ),
        defaultColorScheme="dark",
    )

    register_callbacks(app)
    return app
