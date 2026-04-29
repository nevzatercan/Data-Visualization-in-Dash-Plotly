#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 05:27:29 2024

@author: nevzatercan
"""

import dash
import plotly.graph_objects as go
from dash import (
    ClientsideFunction,
    Dash,
    Input,
    Output,
    State,
    dcc,
    html,
)
import dash_mantine_components as dmc

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True


from dashapp.data_loader import load_air, load_merged
from dashapp.transforms import colorchoose, filter_total, safe_first
from dashapp.utils.translations import to_turkish
from dashapp.layout.stores import make_stores, parse_viewport
from dashapp.layout.controls import make_toolbar
from dashapp.layout.panels import make_side_panel, make_chart_panel, make_hover_panel
from dashapp.layout.info_modals import make_info_modal1, make_info_modal2
import dashapp.charts.histogram as _histogram_chart
import dashapp.charts.cizgikutu as _cizgikutu_chart
import dashapp.charts.cizgi as _cizgi_chart
import dashapp.charts.pasta as _pasta_chart
import dashapp.charts.balon as _balon_chart
import dashapp.charts.gosterge as _gosterge_chart
import dashapp.charts.kursun as _kursun_chart
import dashapp.charts.sunburst as _sunburst_chart
import dashapp.charts.linearea as _linearea_chart
import dashapp.charts.radar as _radar_chart

df_air = load_air()
merged_df = load_merged()


# Uygulama düzeni
app.layout = dmc.MantineProvider(
    html.Div([
        *make_stores(),
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        html.Div(id='dummy-input', style={'display': 'none'}),

        make_toolbar(),

        html.Div([
            dcc.Graph(
                id='Harita',
                figure={},
                config={'displayModeBar': False},
                clear_on_unhover=True
            ),
        ],
        style={'position': 'absolute', 'top': '0px !important', 'left': '0px !important', 'overflow-y': 'hidden', 'margin-top': '-4.6%'}),

        make_side_panel(),
        make_chart_panel(),
        make_hover_panel(),
        make_info_modal1(),
        make_info_modal2(),
    ])
)


# Filtre buton sabitleri — her buton için (flag, tek-renkli-skala, filtre-fn)
_DEFAULT_SCALE = [(0, '#b3eb73'), (0.33, '#fbed71'), (0.45, '#efb35d'), (1, '#e86c75')]
_FILTER_CONFIG = {
    'yesilbuton.n_clicks':    (1, [(0, '#b3eb73'), (1, '#b3eb73')],    lambda df: df[df["FactValueNumeric"] <= 18]),
    'sarıbuton.n_clicks':     (2, [(0, '#fbed71'), (1, '#fbed71')],    lambda df: df[(df["FactValueNumeric"] > 18) & (df["FactValueNumeric"] <= 31)]),
    'turuncubutton.n_clicks': (3, [(0, '#efb35d'), (1, '#efb35d')],    lambda df: df[(df["FactValueNumeric"] > 31) & (df["FactValueNumeric"] <= 48)]),
    'kırmızıbuton.n_clicks':  (4, [(0, '#e86c75'), (1, '#e86c75')],    lambda df: df[df["FactValueNumeric"] > 48]),
}

# Map haritasının güncelleme callback'i
@app.callback(
    [Output('Harita', 'figure'),
     Output('filter-store', 'data')],
    [Input('secilenyıl', 'value'),
     Input('yesilbuton', 'n_clicks'),
     Input('sarıbuton', 'n_clicks'),
     Input('turuncubutton', 'n_clicks'),
     Input('kırmızıbuton', 'n_clicks')],
    [State('viewport-store', 'data'),
     State('filter-store', 'data')],
)
def update_maps(option_slctd, greenButton_clicks, yellowButton_clicks, orangeButton_clicks, redButton_clicks, vp, filter_data):
    width, height = parse_viewport(vp)
    isFiltered = (filter_data or {}).get('is_filtered', 0)

    ctx = dash.callback_context
    filtered_df_air = filter_total(df_air, year=option_slctd, dim1='Total', dim1_y=None)
    filteredmerged_df = filter_total(merged_df, year=option_slctd)
    new_color_scale = _DEFAULT_SCALE

    prop_id = ctx.triggered[0]['prop_id']
    if prop_id in _FILTER_CONFIG:
        flag, single_scale, mask_fn = _FILTER_CONFIG[prop_id]
        if isFiltered != flag:
            filtered_df_air = mask_fn(filtered_df_air)
            new_color_scale = single_scale
            isFiltered = flag
        else:
            isFiltered = 0
            # new_color_scale zaten _DEFAULT_SCALE olarak ayarlı

    #Figure Oluşturma
    fig = go.Figure()

    # Choropleth grafiği oluşturma ve fig'e ekleme
    choropleth_trace = go.Choropleth(
        hoverinfo="none",
        locationmode='ISO-3',
        locations=filtered_df_air['SpatialDimValueCode'],
        z=filtered_df_air['NormalizationForFactValueNumeric'],
        colorscale=new_color_scale,
        showscale=False,
    )
    fig.add_trace(choropleth_trace)

    # Scatter_geo grafiği oluşturma — ölüm oranları her zaman tam skala
    scatter_geo_trace = go.Scattergeo(
        hoverinfo="none",
        locationmode='ISO-3',
        locations=filteredmerged_df['Country Code'],
        text=filteredmerged_df['Country Name'],
        mode="markers",
        marker=dict(
            size=filteredmerged_df['Percentage of cause-specific deaths out of total deaths'] * 2.5,
            color=filteredmerged_df['NormalizationForPerDeath'],
            colorscale=_DEFAULT_SCALE,
        )
    )
    fig.add_trace(scatter_geo_trace)

    fig.update_geos(
        projection_scale=1,
        showframe=False,
        projection_type="equirectangular",
        showcountries=True,
        showocean=True,
        oceancolor="#a3d6fb",
        visible=True
    )
    fig.update_layout(
        showlegend=False,
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=0, r=0, b=0, t=0),
        dragmode='turntable'
    )

    # Slider drag'de isFiltered değişmediyse store'u gereksiz güncelleme
    new_filter_data = {'is_filtered': isFiltered}
    if (filter_data or {}).get('is_filtered', 0) == isFiltered:
        return fig, dash.no_update
    return fig, new_filter_data



@app.callback(
    [Output('clicked_location', 'style'),
     Output('side_clicked_location', 'style'),
     Output('pm25img', 'src'),
     Output('text2', 'children'),
     Output('histogram', 'figure'),
     Output('cizgi', 'figure'),
     Output('cizgikutu', 'figure'),
     Output('pasta', 'figure'),
     Output('balon', 'figure'),
     Output('gösterge', 'figure'),
     Output('kursun', 'figure'),
     Output('panel-store', 'data')],
    [Input('Harita', 'clickData'),
     Input('closeButton', 'n_clicks')],
    [State('secilenyıl', 'value'),
     State('viewport-store', 'data'),
     State('panel-store', 'data')],
)
def display_click_data(clickData, n_clicks, option_slctd, vp, panel_data):
    width, height = parse_viewport(vp)
    is_hidden = (panel_data or {}).get('is_hidden', 1)

    _empty = {'data': []}
    _hide  = {'display': 'none'}
    _reset = (_hide, _hide, "", "", _empty, _empty, _empty, _empty, _empty, _empty, _empty, {'is_hidden': 1})

    if n_clicks and is_hidden == 0:
        return _reset

    if clickData is not None:
        clicked_location = clickData['points'][0]['location']
        country_name_en = safe_first(
            merged_df[merged_df['Country Code'] == clicked_location]['Country Name'].drop_duplicates(),
            default=clicked_location,
        )
        country_name_tr = to_turkish(country_name_en)
        if ' ' in country_name_tr:
            country_name_tr = country_name_tr.split(' ')[0]

        filtered_df_forcolor = filter_total(merged_df, year=option_slctd, country=clicked_location)
        death_value = safe_first(filtered_df_forcolor['Number'], default=0)
        if death_value:
            text = "Solunum yolu hastalıklarına(SYH) bağlı " + str(option_slctd) + " yılı ölüm sayısı: " + str(int(death_value)) + " kişi"
        else:
            text = "Bu ülkenin ölüm verileri bulunmamaktadır."

        norm_value = safe_first(filtered_df_forcolor['NormalizationForFactValueNumeric'])
        cloud_img, cloud_bg = colorchoose(norm_value)

        style  = {'position': 'fixed', 'top': 0, 'right': 0, 'margin-top': '6.25%', 'margin-right': '5%', 'margin-bottom': '6.25%', 'margin-left': '25%', 'width': '70.5%', 'height': '75%', 'background-color': 'rgb(255,255,255,0.95)', 'z-index': '1000', 'display': 'inline-block', 'border-radius': '15px', 'box-shadow': '0 8px 16px rgba(0, 0, 0, 0.2)', 'border': '1px solid rgb(135,135,135)'}
        style2 = {'display': 'inline-block', 'background-color': cloud_bg, 'width': '18%', 'height': '75%', 'position': 'fixed', 'margin-top': '5.75%', 'margin-bottom': '6.25%', 'margin-left': '5%', 'border-radius': '15px', 'box-shadow': '0 8px 16px rgba(0, 0, 0, 0.2)', 'border': '1px solid rgb(135,135,135)'}

        return (
            style, style2, cloud_img, text,
            _histogram_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr),
            _cizgikutu_chart.figure(clicked_location, width=width, height=height, country_name_english=country_name_en),
            _cizgi_chart.figure(clicked_location, width=width, height=height, country_name=country_name_tr),
            _pasta_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr, country_name_english=country_name_en),
            _balon_chart.figure(option_slctd, clicked_location, width=width, height=height, country_name=country_name_tr),
            _gosterge_chart.figure(option_slctd, clicked_location, width=width, height=height),
            _kursun_chart.figure(clicked_location, width=width, height=height),
            {'is_hidden': 0},
        )

    return _reset


#### radar callback

@app.callback(
    [Output('hovered_location', 'style'),
     Output('gül', 'figure'),
     Output('hover-store', 'data')],
    [Input('Harita', 'hoverData'),
     Input('secilenyıl', 'value')],
    [State('viewport-store', 'data'),
     State('hover-store', 'data')],
)
def display_hover_data(hoverData, option_slctd, vp, hover_data):
    width, height = parse_viewport(vp)
    last_iso3 = (hover_data or {}).get('last_iso3', '')

    if hoverData is None:
        return {'display': 'none'}, {'data': []}, {'last_iso3': ''}

    location = hoverData['points'][0]['location']
    if location == last_iso3:
        return dash.no_update, dash.no_update, dash.no_update

    fig_dict = _radar_chart.figure(location, option_slctd, width=width, height=height)

    if fig_dict is None:
        return {'display': 'none'}, {'data': []}, {'last_iso3': ''}

    bbox = hoverData['points'][0]['bbox']
    has_data = any(
        t.get('type') == 'barpolar'
        for t in fig_dict.get('data', [])
    )
    if has_data:
        style = {
            'position': 'fixed',
            'top': str(bbox['y1'] + 10) + 'px',
            'left': str(bbox['x1'] + 10) + 'px',
            'padding': '10px',
            'background-color': 'transparent',
            'display': 'block',
            'z-index': 9999,
            'width': '20%',
            'height': '250px',
        }
    else:
        style = {
            'position': 'fixed',
            'top': str(bbox['y1'] + 10) + 'px',
            'left': str(bbox['x1'] + 10) + 'px',
            'padding': '10px',
            'border': '1px solid black',
            'background-color': 'white',
            'display': 'block',
            'z-index': 9999,
        }
    return style, fig_dict, {'last_iso3': location}


@app.callback(
    [Output('modal-info1', 'opened'),
     Output('BolgeHaritasi', 'src'),
     Output('sunburst', 'figure'),
     Output('linearea', 'figure'),
     Output('modal-info2', 'opened')],
    [Input('closeButton2', 'n_clicks'),
     Input('closeButton3', 'n_clicks'),
     Input('info_circle1', 'n_clicks'),
     Input('info_circle2', 'n_clicks')],
    [State('viewport-store', 'data')],
    prevent_initial_call=True
)
def toggle_info_div(close_clicks, close_clicks2, info_clicks, info_clicks2, vp):
    width, height = parse_viewport(vp)

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    prop_id = ctx.triggered[0]['prop_id']
    if prop_id in ('closeButton2.n_clicks', 'closeButton3.n_clicks'):
        return False, "", {'data': []}, {'data': []}, False
    elif prop_id == 'info_circle1.n_clicks':
        return (
            True,
            "assets/img/maps.png",
            _sunburst_chart.figure(width=width, height=height),
            _linearea_chart.figure(width=width, height=height),
            False,
        )
    elif prop_id == 'info_circle2.n_clicks':
        return False, "", {'data': []}, {'data': []}, True
    else:
        raise dash.exceptions.PreventUpdate


# Tarayıcı boyutunu viewport-store'a yazar (assets/js/viewport.js)
app.clientside_callback(
    ClientsideFunction(namespace='viewport', function_name='updateViewport'),
    Output('viewport-store', 'data'),
    Input('dummy-input', 'children'),
)


# Uygulamayı çalıştırma
if __name__ == '__main__':
    app.run_server(debug=True)
