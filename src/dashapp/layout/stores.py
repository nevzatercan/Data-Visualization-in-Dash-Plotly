"""dcc.Store bileşenleri ve yardımcıları.

storage_type='memory': sekme bazlı izolasyon sağlar, sayfa yenilenmesinde
default değerlere döner (multi-user güvenli).
"""

from __future__ import annotations

from dash import dcc


def make_stores() -> list:
    """4 dcc.Store bileşenini liste olarak döndürür."""
    return [
        dcc.Store(id="viewport-store", storage_type="memory", data={"width": 1300, "height": 800}),
        dcc.Store(id="filter-store",   storage_type="memory", data={"is_filtered": 0}),
        dcc.Store(id="panel-store",    storage_type="memory", data={"is_hidden": 1}),
        dcc.Store(id="hover-store",    storage_type="memory", data={"last_iso3": ""}),
    ]


def parse_viewport(vp: dict | None) -> tuple[int, int]:
    """viewport-store datasını (width, height) olarak çözer."""
    d = vp or {}
    return d.get("width", 1300), d.get("height", 800)
