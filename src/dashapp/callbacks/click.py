"""Harita tıklama callback'i — ülke seçilince yan panel + 7 grafik güncellenir."""
from __future__ import annotations

import dash
from dash import Input, Output, State

import dashapp.charts.balon as _balon_chart
import dashapp.charts.cizgi as _cizgi_chart
import dashapp.charts.cizgikutu as _cizgikutu_chart
import dashapp.charts.gosterge as _gosterge_chart
import dashapp.charts.histogram as _histogram_chart
import dashapp.charts.kursun as _kursun_chart
import dashapp.charts.pasta as _pasta_chart
from dashapp.data_loader import load_merged
from dashapp.layout.stores import parse_viewport
from dashapp.transforms import colorchoose, filter_total, safe_first
from dashapp.utils.translations import to_turkish

_CHART_PANEL_STYLE: dict = {
    "position": "fixed", "top": 0, "right": 0,
    "margin-top": "6.25%", "margin-right": "5%",
    "margin-bottom": "6.25%", "margin-left": "25%",
    "width": "70.5%", "height": "75%",
    "background-color": "rgb(255,255,255,0.95)",
    "z-index": "1000", "display": "inline-block",
    "border-radius": "15px",
    "box-shadow": "0 8px 16px rgba(0, 0, 0, 0.2)",
    "border": "1px solid rgb(135,135,135)",
}
_SIDE_PANEL_BASE_STYLE: dict = {
    "display": "inline-block",
    "width": "18%", "height": "75%",
    "position": "fixed", "margin-top": "5.75%",
    "margin-bottom": "6.25%", "margin-left": "5%",
    "border-radius": "15px",
    "box-shadow": "0 8px 16px rgba(0, 0, 0, 0.2)",
    "border": "1px solid rgb(135,135,135)",
}


_empty = {"data": []}
_hide = {"display": "none"}
_reset = (_hide, _hide, "", "", _empty, _empty, _empty, _empty, _empty, _empty, _empty, {"is_hidden": 1})


def register(app: dash.Dash) -> None:
    merged_df = load_merged()
    # Pre-built for O(1) country-name lookup on every map click
    _country_name: dict[str, str] = dict(
        zip(merged_df["Country Code"], merged_df["Country Name"])
    )

    @app.callback(
        [Output("clicked_location", "style"),
         Output("side_clicked_location", "style"),
         Output("pm25img", "src"),
         Output("text2", "children"),
         Output("histogram", "figure"),
         Output("cizgi", "figure"),
         Output("cizgikutu", "figure"),
         Output("pasta", "figure"),
         Output("balon", "figure"),
         Output("gösterge", "figure"),
         Output("kursun", "figure"),
         Output("panel-store", "data")],
        [Input("Harita", "clickData"),
         Input("closeButton", "n_clicks")],
        [State("secilenyıl", "value"),
         State("viewport-store", "data"),
         State("panel-store", "data")],
    )
    def display_click_data(clickData, n_clicks, option_slctd, vp, panel_data):
        width, height = parse_viewport(vp)
        is_hidden = (panel_data or {}).get("is_hidden", 1)

        if n_clicks and is_hidden == 0:
            return _reset

        if clickData is None:
            return _reset

        clicked_location = clickData["points"][0]["location"]
        country_name_en = _country_name.get(clicked_location, clicked_location)
        country_name_tr = to_turkish(country_name_en)
        if " " in country_name_tr:
            country_name_tr = country_name_tr.split(" ")[0]

        filtered_df = filter_total(merged_df, year=option_slctd, country=clicked_location)
        death_value = safe_first(filtered_df["Number"], default=0)
        text = (
            f"Solunum yolu hastalıklarına(SYH) bağlı {option_slctd} yılı ölüm sayısı: {int(death_value)} kişi"
            if death_value
            else "Bu ülkenin ölüm verileri bulunmamaktadır."
        )

        norm_value = safe_first(filtered_df["NormalizationForFactValueNumeric"])
        cloud_img, cloud_bg = colorchoose(norm_value)

        return (
            _CHART_PANEL_STYLE,
            {**_SIDE_PANEL_BASE_STYLE, "background-color": cloud_bg},
            cloud_img,
            text,
            _histogram_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr),
            _cizgikutu_chart.figure(clicked_location, width=width, height=height, country_name_english=country_name_en),
            _cizgi_chart.figure(clicked_location, width=width, height=height, country_name=country_name_tr),
            _pasta_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr, country_name_english=country_name_en),
            _balon_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr),
            _gosterge_chart.figure(option_slctd, clicked_location, width=width, height=height),
            _kursun_chart.figure(clicked_location, width=width, height=height),
            {"is_hidden": 0},
        )
