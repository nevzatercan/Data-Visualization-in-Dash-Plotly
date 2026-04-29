"""Alt araç çubuğu: bilgi daireleri, yıl kaydırıcısı, filtre butonları.

info_circle3 (media butonu) Faz 5'te kaldırıldı — callback bağlantısı yoktu.
"""
from __future__ import annotations

from dash import html
import dash_mantine_components as dmc

# Filtre butonları — (id, renk). Renk değerleri kasıtlı olarak daha koyu/doygun;
# veri görselleştirme threshold renkleri (theme.THRESHOLD_COLORS) ile aynı değil.
_FILTER_BUTTONS = [
    ("yesilbuton",    "#85e043"),
    ("sarıbuton",     "#eff229"),
    ("turuncubutton", "#f2a529"),
    ("kırmızıbuton",  "#d3382e"),
]

_FILTER_BTN_BASE_STYLE = {
    "width": "25%",
    "height": "100%",
    "float": "left",
    "cursor": "pointer",
}


def make_toolbar() -> html.Div:
    """Sabit konumlu alt araç çubuğunu döndürür."""
    return html.Div(
        [
            # Sol: bilgi daireleri
            html.Div(
                [
                    dmc.ActionIcon(
                        html.Img(
                            src="assets/img/world.png",
                            style={"width": "80%", "margin": "10%"},
                        ),
                        id="info_circle1",
                        size=50,
                        radius="xl",
                        variant="white",
                        style={
                            "border": "1px solid black",
                            "box-shadow": "rgba(0,0,0,0.35) 0px 5px 15px",
                        },
                    ),
                    dmc.ActionIcon(
                        html.Img(
                            src="assets/img/table.png",
                            style={"width": "82%", "margin": "9%"},
                        ),
                        id="info_circle2",
                        size=50,
                        radius="xl",
                        variant="white",
                        style={
                            "border": "1px solid black",
                            "box-shadow": "rgba(0,0,0,0.35) 0px 5px 15px",
                        },
                    ),
                ],
                id="info_icons",
                style={
                    "float": "left",
                    "width": "30%",
                    "height": "100%",
                    "display": "flex",
                    "justify-content": "space-around",
                    "align-items": "center",
                },
            ),
            # Orta: yıl kaydırıcısı
            html.Div(
                dmc.Slider(
                    id="secilenyıl",
                    min=2010,
                    max=2019,
                    step=1,
                    value=2010,
                    marks=[{"value": i, "label": str(i)} for i in range(2010, 2020)],
                    labelAlwaysOn=True,
                    style={"width": "100%"},
                ),
                style={
                    "float": "left",
                    "width": "30%",
                    "height": "100%",
                    "display": "flex",
                    "align-items": "center",
                    "padding": "0 2%",
                    "z-index": "9",
                },
            ),
            # Sağ: renk filtresi butonları (4 renkli segment)
            html.Div(
                html.Div(
                    [
                        html.Div(
                            id=btn_id,
                            style={**_FILTER_BTN_BASE_STYLE, "backgroundColor": color},
                        )
                        for btn_id, color in _FILTER_BUTTONS
                    ],
                    style={
                        "width": "90%",
                        "height": "60%",
                        "borderRadius": "25px",
                        "overflow": "hidden",
                        "position": "relative",
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "margin-top": "2%",
                    },
                ),
                id="infoImg",
                style={
                    "float": "right",
                    "width": "40%",
                    "height": "100%",
                    "z-index": "9",
                },
            ),
        ],
        style={
            "position": "fixed",
            "bottom": "4px",
            "left": "0",
            "width": "100%",
            "height": "10%",
            "background-color": "transparent",
            "z-index": "9",
        },
    )
