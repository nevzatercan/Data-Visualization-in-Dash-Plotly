"""Proje genelinde ortak Plotly layout ayarları ve UI sabitleri."""

from __future__ import annotations

# ── Font sabitleri ────────────────────────────────────────────────────────────
_FONT_COLOR     = "rgba(241, 245, 249, 0.92)"   # slate-100  — yüksek kontrast beyaz
_FONT_COLOR_DIM = "rgba(148, 163, 184, 0.80)"   # slate-400  — ikincil metin
_FONT_FAMILY    = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

# Her grafik için geçerli temel layout ayarları (dark glassmorphism panel)
TRANSPARENT_LAYOUT: dict = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=_FONT_COLOR, family=_FONT_FAMILY, size=12),
)

# Eksen teması — ince, düşük kontrastlı çizgiler
AXIS_STYLE: dict = dict(
    showgrid=True,
    gridcolor="rgba(56, 130, 246, 0.08)",
    linecolor="rgba(56, 130, 246, 0.20)",
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

# Standart margin'ler
CHART_MARGIN: dict      = dict(l=8, r=8, t=36, b=8)
CHART_MARGIN_NOTITLE: dict = dict(l=8, r=8, t=10, b=8)

# ── Grafik serisi renk paleti — harmonik, koyu arka plana oranlanmış ──────────
CHART_COLORS: list[str] = [
    "rgba( 56, 189, 248, 0.90)",   # sky-400      — ana mavi
    "rgba(251, 113, 133, 0.90)",   # rose-400     — sıcak kırmızı
    "rgba( 52, 211, 153, 0.90)",   # emerald-400  — yeşil
    "rgba(251, 191,  36, 0.90)",   # amber-400    — altın sarısı
    "rgba(167, 139, 250, 0.90)",   # violet-400   — mor
    "rgba( 45, 212, 191, 0.90)",   # teal-400     — okyanus mavisi
    "rgba(253, 224,  71, 0.90)",   # yellow-300   — canlı sarı
    "rgba(244, 114, 182, 0.90)",   # pink-400     — pembe
]

# ── Eşik renkleri — PM2.5 ve ölüm oranı kategorileri ────────────────────────
THRESHOLD_COLORS: dict[str, str] = {
    "green":  "#4ade80",   # green-400
    "yellow": "#facc15",   # yellow-400
    "orange": "#fb923c",   # orange-400
    "red":    "#f87171",   # red-400
}

# Choropleth ve scatter için 4-adım renk skalası
DEFAULT_SCALE: list[tuple] = [
    (0,    THRESHOLD_COLORS["green"]),
    (0.33, THRESHOLD_COLORS["yellow"]),
    (0.50, THRESHOLD_COLORS["orange"]),
    (1,    THRESHOLD_COLORS["red"]),
]

# dcc.Graph bileşenleri için ortak config (araç çubuğunu gizler)
GRAPH_CONFIG: dict = {"displayModeBar": False}
