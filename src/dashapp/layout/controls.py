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

# Filtre segmentleri — (id, hex-renk, tooltip-etiket)
_FILTER_SEGMENTS = [
    ("yesilbuton",    "#78c850", "İyi  ≤ 18 μg/m³"),
    ("sarıbuton",     "#e8e840", "Orta  ≤ 31 μg/m³"),
    ("turuncubutton", "#f0941c", "Kötü  ≤ 48 μg/m³"),
    ("kırmızıbuton",  "#d43030", "Tehlikeli  > 48 μg/m³"),
]

# Köşe yarıçapları — sol uç / orta / sağ uç
_RADIUS = ["8px 0 0 8px", "0", "0", "0 8px 8px 0"]


def make_toolbar() -> html.Div:
    """Ekranın altına sabitlenmiş floating glassmorphism araç çubuğu."""
    return html.Div(
        # ── Outer centering wrapper ──────────────────────────────────────────
        html.Div(
            [
                # ── 1. Bilgi ikonları ────────────────────────────────────────
                html.Div(
                    [
                        dmc.Tooltip(
                            dmc.ActionIcon(
                                DashIconify(icon="lucide:globe", width=20, color="rgba(255,255,255,0.85)"),
                                id="info_circle1",
                                size=42,
                                radius="xl",
                                variant="subtle",
                                className="info-btn",
                                style={"border": "1px solid rgba(255,255,255,0.15)"},
                            ),
                            label="Bölgesel PM2.5 haritası",
                            position="top",
                            withArrow=True,
                        ),
                        dmc.Tooltip(
                            dmc.ActionIcon(
                                DashIconify(icon="lucide:table-2", width=20, color="rgba(255,255,255,0.85)"),
                                id="info_circle2",
                                size=42,
                                radius="xl",
                                variant="subtle",
                                className="info-btn",
                                style={"border": "1px solid rgba(255,255,255,0.15)"},
                            ),
                            label="Veri tablosu",
                            position="top",
                            withArrow=True,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "10px",
                        "alignItems": "center",
                        "flexShrink": 0,
                    },
                ),

                # ── Dikey ayraç ──────────────────────────────────────────────
                html.Div(style={
                    "width": "1px", "height": "40px",
                    "background": "rgba(255,255,255,0.12)",
                    "flexShrink": 0,
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
                    "background": "rgba(255,255,255,0.12)",
                    "flexShrink": 0,
                }),

                # ── 3. PM2.5 filtre barı ─────────────────────────────────────
                html.Div(
                    [
                        html.Div("PM2.5 FİLTRE", className="panel-label", style={"textAlign": "center"}),
                        # Renkli segment barı
                        html.Div(
                            [
                                dmc.Tooltip(
                                    html.Div(
                                        id=btn_id,
                                        className="filter-seg",
                                        style={
                                            "flex": 1,
                                            "height": "28px",
                                            "backgroundColor": color,
                                            "borderRadius": radius,
                                        },
                                    ),
                                    label=label,
                                    position="top",
                                    withArrow=True,
                                )
                                for (btn_id, color, label), radius
                                in zip(_FILTER_SEGMENTS, _RADIUS)
                            ],
                            id="infoImg",
                            style={
                                "display": "flex",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "boxShadow": "0 2px 12px rgba(0,0,0,0.4)",
                            },
                        ),
                        # Eşik değerleri
                        html.Div(
                            [html.Span(lbl, style={"flex": 1, "textAlign": "center", "color": "rgba(255,255,255,0.45)", "fontSize": "9px"})
                             for lbl in ("≤18", "≤31", "≤48", ">48")],
                            style={"display": "flex", "marginTop": "4px"},
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
                "background": "rgba(13, 17, 30, 0.72)",
                "backdropFilter": "blur(28px) saturate(1.5)",
                "WebkitBackdropFilter": "blur(28px) saturate(1.5)",
                "border": "1px solid rgba(255, 255, 255, 0.10)",
                "borderRadius": "20px",
                "padding": "14px 22px 18px",
                "boxShadow": (
                    "0 8px 32px rgba(0,0,0,0.50), "
                    "0 2px 8px rgba(0,0,0,0.30), "
                    "inset 0 1px 0 rgba(255,255,255,0.08)"
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
