"""Viewport clientside callback'i — tarayıcı boyutunu viewport-store'a yazar."""
from __future__ import annotations

import dash
from dash import ClientsideFunction, Input, Output


def register(app: dash.Dash) -> None:
    app.clientside_callback(
        ClientsideFunction(namespace="viewport", function_name="updateViewport"),
        Output("viewport-store", "data"),
        Input("dummy-input", "children"),
    )
