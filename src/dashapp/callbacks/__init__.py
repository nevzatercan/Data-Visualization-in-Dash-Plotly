"""Callback paketi.

``register_callbacks(app)`` tek giriş noktasıdır; tüm callback modüllerini
içe aktararak Dash uygulamasına bağlar.
"""
from __future__ import annotations

from dash import Dash

from dashapp.callbacks import click, hover, info, maps, viewport


def register_callbacks(app: Dash) -> None:
    """Tüm callback'leri uygulamaya kaydet."""
    maps.register(app)
    click.register(app)
    hover.register(app)
    info.register(app)
    viewport.register(app)
