"""Alt araç çubuğu — floating glassmorphism pill.

Bileşenler:
  info_circle1 / info_circle2 : bilgi modal açıcılar
  secilenyıl                  : yıl kaydırıcısı (2010-2019)
  yesilbuton / sarıbuton / turuncubutton / kırmızıbuton : PM2.5 filtre segmentleri
"""
from __future__ import annotations

from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Filtre segmentleri — (id, hex-renk, kısa-ad, eşik-etiket)
_FILTER_SEGMENTS = [
    ("yesilbuton",    "#22c55e", "İyi",       "≤ 18 μg/m³"),
    ("sarıbuton",     "#eab308", "Orta",      "≤ 31 μg/m³"),
    ("turuncubutton", "#f97316", "Kötü",      "≤ 48 μg/m³"),
    ("kırmızıbuton",  "#ef4444", "Tehlikeli", "> 48 μg/m³"),
]

# Köşe yarıçapları — sol uç / orta / sağ uç
_RADIUS = ["8px 0 0 8px", "0", "0", "0 8px 8px 0"]

# Segment metin rengi: koyu/açık arka plana göre
_TEXT_COLOR = [
    "rgba(0,0,0,0.75)",   # yeşil — açık
    "rgba(0,0,0,0.75)",   # sarı — açık
    "rgba(255,255,255,0.92)",  # turuncu — koyu metin daha okunur
    "rgba(255,255,255,0.92)",  # kırmızı — koyu metin daha okunur
]


def _info_btn(icon: str, btn_id: str, label: str) -> html.Div:
    """İkon + görünür etiket içeren tıklanabilir bilgi butonu."""
    return html.Div(
        [
            DashIconify(icon=icon, width=20, color="rgba(56,189,248,0.88)"),
            html.Span(
                label,
                style={
                    "fontSize": "9px",
                    "fontWeight": "600",
                    "letterSpacing": "0.5px",
                    "color": "rgba(148, 163, 184, 0.80)",
                    "textAlign": "center",
                    "lineHeight": "1.2",
                    "maxWidth": "52px",
                },
            ),
        ],
        id=btn_id,
        n_clicks=0,
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "gap": "4px",
            "padding": "8px 10px",
            "borderRadius": "12px",
            "border": "1px solid rgba(56,130,246,0.22)",
            "background": "rgba(56,130,246,0.06)",
            "cursor": "pointer",
            "minWidth": "58px",
            "transition": "background 0.15s ease",
        },
    )


def make_toolbar() -> html.Div:
    """Ekranın altına sabitlenmiş floating glassmorphism araç çubuğu."""
    return html.Div(
        # ── Outer centering wrapper ──────────────────────────────────────────
        html.Div(
            [
                # ── 1. Bilgi butonları (ikon + etiket) ───────────────────────
                html.Div(
                    [
                        _info_btn("lucide:globe",   "info_circle1", "PM2.5\nHarita"),
                        _info_btn("lucide:table-2", "info_circle2", "Veri\nTablosu"),
                    ],
                    style={
                        "display": "flex",
                        "gap": "10px",
                        "alignItems": "stretch",
                        "flexShrink": 0,
                    },
                ),

                # ── Dikey ayraç ──────────────────────────────────────────────
                html.Div(style={
                    "width": "1px", "height": "40px",
                    "background": "rgba(56, 130, 246, 0.15)",
                    "flexShrink": 0,
                    "alignSelf": "center",
                }),

                # ── 2. Yıl kaydırıcısı ───────────────────────────────────────
                html.Div(
                    [
                        html.Div("YIL", className="panel-label"),
                        dmc.Slider(
                            id="secilenyıl",
                            min=2010, max=2019, step=1, value=2010,
                            marks=[{"value": i, "label": str(i)} for i in range(2010, 2020)],
                            labelAlwaysOn=True,
                            className="toolbar-slider",
                            style={"width": "100%"},
                        ),
                    ],
                    style={
                        "flex": 1,
                        "minWidth": 0,
                        "paddingTop": "4px",
                    },
                ),

                # ── Dikey ayraç ──────────────────────────────────────────────
                html.Div(style={
                    "width": "1px", "height": "40px",
                    "background": "rgba(56, 130, 246, 0.15)",
                    "flexShrink": 0,
                    "alignSelf": "center",
                }),

                # ── 3. PM2.5 filtre barı ─────────────────────────────────────
                html.Div(
                    [
                        html.Div("PM2.5 FİLTRE", className="panel-label", style={"textAlign": "center"}),
                        # Renkli segment barı — her segment kendi adını ve eşiğini gösterir
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            name,
                                            style={
                                                "fontSize": "10px",
                                                "fontWeight": "700",
                                                "color": txt_color,
                                                "lineHeight": "1.1",
                                            },
                                        ),
                                        html.Span(
                                            threshold,
                                            style={
                                                "fontSize": "8px",
                                                "color": txt_color,
                                                "opacity": "0.85",
                                                "lineHeight": "1.1",
                                            },
                                        ),
                                    ],
                                    id=btn_id,
                                    n_clicks=0,
                                    className="filter-seg",
                                    style={
                                        "flex": 1,
                                        "height": "42px",
                                        "backgroundColor": color,
                                        "borderRadius": radius,
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "gap": "1px",
                                        "cursor": "pointer",
                                        "padding": "0 4px",
                                        "transition": "filter 0.15s ease",
                                    },
                                )
                                for (btn_id, color, name, threshold), radius, txt_color
                                in zip(_FILTER_SEGMENTS, _RADIUS, _TEXT_COLOR)
                            ],
                            id="infoImg",
                            style={
                                "display": "flex",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "boxShadow": "0 2px 12px rgba(0,0,0,0.4)",
                            },
                        ),
                    ],
                    style={"minWidth": "220px", "flexShrink": 0},
                ),
            ],
            # ── Glass container ───────────────────────────────────────────────
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "20px",
                "background": "rgba(10, 18, 36, 0.90)",
                "backdropFilter": "blur(32px) saturate(1.7)",
                "WebkitBackdropFilter": "blur(32px) saturate(1.7)",
                "border": "1px solid rgba(56, 130, 246, 0.18)",
                "borderRadius": "20px",
                "padding": "14px 22px 18px",
                "boxShadow": (
                    "0 8px 40px rgba(0,0,0,0.55), "
                    "0 2px 8px rgba(0,0,0,0.35), "
                    "inset 0 1px 0 rgba(255,255,255,0.05), "
                    "inset 0 0 0 1px rgba(0,0,0,0.30)"
                ),
            },
        ),
        # ── Outer positioning wrapper ────────────────────────────────────────
        style={
            "position": "fixed",
            "bottom": "48px",   # Dash debug bar (~32px) + nefes boşluğu
            "left": "50%",
            "transform": "translateX(-50%)",
            "width": "calc(100% - 40px)",
            "maxWidth": "1060px",
            "zIndex": 9999,
        },
    )
