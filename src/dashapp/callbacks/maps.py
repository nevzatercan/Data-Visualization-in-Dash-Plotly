"""Harita callback'i — WebGL Mapbox tabanlı choropleth."""
from __future__ import annotations

import dash
import plotly.graph_objects as go
from dash import Input, Output, State

from dashapp.data_loader import load_air, load_country_centroids, load_merged
from dashapp.layout.stores import parse_viewport
from dashapp.theme import DEFAULT_SCALE, THRESHOLD_COLORS
from dashapp.transforms import filter_total

# GeoJSON URL: Dash tarafından statik olarak sunulur, tarayıcı bir kez indirir ve önbelleğe alır.
# Python callback'inde GeoJSON veri gönderilmez → her güncellemede sıfır overhead.
_GEOJSON_URL = "/assets/geojson/countries.geojson"

# Filtre buton konfigürasyonu: prop_id → (flag, tek-renkli-skala, filtre-fn)
_FILTER_CONFIG = {
    "yesilbuton.n_clicks":    (1, [(0, THRESHOLD_COLORS["green"]),  (1, THRESHOLD_COLORS["green"])],  lambda df: df[df["FactValueNumeric"] <= 18]),
    "sarıbuton.n_clicks":     (2, [(0, THRESHOLD_COLORS["yellow"]), (1, THRESHOLD_COLORS["yellow"])], lambda df: df[(df["FactValueNumeric"] > 18) & (df["FactValueNumeric"] <= 31)]),
    "turuncubutton.n_clicks": (3, [(0, THRESHOLD_COLORS["orange"]), (1, THRESHOLD_COLORS["orange"])], lambda df: df[(df["FactValueNumeric"] > 31) & (df["FactValueNumeric"] <= 48)]),
    "kırmızıbuton.n_clicks":  (4, [(0, THRESHOLD_COLORS["red"]),    (1, THRESHOLD_COLORS["red"])],    lambda df: df[df["FactValueNumeric"] > 48]),
}

# Mapbox carto-darkmatter: ücretsiz, token gerektirmez.
_MAPBOX_STYLE = "carto-darkmatter"
_MAP_CENTER = {"lat": 25, "lon": 10}
_MAP_ZOOM = 1.4


def register(app: dash.Dash) -> None:
    df_air = load_air()
    merged_df = load_merged()
    centroids = load_country_centroids()

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

        # ── Choropleth (PM2.5 seviyesi renk dolgusu) ─────────────────────────
        fig = go.Figure(go.Choroplethmapbox(
            geojson=_GEOJSON_URL,
            featureidkey="properties.ISO3166-1-Alpha-3",
            locations=filtered_df_air["SpatialDimValueCode"],
            z=filtered_df_air["NormalizationForFactValueNumeric"],
            colorscale=new_color_scale,
            marker_opacity=0.78,
            marker_line_width=0.4,
            marker_line_color="rgba(255,255,255,0.18)",
            showscale=False,
            hoverinfo="none",
            below="",
        ))

        # ── Scatter baloncukları (ölüm oranı) ────────────────────────────────
        lats: list[float] = []
        lons: list[float] = []
        sizes: list[float] = []
        colors: list[float] = []

        for iso, perc, norm in zip(
            filteredmerged_df["Country Code"],
            filteredmerged_df["Percentage of cause-specific deaths out of total deaths"],
            filteredmerged_df["NormalizationForPerDeath"],
        ):
            if iso not in centroids:
                continue
            lat, lon = centroids[iso]
            lats.append(lat)
            lons.append(lon)
            sizes.append(max(3.0, float(perc) * 2.5))
            colors.append(float(norm))

        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=sizes,
                color=colors,
                colorscale=DEFAULT_SCALE,
                opacity=0.65,
                sizemin=3,
            ),
            hoverinfo="none",
            showlegend=False,
        ))

        # ── Layout ───────────────────────────────────────────────────────────
        fig.update_layout(
            mapbox=dict(
                style=_MAPBOX_STYLE,
                center=_MAP_CENTER,
                zoom=_MAP_ZOOM,
            ),
            showlegend=False,
            autosize=True,
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
            paper_bgcolor="rgba(0,0,0,0)",
            uirevision="map",   # zoom/pan korunur, veri güncellemesinde reset olmaz
        )

        if (filter_data or {}).get("is_filtered", 0) == isFiltered:
            return fig, dash.no_update
        return fig, {"is_filtered": isFiltered}
