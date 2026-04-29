"""Harita callback'i — yıl/filtre değişince choropleth + scatter yeniden çizilir."""
from __future__ import annotations

import dash
import plotly.graph_objects as go
from dash import Input, Output, State

from dashapp.data_loader import load_air, load_merged
from dashapp.layout.stores import parse_viewport
from dashapp.theme import DEFAULT_SCALE
from dashapp.transforms import filter_total

# Filtre buton konfigürasyonu: prop_id → (flag, tek-renkli-skala, filtre-fn)
_FILTER_CONFIG = {
    "yesilbuton.n_clicks":    (1, [(0, "#b3eb73"), (1, "#b3eb73")], lambda df: df[df["FactValueNumeric"] <= 18]),
    "sarıbuton.n_clicks":     (2, [(0, "#fbed71"), (1, "#fbed71")], lambda df: df[(df["FactValueNumeric"] > 18) & (df["FactValueNumeric"] <= 31)]),
    "turuncubutton.n_clicks": (3, [(0, "#efb35d"), (1, "#efb35d")], lambda df: df[(df["FactValueNumeric"] > 31) & (df["FactValueNumeric"] <= 48)]),
    "kırmızıbuton.n_clicks":  (4, [(0, "#e86c75"), (1, "#e86c75")], lambda df: df[df["FactValueNumeric"] > 48]),
}


def register(app: dash.Dash) -> None:
    df_air = load_air()
    merged_df = load_merged()

    @app.callback(
        [Output("Harita", "figure"),
         Output("filter-store", "data")],
        [Input("secilenyıl", "value"),
         Input("yesilbuton", "n_clicks"),
         Input("sarıbuton", "n_clicks"),
         Input("turuncubutton", "n_clicks"),
         Input("kırmızıbuton", "n_clicks")],
        [State("viewport-store", "data"),
         State("filter-store", "data")],
    )
    def update_maps(option_slctd, _g, _y, _o, _r, vp, filter_data):
        width, height = parse_viewport(vp)
        isFiltered = (filter_data or {}).get("is_filtered", 0)

        ctx = dash.callback_context
        filtered_df_air = filter_total(df_air, year=option_slctd, dim1="Total", dim1_y=None)
        filteredmerged_df = filter_total(merged_df, year=option_slctd)
        new_color_scale = DEFAULT_SCALE

        prop_id = ctx.triggered[0]["prop_id"]
        if prop_id in _FILTER_CONFIG:
            flag, single_scale, mask_fn = _FILTER_CONFIG[prop_id]
            if isFiltered != flag:
                filtered_df_air = mask_fn(filtered_df_air)
                new_color_scale = single_scale
                isFiltered = flag
            else:
                isFiltered = 0

        fig = go.Figure()
        fig.add_trace(go.Choropleth(
            hoverinfo="none",
            locationmode="ISO-3",
            locations=filtered_df_air["SpatialDimValueCode"],
            z=filtered_df_air["NormalizationForFactValueNumeric"],
            colorscale=new_color_scale,
            showscale=False,
        ))
        fig.add_trace(go.Scattergeo(
            hoverinfo="none",
            locationmode="ISO-3",
            locations=filteredmerged_df["Country Code"],
            text=filteredmerged_df["Country Name"],
            mode="markers",
            marker=dict(
                size=filteredmerged_df["Percentage of cause-specific deaths out of total deaths"] * 2.5,
                color=filteredmerged_df["NormalizationForPerDeath"],
                colorscale=DEFAULT_SCALE,
            ),
        ))
        fig.update_geos(
            projection_scale=1, showframe=False,
            projection_type="equirectangular",
            showcountries=True, showocean=True,
            oceancolor="#a3d6fb", visible=True,
        )
        fig.update_layout(
            showlegend=False, autosize=False,
            width=width, height=height,
            margin=dict(l=0, r=0, b=0, t=0),
            dragmode="turntable",
        )

        if (filter_data or {}).get("is_filtered", 0) == isFiltered:
            return fig, dash.no_update
        return fig, {"is_filtered": isFiltered}
