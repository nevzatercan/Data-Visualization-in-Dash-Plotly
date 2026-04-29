"""Tıklama ve hover panelleri.

Üç panel:
- side_clicked_location : sol dar panel (PM2.5 göstergesi, mermi grafiği)
- clicked_location      : sağ geniş panel (7 grafik tablosu)
- hovered_location      : radar tooltip (harita üzerinde hover)
"""
from __future__ import annotations

from dash import dcc, html

from dashapp.theme import GRAPH_CONFIG


# ---------------------------------------------------------------------------
# Sol dar panel — PM2.5 göstergesi
# ---------------------------------------------------------------------------

def make_side_panel() -> html.Div:
    """Sol dar panel — başlangıçta gizli."""
    return html.Div(
        [
            html.Img(
                src="",
                style={
                    "width": "80%",
                    "height": "20%",
                    "margin-left": "10%",
                    "margin-right": "10%",
                    "margin-top": "10%",
                },
                id="pm25img",
            ),
            dcc.Graph(id="gösterge", figure={}),
            html.P(
                id="text2",
                style={
                    "font-size": "14px",
                    "text-align": "center",
                    "margin-top": "-30px",
                    "font-weight": "bold",
                    "font-family": "Arial",
                    "margin-left": "3%",
                    "margin-right": "3%",
                },
            ),
            html.P(
                "Son verilere göre: ",
                id="text1",
                style={
                    "font-size": "20px",
                    "text-align": "center",
                    "margin-top": "15%",
                    "margin-bottom": "-3%",
                },
            ),
            dcc.Graph(id="kursun", figure={}),
            # Açıklama satırı (çizgi göstergeleri)
            html.Div(
                [
                    html.Img(
                        src="assets/img/çizgi.png",
                        style={
                            "vertical-align": "middle",
                            "width": "5%",
                            "padding-left": "3%",
                            "margin-right": "-4%",
                        },
                    ),
                    html.P(
                        ": Tüm yılların ortalama değeri ",
                        style={
                            "display": "inline-block",
                            "margin-left": "10px",
                            "vertical-align": "middle",
                            "font-size": "59%",
                        },
                    ),
                    html.Img(
                        src="assets/img/çizgi2.png",
                        style={
                            "vertical-align": "middle",
                            "width": "11%",
                            "padding-left": "7%",
                        },
                    ),
                    html.P(
                        ": Son yılın değeri",
                        style={
                            "display": "inline-block",
                            "vertical-align": "middle",
                            "font-size": "59%",
                            "margin-left": "1.5%",
                        },
                    ),
                ],
                style={"display": "flex", "align-items": "center"},
            ),
        ],
        id="side_clicked_location",
        style={"display": "none"},
    )


# ---------------------------------------------------------------------------
# Sağ geniş panel — 7 grafik tablosu
# ---------------------------------------------------------------------------

def make_chart_panel() -> html.Div:
    """Sağ geniş panel — başlangıçta gizli."""
    return html.Div(
        [
            html.Div(
                id="closeButton",
                children="×",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "20px",
                    "font-size": "24px",
                    "color": "black",
                    "cursor": "pointer",
                    "display": "block",
                    "z-index": "9999",
                },
            ),
            html.Table(
                [
                    html.Tr(
                        [
                            html.Td(
                                dcc.Graph(id="histogram", figure={}, config=GRAPH_CONFIG),
                                style={
                                    "box-shadow": "2px 2px 2px rgba(0,0,0,0.1)",
                                    "outline": "2px solid rgb(0,0,0,0.5)",
                                    "border-top-left-radius": "12px",
                                },
                                colSpan=4,
                            ),
                            html.Td(
                                dcc.Graph(id="pasta", figure={}, config=GRAPH_CONFIG),
                                style={
                                    "box-shadow": "2px 2px 2px rgba(0,0,0,0.1)",
                                    "border-top-right-radius": "12px",
                                    "outline": "2px solid rgb(0,0,0,0.5)",
                                },
                                colSpan=2,
                                rowSpan=2,
                            ),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td(
                                dcc.Graph(id="balon", figure={}, config=GRAPH_CONFIG),
                                style={
                                    "box-shadow": "2px 2px 2px rgba(0,0,0,0.1)",
                                    "outline": "2px solid rgb(0,0,0,0.5)",
                                },
                                colSpan=4,
                            ),
                        ]
                    ),
                    html.Tr(
                        html.Td(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Graph(id="cizgikutu", figure={}, config=GRAPH_CONFIG),
                                        style={
                                            "width": "50%",
                                            "display": "inline-block",
                                            "box-shadow": "2px 2px 2px rgba(0,0,0,0.1)",
                                            "outline": "2px solid rgb(0,0,0,0.5)",
                                            "border-bottom-left-radius": "12px",
                                            "outline-offset": "1px",
                                        },
                                    ),
                                    html.Div(
                                        dcc.Graph(id="cizgi", figure={}, config=GRAPH_CONFIG),
                                        style={
                                            "width": "50%",
                                            "display": "inline-block",
                                            "box-shadow": "2px 2px 2px rgba(0,0,0,0.1)",
                                            "outline": "2px solid rgb(0,0,0,0.5)",
                                            "border-bottom-right-radius": "12px",
                                            "outline-offset": "1px",
                                        },
                                    ),
                                ]
                            ),
                            style={"width": "100%"},
                            colSpan=6,
                        )
                    ),
                ]
            ),
        ],
        id="clicked_location",
        style={"display": "none"},
    )


# ---------------------------------------------------------------------------
# Radar hover tooltip
# ---------------------------------------------------------------------------

def make_hover_panel() -> html.Div:
    """Harita hover radar tooltip — başlangıçta gizli."""
    return html.Div(
        [dcc.Graph(id="gül", figure={}, config=GRAPH_CONFIG)],
        id="hovered_location",
        style={
            "display": "none",
            "width": "20%",
            "height": "250px",
            "background-color": "transparent",
        },
    )
