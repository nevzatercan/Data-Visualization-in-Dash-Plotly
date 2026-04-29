"""Proje genelinde ortak Plotly layout ayarları ve UI sabitleri.

Her grafik modülünden ``from dashapp.theme import TRANSPARENT_LAYOUT``
ile içe aktarılır ve ``fig.update_layout(**TRANSPARENT_LAYOUT)`` ile
uygulanır.  Modül-düzeyinde grafiklerin tekrar eden ``update_layout``
bloklarını ortadan kaldırır.
"""

from __future__ import annotations

# ── Tüm grafik fontları için temel renk/aile sabiti ──────────────────────────
_FONT_COLOR   = "rgba(255, 255, 255, 0.82)"
_FONT_COLOR_DIM = "rgba(255, 255, 255, 0.45)"
_FONT_FAMILY  = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

# Her grafik için geçerli temel layout ayarları (dark glassmorphism panel)
TRANSPARENT_LAYOUT: dict = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=_FONT_COLOR, family=_FONT_FAMILY, size=12),
)

# Eksen teması — dark panel uyumlu ince beyaz çizgi
AXIS_STYLE: dict = dict(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.06)",
    linecolor="rgba(255,255,255,0.18)",
    linewidth=1.5,
    tickfont=dict(color=_FONT_COLOR_DIM, size=10),
    title_font=dict(color=_FONT_COLOR_DIM),
)

# Grafik başlığı için tutarlı stil
CHART_TITLE_STYLE: dict = dict(
    font=dict(size=12, color=_FONT_COLOR, family=_FONT_FAMILY),
    x=0.5, xanchor="center",
    y=0.98, yanchor="top",
    pad=dict(t=4),
)

# Standart küçük margin
CHART_MARGIN: dict = dict(l=8, r=8, t=36, b=8)
CHART_MARGIN_NOTITLE: dict = dict(l=8, r=8, t=10, b=8)

# Consistent renk paleti — tüm grafiklerde döngüsel kullanım
CHART_COLORS: list[str] = [
    "rgba(96,  165, 250, 0.90)",  # blue-400
    "rgba(248, 113, 113, 0.90)",  # red-400
    "rgba(52,  211, 153, 0.90)",  # emerald-400
    "rgba(251, 146,  60, 0.90)",  # orange-400
    "rgba(167, 139, 250, 0.90)",  # violet-400
    "rgba( 34, 211, 238, 0.90)",  # cyan-400
    "rgba(250, 204,  21, 0.90)",  # yellow-400
    "rgba(244, 114, 182, 0.90)",  # pink-400
]

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
