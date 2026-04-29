"""Tıklama ve hover panelleri — glassmorphism tasarımı.

Üç panel:
  side_clicked_location : sol dar panel (PM2.5 göstergesi + mermi grafiği)
  clicked_location      : sağ geniş panel (7 grafik tablosu)
  hovered_location      : harita hover radar tooltip
"""
from __future__ import annotations

from dash import dcc, html

from dashapp.theme import GRAPH_CONFIG

# ── Ortak grafik config (mod bar gizli) ─────────────────────────────────────
_GC = GRAPH_CONFIG


# ═══════════════════════════════════════════════════════════════════════════════
# Sol dar panel — PM2.5 göstergesi
# ═══════════════════════════════════════════════════════════════════════════════

def make_side_panel() -> html.Div:
    """Sol dar panel — başlangıçta gizli."""
    return html.Div(
        [
            # Kapat butonu
            html.Div("×", id="close-side", className="close-x",
                     style={"display": "none"}),  # side panel kendi close butonu yok, chart panel'deki kullanılır

            # PM2.5 bulut görseli
            html.Div(
                html.Img(
                    src="",
                    id="pm25img",
                    style={"width": "72px", "height": "72px", "objectFit": "contain"},
                ),
                style={"textAlign": "center", "paddingTop": "28px"},
            ),

            # Gauge grafiği
            dcc.Loading(
                dcc.Graph(id="gösterge", figure={}, config=_GC, style={"height": "160px"}),
                type="circle",
                color="rgba(96,165,250,0.85)",
                overlay_style={"visibility": "visible", "opacity": 0.45},
                delay_show=150,
            ),

            # Ölüm sayısı metni
            html.P(
                id="text2",
                style={
                    "fontSize": "12px",
                    "textAlign": "center",
                    "color": "rgba(148, 163, 184, 0.85)",
                    "fontWeight": "500",
                    "lineHeight": "1.5",
                    "padding": "0 14px",
                    "marginTop": "-10px",
                },
            ),

            # Ayraç
            html.Div(style={
                "height": "1px",
                "background": "rgba(56, 130, 246, 0.14)",
                "margin": "14px 16px",
            }),

            # "Son verilere göre" başlığı
            html.P(
                "Son verilere göre",
                id="text1",
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": "1px",
                    "textTransform": "uppercase",
                    "textAlign": "center",
                    "color": "rgba(100, 116, 139, 0.70)",
                    "marginBottom": "0",
                },
            ),

            # Mermi grafiği
            dcc.Loading(
                dcc.Graph(id="kursun", figure={}, config=_GC, style={"height": "160px"}),
                type="circle",
                color="rgba(96,165,250,0.85)",
                overlay_style={"visibility": "visible", "opacity": 0.45},
                delay_show=150,
            ),

            # Çizgi açıklaması
            html.Div(
                [
                    html.Img(
                        src="assets/img/çizgi.png",
                        style={"height": "12px", "marginRight": "6px", "verticalAlign": "middle"},
                    ),
                    html.Span(
                        "Tüm yıllar ort.",
                        style={"fontSize": "10px", "color": "rgba(148, 163, 184, 0.60)", "marginRight": "14px"},
                    ),
                    html.Img(
                        src="assets/img/çizgi2.png",
                        style={"height": "12px", "marginRight": "6px", "verticalAlign": "middle"},
                    ),
                    html.Span(
                        "Son yıl",
                        style={"fontSize": "10px", "color": "rgba(148, 163, 184, 0.60)"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "paddingBottom": "12px",
                },
            ),
        ],
        id="side_clicked_location",
        className="glass panel-left",
        style={"display": "none"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Sağ geniş panel — 7 grafik grid'i
# ═══════════════════════════════════════════════════════════════════════════════

def make_chart_panel() -> html.Div:
    """Sağ geniş panel — başlangıçta gizli.

    Grid düzeni (2 sütun: 2fr | 1fr):
      [histogram  ] [pasta     ]
      [balon      ] [pasta     ]  ← pasta 2 satıra yayılır
      [cizgikutu  +  cizgi     ]  ← 3. satır tam genişlik (flex 50/50)
    """
    return html.Div(
        [
            # ── Kapat butonu ──────────────────────────────────────────────────
            html.Div("×", id="closeButton", className="close-x"),

            # ── Grafik grid ───────────────────────────────────────────────────
            dcc.Loading(
                html.Div(
                    [
                        # Histogram — sol üst
                        html.Div(
                            dcc.Graph(id="histogram", figure={}, config=_GC),
                            style=_cell(radius="12px 0 0 0"),
                        ),
                        # Pasta — sağ sütun, 2 satıra yayılır
                        html.Div(
                            dcc.Graph(id="pasta", figure={}, config=_GC),
                            style={**_cell(radius="0 12px 0 0"), "gridRow": "span 2"},
                        ),
                        # Balon — sol orta
                        html.Div(
                            dcc.Graph(id="balon", figure={}, config=_GC),
                            style=_cell(),
                        ),
                        # 3. satır: tam genişlik, flex 50/50
                        html.Div(
                            [
                                html.Div(
                                    dcc.Graph(id="cizgikutu", figure={}, config=_GC),
                                    style=_cell(radius="0 0 0 12px"),
                                ),
                                html.Div(
                                    dcc.Graph(id="cizgi", figure={}, config=_GC),
                                    style=_cell(radius="0 0 12px 0"),
                                ),
                            ],
                            style={
                                "gridColumn": "1 / -1",
                                "display": "flex",
                            },
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "2fr 1fr",
                        "gridTemplateRows": "1fr 1fr 1fr",
                        "height": "100%",
                        "overflow": "hidden",
                        "borderRadius": "12px",
                    },
                ),
                type="circle",
                color="rgba(96,165,250,0.90)",
                overlay_style={
                    "visibility": "visible",
                    "opacity": 0.5,
                    "filter": "blur(1px)",
                },
                style={"height": "100%"},
                delay_show=100,
            ),
        ],
        id="clicked_location",
        className="glass panel-right",
        style={"display": "none"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Hover radar tooltip
# ═══════════════════════════════════════════════════════════════════════════════

def make_hover_panel() -> html.Div:
    """Harita hover radar tooltip — başlangıçta gizli."""
    return html.Div(
        [dcc.Graph(id="gül", figure={}, config=_GC)],
        id="hovered_location",
        style={
            "display": "none",
            "width": "20%",
            "height": "250px",
            "background": "transparent",
        },
    )


# ── Yardımcı stil fonksiyonları ───────────────────────────────────────────────

def _cell(radius: str = "0") -> dict:
    """Grafik hücresi için temel stil."""
    return {
        "borderRadius": radius,
        "overflow": "hidden",
        "background": "rgba(56, 130, 246, 0.04)",
        "border": "1px solid rgba(56, 130, 246, 0.10)",
    }
