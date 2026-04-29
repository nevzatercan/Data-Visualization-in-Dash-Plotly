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
    dash_table,
    dcc,
    html,
)

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True


from dashapp.data_loader import load_air, load_merged
from dashapp.transforms import colorchoose, filter_total, safe_first
from dashapp.utils.translations import to_turkish
from dashapp.layout.stores import make_stores, parse_viewport
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



####SQL 

sqlmerged_df=merged_df.copy()
sqlmerged_df = sqlmerged_df[sqlmerged_df["Dim1_y"] == "Total"]
sqlmerged_df['Year'] = sqlmerged_df['Year'].astype(int)
sutunlar_cikarilacak2 = ['Dim1_y', 'Dim1_x','Value']
sqlmerged_df = sqlmerged_df.drop(columns=sutunlar_cikarilacak2)

# Renk kodlarını ayarlama
threshold_color_map = {
    'green': '#b3eb73',
    'yellow': '#fbed71',
    'orange': '#efb35d',
    'red': '#e86c75'
}

data_style = []

# Stil ayarlarını 'Number' sütununa uygulama
column = 'Number'

if sqlmerged_df[column].dtype == 'float64' or sqlmerged_df[column].dtype == 'int64':
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 0 && {{{}}} < 10000'.format(column, column)
        },
        'backgroundColor': threshold_color_map['green'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 10000 && {{{}}} < 20000'.format(column, column)
        },
        'backgroundColor': threshold_color_map['yellow'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 20000 && {{{}}} < 50000'.format(column, column)
        },
        'backgroundColor': threshold_color_map['orange'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 50000'.format(column)
        },
        'backgroundColor': threshold_color_map['red'],
        'color': 'white'
    })

# Stil ayarlarını 'Percentage of cause-specific deaths out of total deaths' sütununa uygulama
column = 'Percentage of cause-specific deaths out of total deaths'

if sqlmerged_df[column].dtype == 'float64' or sqlmerged_df[column].dtype == 'int64':
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 0 && {{{}}} < 3'.format(column, column)
        },
        'backgroundColor': threshold_color_map['green'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 3 && {{{}}} < 6'.format(column, column)
        },
        'backgroundColor': threshold_color_map['yellow'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 6 && {{{}}} < 9'.format(column, column)
        },
        'backgroundColor': threshold_color_map['orange'],
        'color': 'white'
    })
    data_style.append({
        'if': {
            'column_id': column,
            'filter_query': '{{{}}} >= 9 && {{{}}} < 101'.format(column, column)
        },
        'backgroundColor': threshold_color_map['red'],
        'color': 'white'
    })

# Bu noktada data_style listesi hem 'Number' hem de 'Percentage of cause-specific deaths out of total deaths' sütunları için gerekli stil ayarlarını içerecek







###


