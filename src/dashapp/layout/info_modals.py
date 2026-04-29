"""Bilgi panelleri — dmc.Modal bileşenleri.

İki modal:
- modal-info1  : PM2.5 dünya haritası + sunburst + linearea (eski info_div)
- modal-info2  : Veri tablosu (eski info_div2)

Callback, `opened` prop'unu True/False yaparak modali açıp kapatır.
Close buton ID'leri (closeButton2, closeButton3) geriye dönük uyumluluk için korundu.
"""
from __future__ import annotations

from dash import dash_table, dcc, html
import dash_mantine_components as dmc

from dashapp.data_loader import load_table_data
from dashapp.theme import GRAPH_CONFIG, THRESHOLD_COLORS


def _build_table_styles() -> list[dict]:
    """Number ve Percentage sütunları için koşullu renk stilleri."""
    styles: list[dict] = []
    for col, ranges in [
        ("Number", [
            (0,      10_000, "green"),
            (10_000, 20_000, "yellow"),
            (20_000, 50_000, "orange"),
            (50_000, None,   "red"),
        ]),
        ("Percentage of cause-specific deaths out of total deaths", [
            (0,  3,   "green"),
            (3,  6,   "yellow"),
            (6,  9,   "orange"),
            (9,  101, "red"),
        ]),
    ]:
        for lo, hi, color in ranges:
            fq = (
                f"{{{{{col}}}}} >= {lo} && {{{{{col}}}}} < {hi}"
                if hi is not None
                else f"{{{{{col}}}}} >= {lo}"
            )
            styles.append({
                "if": {"column_id": col, "filter_query": fq},
                "backgroundColor": THRESHOLD_COLORS[color],
                "color": "white",
            })
    return styles


# ---------------------------------------------------------------------------
# Modal 1 — PM2.5 haritası
# ---------------------------------------------------------------------------

