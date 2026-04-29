"""Proje genelinde ortak Plotly layout ayarları.

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