# Uygulama düzeni
app.layout = html.Div([
    *make_stores(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(id='dummy-input', style={'display': 'none'}),
   
html.Div([
    html.Div([
        html.Div([
            html.Div([html.Img(src='assets/world.png',style={'width':'100%'})],id='info_circle1',style={'width':'50px','height':'50px','border-radius': '50%','background-color': 'rgba(255, 255, 255, 0.93)','border':'1px solid black','box-shadow': 'rgba(0, 0, 0, 0.35) 0px 5px 15px'}),
            html.Div([html.Img(src='assets/table.png',style={'width':'82%','margin':'9%'})],id='info_circle2',style={'width':'50px','height':'50px','border-radius': '50%','background-color': 'rgba(255, 255, 255, 0.93)','border':'1px solid black','box-shadow': 'rgba(0, 0, 0, 0.35) 0px 5px 15px'}),
            html.Div([html.Img(src='assets/media.png',style={'width':'85%','margin':'7%','margin-top':'12%'})],id='info_circle3',style={'width':'50px','height':'50px','border-radius': '50%','background-color': 'rgba(255, 255, 255, 0.93)','border':'1px solid black','box-shadow': 'rgba(0, 0, 0, 0.35) 0px 5px 15px'}),
        ], style={'display': 'flex', 'justify-content': 'space-around', 'align-items': 'center', 'height': '100%'})
    ],
    id="info_icons",
    style={'float': 'left', 'width': '30%', 'height': '100%', 'background-color': 'transparent','z-index':'9'}),
    html.Div([
        html.Div([
            dcc.Slider(
                id='secilenyıl',
                min=2010,
                max=2019,
                step=1,
                value=2010,
                marks={i: str(i) for i in range(2010, 2020)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='drag',
                className='custom-slider'
            ),
        ],
        style={'float': 'right','width': '100%','margin-top': '3%', 'left': '0px','z-index':'9'}),
    ],
    style={'float': 'left', 'width': '30%', 'height': '100%', 'background-color': 'transparent','z-index':'9'}),
    html.Div([
        html.Div(
    style={
        'width': '90%',
        'height': '60%',
        'borderRadius': '25px',
        'overflow': 'hidden',
        'position': 'relative',
        'margin-left': '5%',
        'margin-right':'5%',
        'margin-top': '2%'
    },
    children=[
        html.Div(id="yesilbuton", style={'backgroundColor': '#85e043', 'width': '25%','height':'100%','float': 'left'}),
        html.Div(id="sarıbuton", style={'backgroundColor': '#eff229', 'width': '25%','height':'100%','float': 'left'}),
        html.Div(id="turuncubutton", style={'backgroundColor': '#f2a529', 'width': '25%','height':'100%','float': 'left'}),
        html.Div(id="kırmızıbuton", style={'backgroundColor': '#d3382e', 'width': '25%','height':'100%','float': 'left'})
    ]
)
    ],
    id="infoImg",
    style={'float': 'right', 'width': '40%', 'height': '100%', 'background-color': 'transparent','z-index':'9'})
],
style={'position': 'fixed', 'bottom': '4px', 'left': '0', 'width': '100%', 'height': '10%', 'background-color': 'transparent','z-index':'9'}),



    html.Div([
        dcc.Graph(
            id='Harita',
            figure={},
            config={'displayModeBar': False},
            clear_on_unhover=True
        ),
    ],
    style={'position': 'absolute','top': '0px !important', 'left': '0px !important','overflow-y':'hidden','margin-top':'-4.6%'}),
    html.Div([
    html.Div([
        html.Img(src='', style={'width': '80%', 'height': '20%', 'margin-left': '10%', 'margin-right': '10%', 'margin-top': '10%'}, id='pm25img'),
        dcc.Graph(id='gösterge', figure={}),
        html.P(id='text2', style={'font-size': '14px', 'text-align': 'center', 'margin-top': '-30px', 'font-weight': 'bold', 'font-family': 'Arial', 'margin-left': '3%', 'margin-right': '3%'}),
        html.P("Son verilere göre: ", id='text1', style={'font-size': '20px', 'text-align': 'center', 'margin-top': '15%', 'margin-bottom': '-3%'}),
        dcc.Graph(id='kursun', figure={}),
        html.Div([
            html.Div([
                html.Img(src="assets/çizgi.png", style={'vertical-align': 'middle','width':'5%','padding-left':'3%','margin-right':'-4%'}),
                html.P(": Tüm yılların ortalama değeri ", style={'display': 'inline-block', 'margin-left': '10px', 'vertical-align': 'middle','font-size':'59%'}),

                html.Img(src="assets/çizgi2.png", style={'vertical-align': 'middle','width':'11%', 'padding-left':'7%'}),
                html.P(": Son yılın değeri", style={'display': 'inline-block', 'vertical-align': 'middle','font-size':'59%','margin-left':'1.5%'}),
            ], style={'display': 'flex', 'align-items': 'center'}),
        ]),
    ], id='side_clicked_location', style={'display': 'none'}),

        html.Div([
            html.Div(
                id="closeButton", 
                children="×",  
                style={
                    'position': 'absolute', 
                    'top': '10px', 
                    'right': '20px', 
                    'font-size': '24px', 
                    'color': 'black', 
                    'cursor': 'pointer',
                    'display':'block',
                    'z-index': '9999'
                }
            ),
html.Table([
    html.Tr([
        html.Td(dcc.Graph(id='histogram',figure={},config={'displayModeBar': False}), style={'box-shadow': '2px 2px 2px rgba(0, 0, 0, 0.1)','outline': '2px solid rgb(0,0,0,0.5)','border-top-left-radius': '12px'}, colSpan=4),
        html.Td(dcc.Graph(id='pasta',figure={},config={'displayModeBar': False}), style={'box-shadow': '2px 2px 2px rgba(0, 0, 0, 0.1)','border-top-right-radius': '12px','outline': '2px solid rgb(0,0,0,0.5)'}, colSpan=2, rowSpan=2),
    ]),
    html.Tr([
        html.Td(dcc.Graph(id='balon',figure={},config={'displayModeBar': False}), style={'box-shadow': '2px 2px 2px rgba(0, 0, 0, 0.1)','outline': '2px solid rgb(0,0,0,0.5)'}, colSpan=4),
    ]),
    html.Tr(
        html.Td(
            html.Div([
                html.Div(
                    dcc.Graph(id='cizgikutu', figure={}, config={'displayModeBar': False}),
                    style={'width': '50%', 'display': 'inline-block', 'box-shadow': '2px 2px 2px rgba(0, 0, 0, 0.1)','outline': '2px solid rgb(0,0,0,0.5)','border-bottom-left-radius': '12px','outline-offset':'1px'}
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=1*2000,  # milisaniye cinsinden güncelleme aralığı
                    n_intervals=0
                ),
                html.Div(
                    dcc.Graph(id='cizgi', figure={}, config={'displayModeBar': False}),
                    style={'width': '50%', 'display': 'inline-block', 'box-shadow': '2px 2px 2px rgba(0, 0, 0, 0.1)','outline': '2px solid rgb(0,0,0,0.5)','border-bottom-right-radius': '12px','outline-offset':'1px'}
                )
            ]),
            style={'width': '100%'}, colSpan = 6
        )
    )
])

        ],
        id='clicked_location',
        style={'display': 'none'}),
        ]),
    
    
    html.Div([
        dcc.Graph(id='gül',figure={},config={'displayModeBar': False})
    ],
    id='hovered_location',
    style={'display': 'none','width':'20%','height':'250px','background-color': 'transparent'}
    ),
    
html.Div([
    html.Div(
        id="closeButton2", 
        children="×",  
        style={
            'position': 'absolute', 
            'top': '10px', 
            'right': '20px', 
            'font-size': '24px', 
            'color': 'black', 
            'cursor': 'pointer',
            'display':'block',
            'z-index': '9999'
        }
    ),

html.Div([
    html.P("Bölgelere Göre PM2.5 Seviyeleri", style={'color':'black', 'font-size':'145%', 'margin-bottom':'2%'}),
    html.Img(src='', style={'width':'100%','margin-top':'1%','height':'69%'}, id='BolgeHaritasi'),
    html.Div([
        html.Div([
            html.P("Afrika: ", style={'display':'inline'}),
            html.Span("29.11 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','margin-right':'-11%','background-color':'#e3a96d'}),
        ],style={'margin-top':'10%','margin-bottom':'10%'}),
        html.Div([
            html.P("Batı Pasifik: ", style={'display':'inline'}),
            html.Span("17.06 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','background-color':'#bfe982'}),
        ]),
    ], style={'width': '33%', 'float': 'left','border-right':'1px solid black','height':'18%'}),
    html.Div([
        html.Div([
            html.P("Amerika: ", style={'display':'inline','margin-left':'-5%'}),
            html.Span("14.61 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','margin-right':'-24%','background-color':'#bfe982'}),
        ],style={'margin-top':'10%','margin-bottom':'10%'}),
        html.Div([
            html.P("Güneydoğu Asya: ", style={'display':'inline'}),
            html.Span("29.81 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','background-color':'#e3a96d'}),
        ]),
    ], style={'width': '33%', 'float': 'left','border-right':'1px solid black','height':'18%'}),
    html.Div([
        html.Div([
            html.P("Avrupa: ", style={'display':'inline','margin-left':'-17%',}),
            html.Span("19.22 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','margin-right':'-21%','background-color':'#ddeb83' }),
        ],style={'margin-top':'10%','margin-bottom':'10%'}),
        html.Div([
            html.P("Ortadoğu: ", style={'display':'inline'}),
            html.Span("40.89 μm", style={'border': '1px solid black', 'padding': '2px', 'margin-left': '5px','background-color':'#d97378'}),
        ]),
    ], style={'width': '33%', 'float': 'left'}),
],
id="left_div",
style={
    'height': '100%',
    'width': '64%',  # Adjusted width to account for the margin
    'float': 'left',
    'background-color': 'rgba(255, 255, 255, 0.93)',
    'border-top-left-radius': '21px',
    'border-bottom-left-radius': '21px',
    'border':'2px solid rgba(0, 0, 0, 0.73)',
    'box-sizing':'border-box',
    'margin-right': '1%',  # Add margin to the right
}
),




    html.Div([
        dcc.Graph(id='sunburst', figure={}, config={'displayModeBar': False})
        ],
        id="top_right_div",
        style={
            'height': '50%',
            'width': '34%',  # Adjusted width to account for the margin
            'float': 'left',
            'background-color': 'rgba(255, 255, 255, 0.93)',
            'margin-left': '1%',  # Add margin to the left
            'border': '2px solid rgba(0, 0, 0, 0.73)',
            'box-sizing': 'border-box',
            'border-top-right-radius': '21px',
        }
    ),

    html.Div([
        dcc.Graph(id='linearea', figure={}, config={'displayModeBar': False})
        ],
        id="bottom_right_div",
        style={
            'height': '50%',
            'width': '34%',  # Adjusted width to account for the margin
            'float': 'left',
            'background-color': 'rgba(255, 255, 255, 0.93)',
            'margin-left': '1%',  # Add margin to the left
            'border-bottom': '2px solid rgba(0, 0, 0, 0.73)',
            'border-left': '2px solid rgba(0, 0, 0, 0.73)',
            'border-right': '2px solid rgba(0, 0, 0, 0.73)',
            'box-sizing': 'border-box',
            'border-bottom-right-radius': '21px',
        }
    ),
],
id='info_div',
style={
    'position': 'absolute',
    'margin-top': '5%',
    'margin-right': '5%',
    'margin-bottom': '5%',
    'margin-left': '5%',
    'width': '90%',
    'height': '80%',

    'z-index': '1000',
    'display': 'none'
}),


html.Div([
    html.Div(
        id="closeButton3", 
        children="×",  
        style={
            'position': 'absolute', 
            'top': '10px', 
            'right': '20px', 
            'font-size': '24px', 
            'color': 'white', 
            'cursor': 'pointer',
            'display': 'block',
            'z-index': '9999'
        }
    ),
    
    html.Div([
        html.P("PM2.5 ve SOLUNUM YOLU HASTALIKLARINA BAĞLI ÖLÜM VERİLERİ TABLOSU",style={'color':'white','margin-left':'27%','font-size':'110%'}),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in sqlmerged_df.columns],
            data=sqlmerged_df.to_dict('records'),
            style_cell=dict(textAlign='left'),
            style_header=dict(backgroundColor="paleturquoise"),
            style_data=dict(backgroundColor="lavender"),
            style_data_conditional=data_style,  
            sort_action='native', 
            filter_action='native',  
            style_table={
                'overflowX': 'auto',
                'height': '100%',
                'width': '100%',
            },
        ),
        ],

        style={
            'height': '100%',  # Kapsayıcı div'in yüksekliği
            'width': '100%'    # Kapsayıcı div'in genişliği
        }
    )
],
    id='info_div2',
    style={
        'position': 'absolute',
        'margin-top': '5%',
        'margin-right': '5%',
        'margin-bottom': '5%',
        'margin-left': '5%',
        'width': '90%',
        'height': '80%',
        'background-color': 'rgba(0, 0, 0, 0.8)',
        'z-index': '1000',
        'display': 'none',
        'overflow': 'hidden',  # Taşmayı gizlemek için
        'border':'5px solid white',
        'box-sizing':'borderbox'
    }
)
])

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
        hoverinfo="none",  # Hover'da hiçbir bilgi görüntülenmeyecek
        locationmode='ISO-3',
        locations=filtered_df_air['SpatialDimValueCode'],
        z=filtered_df_air['NormalizationForFactValueNumeric'],
        colorscale=new_color_scale,
        showscale=False,
    )
    
    # Choropleth(Hava Kalitesi haritası) haritayı trace olarak atayıp ileride birleştirmek için kullanmak.
    fig.add_trace(choropleth_trace)
    
    # Scatter_geo grafiği oluşturma ve fig'e ekleme
    scatter_geo_trace = go.Scattergeo(
        hoverinfo="none",  # Hover'da hiçbir bilgi görüntülenmeyecek
        locationmode='ISO-3',
        locations=filteredmerged_df['Country Code'],
        text=filteredmerged_df['Country Name'],
        mode="markers",
        marker=dict(
            size=filteredmerged_df['Percentage of cause-specific deaths out of total deaths']*2.5,  # Marker boyutunu değerlerle belirle
            color=filteredmerged_df['NormalizationForPerDeath'],  # Marker rengi
            colorscale=new2_color_scale  # Renk skalası
        )
    )
    #Scatter(Ölüm sayıları haritası) haritayı trace olarak atayıp choropleth ile birleştirir.
    fig.add_trace(scatter_geo_trace)
    
    #Bütün haritanın özelliklerini ayarlama
    fig.update_geos(
        projection_scale=1,  # Haritanın ekranı tamamen kaplamasını sağlar
        showframe=False,
        projection_type="equirectangular",
        ##center=dict(lat=51, lon=10),
        showcountries=True,
        showocean=True,
        oceancolor="#a3d6fb",
        visible = True
    )
    #Haritanın Boyutunu ayarlama
    fig.update_layout(
        
        showlegend=False,
        autosize=False,
        width=width,
        height=height,
        margin=dict(
            l=0,  
            r=0,  
            b=0,  
            t=0,  
        ),
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

        # Output sırası: histogram, cizgikutu→Output('cizgi'), cizgi→Output('cizgikutu') — orijinal tab düzeni
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
    # Eksik veri → ağlayan yüz (beyaz arka plan + border)
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
    [Output('info_div', 'style'),
     Output('BolgeHaritasi', 'src'),
     Output('sunburst', 'figure'),
     Output('linearea', 'figure'),
     Output('info_div2', 'style')],
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
        return {'display': 'none'}, "", {'data': []}, {'data': []}, {'display': 'none'}
    elif prop_id == 'info_circle1.n_clicks':
        return (
            {'position': 'absolute', 'margin-top': '5%', 'margin-right': '5%', 'margin-bottom': '5%', 'margin-left': '5%', 'width': '90%', 'height': '80%', 'z-index': '1000', 'display': 'block', 'text-align': 'center'},
            "assets/maps.png",
            _sunburst_chart.figure(width=width, height=height),
            _linearea_chart.figure(width=width, height=height),
            {'display': 'none'},
        )
    elif prop_id == 'info_circle2.n_clicks':
        return {'display': 'none'}, "", {'data': []}, {'data': []}, {'position': 'absolute', 'margin-top': '5%', 'margin-right': '5%', 'margin-bottom': '5%', 'margin-left': '5%', 'width': '90%', 'height': '80%', 'background-color': 'rgba(0, 0, 0, 0.8)', 'z-index': '1000', 'display': 'block', 'overflow': 'scroll', 'border': '3px solid white', 'box-sizing': 'borderbox'}
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
