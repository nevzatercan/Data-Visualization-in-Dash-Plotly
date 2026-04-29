"""Proje genelinde ortak Plotly layout ayarları ve UI sabitleri.

Her grafik modülünden ``from dashapp.theme import TRANSPARENT_LAYOUT``
ile içe aktarılır ve ``fig.update_layout(**TRANSPARENT_LAYOUT)`` ile
uygulanır.  Modül-düzeyinde grafiklerin tekrar eden ``update_layout``
bloklarını ortadan kaldırır.
"""

from __future__ import annotations

# Her grafik için geçerli temel layout ayarları
TRANSPARENT_LAYOUT: dict = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="black"),
)

# Eksen teması — showgrid=False + siyah çizgi
AXIS_STYLE: dict = dict(
    showgrid=False,
    linecolor="black",
    linewidth=2.5,
    tickfont=dict(color="black"),
)

# ---------------------------------------------------------------------------
# Renk sabitleri — veri görselleştirme (PM2.5 ve ölüm oranı eşikleri)
# Not: filtre buton renkleri (controls.py) bunlardan kasıtlı olarak daha
# koyu/doygun — ayrı bir görsel dil (UI buton rengi ≠ veri rengi).
# ---------------------------------------------------------------------------
THRESHOLD_COLORS: dict[str, str] = {
    "green":  "#b3eb73",
    "yellow": "#fbed71",
    "orange": "#efb35d",
    "red":    "#e86c75",
}

# Choropleth ve scatter için varsayılan 4-dur renk skalası
DEFAULT_SCALE: list[tuple] = [
    (0,    THRESHOLD_COLORS["green"]),
    (0.33, THRESHOLD_COLORS["yellow"]),
    (0.45, THRESHOLD_COLORS["orange"]),
    (1,    THRESHOLD_COLORS["red"]),
]

# dcc.Graph bileşenleri için ortak config (araç çubuğunu gizler)
GRAPH_CONFIG: dict = {"displayModeBar": False}