def make_info_modal1() -> dmc.Modal:
    """PM2.5 dünya haritası modali (eski info_div)."""
    content = html.Div(
        [
            # Kapat butonu
            html.Div(
                id="closeButton2",
                children="×",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "20px",
                    "font-size": "24px",
                    "color": "black",
                    "cursor": "pointer",
                    "z-index": "9999",
                },
            ),
            # Sol kısım — harita + bölge istatistikleri
            html.Div(
                [
                    html.P(
                        "Bölgelere Göre PM2.5 Seviyeleri",
                        style={"color": "black", "font-size": "145%", "margin-bottom": "2%"},
                    ),
                    html.Img(
                        src="",
                        style={"width": "100%", "margin-top": "1%", "height": "69%"},
                        id="BolgeHaritasi",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([
                                        html.P("Afrika: ", style={"display": "inline"}),
                                        html.Span("29.11 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "margin-right": "-11%", "background-color": "#e3a96d"}),
                                    ], style={"margin-top": "10%", "margin-bottom": "10%"}),
                                    html.Div([
                                        html.P("Batı Pasifik: ", style={"display": "inline"}),
                                        html.Span("17.06 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "background-color": "#bfe982"}),
                                    ]),
                                ],
                                style={"width": "33%", "float": "left", "border-right": "1px solid black", "height": "18%"},
                            ),
                            html.Div(
                                [
                                    html.Div([
                                        html.P("Amerika: ", style={"display": "inline", "margin-left": "-5%"}),
                                        html.Span("14.61 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "margin-right": "-24%", "background-color": "#bfe982"}),
                                    ], style={"margin-top": "10%", "margin-bottom": "10%"}),
                                    html.Div([
                                        html.P("Güneydoğu Asya: ", style={"display": "inline"}),
                                        html.Span("29.81 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "background-color": "#e3a96d"}),
                                    ]),
                                ],
                                style={"width": "33%", "float": "left", "border-right": "1px solid black", "height": "18%"},
                            ),
                            html.Div(
                                [
                                    html.Div([
                                        html.P("Avrupa: ", style={"display": "inline", "margin-left": "-17%"}),
                                        html.Span("19.22 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "margin-right": "-21%", "background-color": "#ddeb83"}),
                                    ], style={"margin-top": "10%", "margin-bottom": "10%"}),
                                    html.Div([
                                        html.P("Ortadoğu: ", style={"display": "inline"}),
                                        html.Span("40.89 μm", style={"border": "1px solid black", "padding": "2px", "margin-left": "5px", "background-color": "#d97378"}),
                                    ]),
                                ],
                                style={"width": "33%", "float": "left"},
                            ),
                        ]
                    ),
                ],
                id="left_div",
                style={
                    "height": "100%",
                    "width": "64%",
                    "float": "left",
                    "background-color": "rgba(255,255,255,0.93)",
                    "border-top-left-radius": "21px",
                    "border-bottom-left-radius": "21px",
                    "border": "2px solid rgba(0,0,0,0.73)",
                    "box-sizing": "border-box",
                    "margin-right": "1%",
                },
            ),
            # Sağ kısım — sunburst + linearea
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="sunburst", figure={}, config=GRAPH_CONFIG),
                        id="top_right_div",
                        style={
                            "height": "50%",
                            "width": "100%",
                            "background-color": "rgba(255,255,255,0.93)",
                            "border": "2px solid rgba(0,0,0,0.73)",
                            "box-sizing": "border-box",
                            "border-top-right-radius": "21px",
                        },
                    ),
                    html.Div(
                        dcc.Graph(id="linearea", figure={}, config=GRAPH_CONFIG),
                        id="bottom_right_div",
                        style={
                            "height": "50%",
                            "width": "100%",
                            "background-color": "rgba(255,255,255,0.93)",
                            "border-bottom": "2px solid rgba(0,0,0,0.73)",
                            "border-left": "2px solid rgba(0,0,0,0.73)",
                            "border-right": "2px solid rgba(0,0,0,0.73)",
                            "box-sizing": "border-box",
                            "border-bottom-right-radius": "21px",
                        },
                    ),
                ],
                style={"width": "34%", "height": "100%", "float": "left", "margin-left": "1%"},
            ),
        ],
        style={"position": "relative", "height": "80vh"},
    )

    return dmc.Modal(
        id="modal-info1",
        opened=False,
        withCloseButton=False,
        size="90%",
        centered=True,
        children=content,
        styles={"body": {"padding": "0", "height": "80vh", "overflow": "hidden"}},
    )


# ---------------------------------------------------------------------------
# Modal 2 — Veri tablosu
# ---------------------------------------------------------------------------

def make_info_modal2() -> dmc.Modal:
    """Veri tablosu modali (eski info_div2)."""
    df = load_table_data()
    columns = [{"name": c, "id": c} for c in df.columns]
    data = df.to_dict("records")

    content = html.Div(
        [
            html.Div(
                id="closeButton3",
                children="×",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "20px",
                    "font-size": "24px",
                    "color": "white",
                    "cursor": "pointer",
                    "z-index": "9999",
                },
            ),
            html.P(
                "PM2.5 ve SOLUNUM YOLU HASTALIKLARINA BAĞLI ÖLÜM VERİLERİ TABLOSU",
                style={"color": "white", "margin-left": "27%", "font-size": "110%"},
            ),
            dash_table.DataTable(
                id="table",
                columns=columns,
                data=data,
                style_cell={"textAlign": "left"},
                style_header={"backgroundColor": "paleturquoise"},
                style_data={"backgroundColor": "lavender"},
                style_data_conditional=_build_table_styles(),
                sort_action="native",
                filter_action="native",
                style_table={
                    "overflowX": "auto",
                    "height": "100%",
                    "width": "100%",
                },
            ),
        ],
        style={"position": "relative", "height": "80vh"},
    )

    return dmc.Modal(
        id="modal-info2",
        opened=False,
        withCloseButton=False,
        size="90%",
        centered=True,
        children=content,
        styles={
            "body": {
                "padding": "0",
                "height": "80vh",
                "overflow": "scroll",
                "background-color": "rgba(0,0,0,0.8)",
            },
            "content": {
                "background-color": "rgba(0,0,0,0.8)",
                "border": "5px solid white",
            },
        },
    )
