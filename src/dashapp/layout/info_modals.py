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
    # Bölge istatistikleri — (ad, değer, renk)
    _REGIONS = [
        ("Afrika",         "29.11 μm", "#fb923c"),
        ("Güneydoğu Asya", "29.81 μm", "#fb923c"),
        ("Ortadoğu",       "40.89 μm", "#f87171"),
        ("Avrupa",         "19.22 μm", "#facc15"),
        ("Batı Pasifik",   "17.06 μm", "#4ade80"),
        ("Amerika",        "14.61 μm", "#4ade80"),
    ]

    content = html.Div(
        [
            # ── Kapat butonu ──────────────────────────────────────────────────
            html.Div(
                id="closeButton2",
                n_clicks=0,
                children="×",
                style={
                    "position": "absolute",
                    "top": "12px",
                    "right": "18px",
                    "fontSize": "26px",
                    "lineHeight": "1",
                    "color": "rgba(148,163,184,0.80)",
                    "cursor": "pointer",
                    "zIndex": 9999,
                    "width": "32px",
                    "height": "32px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "borderRadius": "8px",
                    "background": "rgba(255,255,255,0.06)",
                    "border": "1px solid rgba(56,130,246,0.18)",
                    "transition": "background 0.15s ease",
                },
            ),
            # ── Sol kısım — harita + bölge istatistikleri ─────────────────────
            html.Div(
                [
                    html.P(
                        "Bölgelere Göre PM2.5 Seviyeleri",
                        style={
                            "color": "rgba(241,245,249,0.92)",
                            "fontSize": "145%",
                            "fontWeight": "700",
                            "marginBottom": "2%",
                            "marginLeft": "2%",
                        },
                    ),
                    html.Img(
                        src="",
                        style={"width": "100%", "marginTop": "1%", "height": "63%", "objectFit": "contain"},
                        id="BolgeHaritasi",
                    ),
                    # Bölge değerleri — 2 sütun grid
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(name, style={"color": "rgba(148,163,184,0.80)", "fontSize": "11px"}),
                                    html.Span(
                                        val,
                                        style={
                                            "fontSize": "11px",
                                            "fontWeight": "700",
                                            "color": clr,
                                            "marginLeft": "6px",
                                            "padding": "1px 6px",
                                            "borderRadius": "4px",
                                            "background": "rgba(255,255,255,0.06)",
                                        },
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center", "padding": "4px 8px"},
                            )
                            for name, val, clr in _REGIONS
                        ],
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "0",
                            "marginTop": "8px",
                            "borderTop": "1px solid rgba(56,130,246,0.14)",
                        },
                    ),
                ],
                id="left_div",
                style={
                    "height": "100%",
                    "width": "64%",
                    "float": "left",
                    "background": "rgba(10, 18, 36, 0.82)",
                    "borderTopLeftRadius": "16px",
                    "borderBottomLeftRadius": "16px",
                    "border": "1px solid rgba(56,130,246,0.16)",
                    "boxSizing": "border-box",
                    "marginRight": "1%",
                    "padding": "14px 12px 10px",
                },
            ),
            # ── Sağ kısım — sunburst + linearea ──────────────────────────────
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="sunburst", figure={}, config=GRAPH_CONFIG),
                        id="top_right_div",
                        style={
                            "height": "50%",
                            "width": "100%",
                            "background": "rgba(10, 18, 36, 0.70)",
                            "border": "1px solid rgba(56,130,246,0.14)",
                            "boxSizing": "border-box",
                            "borderTopRightRadius": "16px",
                        },
                    ),
                    html.Div(
                        dcc.Graph(id="linearea", figure={}, config=GRAPH_CONFIG),
                        id="bottom_right_div",
                        style={
                            "height": "50%",
                            "width": "100%",
                            "background": "rgba(10, 18, 36, 0.70)",
                            "borderBottom": "1px solid rgba(56,130,246,0.14)",
                            "borderLeft": "1px solid rgba(56,130,246,0.14)",
                            "borderRight": "1px solid rgba(56,130,246,0.14)",
                            "boxSizing": "border-box",
                            "borderBottomRightRadius": "16px",
                        },
                    ),
                ],
                style={"width": "34%", "height": "100%", "float": "left", "marginLeft": "1%"},
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
        styles={
            "body": {"padding": "0", "height": "80vh", "overflow": "hidden"},
            "content": {
                "background": "rgba(7, 11, 20, 0.95)",
                "border": "1px solid rgba(56,130,246,0.22)",
                "borderRadius": "18px",
            },
        },
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
                n_clicks=0,
                children="×",
                style={
                    "position": "absolute",
                    "top": "12px",
                    "right": "18px",
                    "fontSize": "26px",
                    "lineHeight": "1",
                    "color": "rgba(148,163,184,0.80)",
                    "cursor": "pointer",
                    "zIndex": 9999,
                    "width": "32px",
                    "height": "32px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "borderRadius": "8px",
                    "background": "rgba(255,255,255,0.06)",
                    "border": "1px solid rgba(56,130,246,0.18)",
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
