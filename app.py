#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 05:27:29 2024

@author: nevzatercan
"""

import pandas as pd
import plotly.express as px
from dash import Dash,dash_table, dcc, html, Input, Output
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import ClientsideFunction, Input, Output, State
import plotly.express as px
from ipywidgets import widgets

import urllib.request, json,webbrowser,requests,random
from googletrans import Translator


app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


# Veri setlerini yükleme
df_death = pd.read_csv('death.csv', header=6, on_bad_lines='skip', sep=';')
df_air = pd.read_csv('air.csv', header=0, sep=',', encoding="windows-1252")
df_covid = pd.read_csv('covid.csv', header=0, sep=',')
df_death['Percentage of cause-specific deaths out of total deaths'] = df_death['Percentage of cause-specific deaths out of total deaths'].astype(float)
df_air['FactValueNumeric'] = df_air['FactValueNumeric'].astype(float)

# Verileri düzeltilecek ülkeler
df_death.loc[df_death['Country Code'] == 'TUR', 'Region Name'] = 'Europe'
df_death.loc[df_death['Country Name'] == 'T?rkiye', 'Country Name'] = 'Türkiye'

# air'de olan, death'te olmayan ülkelerin listesi
eksik_ülkeler_cod = df_air[~df_air['SpatialDimValueCode'].isin(df_death['Country Code'])]['SpatialDimValueCode'].unique()
eksik_ülkeler_name = df_air[~df_air['Location'].isin(df_death['Country Name'])]['Location'].unique()

# Death'te olmayan ülkeleri ekleyerek eksik yılları ve değerleri doldurma
# Boş liste oluştur
eksik_veriler_cod = []

# df_air'deki ülke kodları ve isimlerinden oluşan bir sözlük oluştur
country_code_name_map = dict(zip(df_air['SpatialDimValueCode'], df_air['Location']))

for ülke_kodu in eksik_ülkeler_cod:
    # Ülke kodunu adıyla eşleştir
    ülke_adı = country_code_name_map.get(ülke_kodu, 'Unknown')

    # 2010-2019 yılları arasında eksik verileri oluştur
    for year in range(2010, 2020):
        eksik_veriler_cod.append({
            'Country Code': ülke_kodu,
            'Country Name': ülke_adı,  # Ülke adını da ekleyin
            'Year': year,
            'Dim1': 'Total',
            'Age Group': '[All]',
            'Sex': 'All',
            'Number': 0,
            'Percentage of cause-specific deaths out of total deaths': 0
        })

eksik_veriler_name = []
for ülke in eksik_ülkeler_name:  # Değişken adını eksik_ülkeler_name olarak değiştirdim.
    for year in range(2010, 2020):
        eksik_veriler_name.append({'Country Name': ülke, 'Year': year, 'Dim1': 'Total', 'Age Group': '[All]', 'Sex': 'All', 'Number': 0, 'Percentage of cause-specific deaths out of total deaths': 0})
        
# Yeni veri çerçevesini oluşturma
df_missing = pd.DataFrame(eksik_veriler_cod)
df_missing2 = pd.DataFrame(eksik_veriler_name)

# Eksik verileri df_death'ten alarak doldurma
df_death = pd.concat([df_death, df_missing], ignore_index=True)
df_death = pd.concat([df_death, df_missing2], ignore_index=True)


# 4 rakamı almak
def first_four_digits(x):
    if pd.notnull(x):
        return str(x)[:4]
    else:
        return ""
    
df_death['Percentage of cause-specific deaths out of total deaths'] = df_death['Percentage of cause-specific deaths out of total deaths'].apply(first_four_digits)
df_air['FactValueNumeric'] = df_air['FactValueNumeric'].apply(first_four_digits)

# df leri birleştirme
merged_df = pd.merge(df_death, df_air, left_on=['Country Code', 'Year'], right_on=['SpatialDimValueCode',  'Period'], how='inner')
# merged_df.fillna(0, inplace=True)
# merged_df['Percentage of cause-specific deaths out of total deaths'] = merged_df['Percentage of cause-specific deaths out of total deaths'].replace('', '0').astype(float)
# merged_df['FactValueNumeric'] = merged_df['FactValueNumeric'].replace('', '0').astype(float)

# merged_df['Percentage of cause-specific deaths out of total deaths'] = merged_df['Percentage of cause-specific deaths out of total deaths'].astype(float)
# merged_df['FactValueNumeric'] = merged_df['FactValueNumeric'].astype(float)

# Boş veya geçersiz değerleri temizleme
df_air.dropna(subset=['FactValueNumeric'], inplace=True)
merged_df.dropna(subset=['Percentage of cause-specific deaths out of total deaths'], inplace=True)
merged_df.dropna(subset=['FactValueNumeric'], inplace=True)

# String değerleri sayısal değerlere dönüştürme
merged_df['Percentage of cause-specific deaths out of total deaths'] = pd.to_numeric(merged_df['Percentage of cause-specific deaths out of total deaths'], errors='coerce')
merged_df['FactValueNumeric'] = pd.to_numeric(merged_df['FactValueNumeric'], errors='coerce')
df_air = df_air[pd.to_numeric(df_air['FactValueNumeric'], errors='coerce').notna()]
df_air['FactValueNumeric'] = pd.to_numeric(df_air['FactValueNumeric'], errors='coerce')


# Gereksiz Veri Temizleme
sutunlar_cikarilacak = ['IndicatorCode', 'ValueType', 'Location type', 'Period type', 'IsLatestYear', 'Dim1 type', 'Dim1ValueCode', 'Dim2 type', 'Dim2', 'Dim2ValueCode', 'Dim3', 'DataSourceDimValueCode', 'Dim3ValueCode', 'DataSource', 'FactValueUoM', 'FactValueNumericLowPrefix', 'FactValueNumericHighPrefix', 'FactValueTranslationID', 'FactComments', 'Language', 'DateModified','Dim3 type','Indicator','ParentLocationCode','ParentLocation','SpatialDimValueCode','Location','Period','FactValueNumericPrefix']
merged_df = merged_df.drop(columns=sutunlar_cikarilacak)
merged_df = merged_df[~merged_df['Age Group'].isin(['[Unknown]'])]

# Number sütununu normalleştirme
merged_df['NormalizationForNumber'] = (merged_df['Number'] - merged_df['Number'].min()) / (merged_df['Number'].max() - merged_df['Number'].min())

# Percentage of cause-specific deaths out of total deaths sütununu normalleştirme
merged_df['NormalizationForPerDeath'] = (merged_df['Percentage of cause-specific deaths out of total deaths'] - merged_df['Percentage of cause-specific deaths out of total deaths'].min()) / (merged_df['Percentage of cause-specific deaths out of total deaths'].max() - merged_df['Percentage of cause-specific deaths out of total deaths'].min())

# Age-standardized death rate per 100 000 standard population sütununu normalleştirme
merged_df['NormalizationForAgeStandardizedDeathRate'] = (merged_df['Age-standardized death rate per 100 000 standard population'] - merged_df['Age-standardized death rate per 100 000 standard population'].min()) / (merged_df['Age-standardized death rate per 100 000 standard population'].max() - merged_df['Age-standardized death rate per 100 000 standard population'].min())

# FactValueNumericLow sütununu normalleştirme
merged_df['NormalizationForFactValueNumericLow'] = (merged_df['FactValueNumericLow'] - merged_df['FactValueNumericLow'].min()) / (merged_df['FactValueNumericLow'].max() - merged_df['FactValueNumericLow'].min())

# FactValueNumericHigh sütununu normalleştirme
merged_df['NormalizationForFactValueNumericHigh'] = (merged_df['FactValueNumericHigh'] - merged_df['FactValueNumericHigh'].min()) / (merged_df['FactValueNumericHigh'].max() - merged_df['FactValueNumericHigh'].min())

# FactValueNumeric sütununu normalleştirme
merged_df['NormalizationForFactValueNumeric'] = (merged_df['FactValueNumeric'] - merged_df['FactValueNumeric'].min()) / (merged_df['FactValueNumeric'].max() - merged_df['FactValueNumeric'].min())

# FactValueNumeric ama df air için normalize etme 
df_air['NormalizationForFactValueNumeric'] = (df_air['FactValueNumeric'] - df_air['FactValueNumeric'].min()) / (df_air['FactValueNumeric'].max() - df_air['FactValueNumeric'].min())

# Yaş ve Cinsiyete Göre df oluşturma
sexallexitmerged_df = merged_df.copy()
sexallexitmerged_df = merged_df[~merged_df['Sex'].isin(['Unknown', 'All'])]
sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[0]', 'Age Group'] = '[0-49]'

# 50 yaş ve öncesini tek grupta toplamak için yapılması gereken işlemler
sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[0-49]', 'NormalizationForPerDeath'] = (sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[0-49]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[1-4]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[5-9]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[10-14]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[15-19]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[20-24]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[25-29]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[30-34]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[35-39]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[40-44]', 'NormalizationForPerDeath'].values + \
    sexallexitmerged_df.loc[sexallexitmerged_df['Age Group'] == '[45-49]', 'NormalizationForPerDeath'].values ) /10

sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[1-4]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[5-9]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[10-14]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[15-19]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[20-24]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[25-29]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[30-34]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[35-39]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[40-44]'].index)
sexallexitmerged_df = sexallexitmerged_df.drop(sexallexitmerged_df[sexallexitmerged_df['Age Group'] == '[45-49]'].index)

# Age için sonrasında filtrelemede gerekli kısımlar
age_group_unique = sexallexitmerged_df['Age Group'].unique()
age_group_unique = np.roll(age_group_unique, -1)  # Diziyi bir birim sola kaydırır
age_sex_group_averages = sexallexitmerged_df.groupby(['Age Group', 'Sex'])['NormalizationForPerDeath'].mean()

# RadarWorld dizilerini oluşturma
RadarWorld = np.empty(5)
RadarWorldForCountry = np.zeros(5)

# RadarWorld sütunlarının ortalamasını almak (Tek Sefer Yeterli)
RadarWorld[0] = merged_df['NormalizationForNumber'].mean() * 10
RadarWorld[1] = merged_df['NormalizationForPerDeath'].mean()
RadarWorld[2] = merged_df['NormalizationForAgeStandardizedDeathRate'].mean()
RadarWorld[3] = merged_df['NormalizationForFactValueNumericLow'].mean()
RadarWorld[4] = merged_df['NormalizationForFactValueNumericHigh'].mean()

############ all cities mean 
cities_meanworld = merged_df[(merged_df['Dim1_y'] == 'Cities') & (merged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
rural_meanworld = merged_df[(merged_df['Dim1_y'] == 'Rural') & (merged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
towns_meanworld = merged_df[(merged_df['Dim1_y'] == 'Towns') & (merged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
urban_meanworld = merged_df[(merged_df['Dim1_y'] == 'Urban') & (merged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
total_meanworld = merged_df[(merged_df['Dim1_y'] == 'Total') & (merged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
all_meansworld = [cities_meanworld, towns_meanworld, urban_meanworld, rural_meanworld]



####SQL 

sqlmerged_df=merged_df.copy()
sqlmerged_df = sqlmerged_df[sqlmerged_df["Dim1_y"] == "Total"]
sqlmerged_df['Year'] = sqlmerged_df['Year'].astype(int)
sutunlar_cikarilacak2 = ['Dim1_y', 'Dim1_x','Value']
sqlmerged_df = sqlmerged_df.drop(columns=sutunlar_cikarilacak2)

# Renk kodlarını ayarlama
threshold_color_map = {
    'green': '#00FF00',  # Yeşil
    'red': '#FF0000'      # Kırmızı
}

# Hücrelerin içindeki sayıya göre renk ayarları
data_style = []
for column in sqlmerged_df.columns:
    if sqlmerged_df[column].dtype == 'float64' or sqlmerged_df[column].dtype == 'int64':
        data_style.append({
            'if': {'column_id': column, 'filter_query': '{{{}}} >= 20'.format(column)},
            'backgroundColor': threshold_color_map['green'],
            'color': 'white'
        })
        data_style.append({
            'if': {'column_id': column, 'filter_query': '{{{}}} < 20'.format(column)},
            'backgroundColor': threshold_color_map['red'],
            'color': 'white'
        })


######ülke isimlerini türkçe alma

translator = Translator()

# Türkçe'ye çevirme fonksiyonu
def translate_to_turkish(text):
    translation = translator.translate(text, src='en', dest='tr')
    return translation.text


###


# Uygulama düzeni
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(id='browser-info', style={'display': 'none'}),
    html.Div(id='dummy-input', style={'display': 'none'}),
    html.P(id='display-browser-info', style={'display': 'none'}),
   
html.Div([
    html.Div([
        html.Div([
            html.Div(id='info_circle1',style={'width':'50px','height':'50px','border-radius': '50%','background-color': '#007bff'}),
            html.Div(id='info_circle2',style={'width':'50px','height':'50px','border-radius': '50%','background-color': '#007bff'}),
            html.Div(id='info_circle3',style={'width':'50px','height':'50px','border-radius': '50%','background-color': '#007bff'}),
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
        html.Div([html.Img(src='',style={'width':'80%','height':'20%','margin-left':'10%','margin-right':'10%','margin-top':'10%'},id = 'pm25img'),
                  dcc.Graph(id ='gösterge',figure={}),
                  html.P(id='text2',style={'font-size':'14px','text-align':'center','margin-top':'-30px','font-weight': 'bold', 'font-family': 'Arial','margin-left': '3%', 'margin-right': '3%'}),
                  html.P("Son verilere göre: ",id='text1',style={'font-size':'20px','text-align':'center','margin-top': '15%','margin-bottom': '-3%'}),
                  dcc.Graph(id ='kursun',figure={})
                  ],id='side_clicked_location',style={'display':'none'}),
        html.Div([
            html.Div(
                id="closeButton", 
                children="&times;",  
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
        children="&times;",  
        style={
            'position': 'absolute', 
            'top': '10px', 
            'right': '20px', 
            'font-size': '24px', 
            'color': 'white', 
            'cursor': 'pointer',
            'display':'block',
            'z-index': '9999'
        }
    ),

    html.Div([
        html.Img(src='',style={'width':'100%','margin-top':'12%'},id = 'BolgeHaritasi'),
        ],
        id="left_div",
        style={
            'height': '100%',
            'width': '65%',
            'float': 'left',
            'background-color': 'rgba(255, 255, 255, 0.1)'  # Örnek arkaplan rengi
        }
    ),

    html.Div([
        dcc.Graph(id='sunburst',figure={},config={'displayModeBar': False})
        ],
        id="top_right_div",
        style={
            'height': '50%',
            'width': '35%',
            'float': 'left',
            'background-color': 'rgba(255, 255, 255, 0.2)'  # Örnek arkaplan rengi
        }
    ),

    html.Div([
        dcc.Graph(id='linearea',figure={},config={'displayModeBar': False})
        ],
        id="bottom_right_div",
        style={
            'height': '50%',
            'width': '35%',
            'float': 'left',
            'background-color': 'rgba(255, 255, 255, 0.3)'  # Örnek arkaplan rengi
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
    'background-color': 'rgba(0, 0, 0, 0.8)',
    'z-index': '1000',
    'display': 'none'
}),

html.Div([
    html.Div(
        id="closeButton3", 
        children="&times;",  
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
    
    html.Div(
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
                'width': '100%'
            },
        ),
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
        'overflow': 'hidden'  # Taşmayı gizlemek için
    }
)
])

# Yükseklik Genişlik default tanımlama,Global değişken olarak kullanabilmek için yapıldı.JS ile tarayıcı boyutu alınıyor ve harita ölçeklendirmede kullanılıyor.
width = 1300
height = 800
isFiltered = 0
# Map haritasının güncelleme callback'i
@app.callback(
    Output('Harita', 'figure'),
    [Input('secilenyıl', 'value'),
     Input('yesilbuton', 'n_clicks'),
     Input('sarıbuton', 'n_clicks'),
     Input('turuncubutton', 'n_clicks'),
     Input('kırmızıbuton', 'n_clicks')
     ]
)
#Haritayı oluşturma
def update_maps(option_slctd,greenButton_clicks,yellowButton_clicks,orangeButton_clicks,redButton_clicks):
    global width, height, isFiltered
    
    ctx = dash.callback_context
    # if not ctx.triggered:
    #     raise dash.exceptions.PreventUpdate
        
    
    #Choropleth haritası için verileri ayarlamak
    filtered_df_air = df_air.copy()
    filtered_df_air = filtered_df_air[filtered_df_air["Dim1"] == 'Total']
    filtered_df_air = filtered_df_air[filtered_df_air["Period"] == option_slctd]
    filtered_df_air_copy = filtered_df_air.copy()
    
    #Scatter haritası için verileri ayarlamak
    filteredmerged_df = merged_df.copy()
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Age Group'] == '[All]']
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Dim1_y'] == 'Total']
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Sex'] == 'All']
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Year'] == option_slctd]
    
    #Choropleth Haritası Renk Skalası
    new_color_scale = [
        (0, '#b3eb73'),
        (0.33, '#fbed71'),
        (0.45, '#efb35d'),
        (1, '#e86c75')     
    ]    
    
    #Scatter Haritası Renk Skalası
    new2_color_scale = [
        (0, 'red'),   
        (0.5, 'red'), 
        (1, 'red')  
    ]
    
    prop_id = ctx.triggered[0]['prop_id']
    if prop_id == 'yesilbuton.n_clicks':
        if isFiltered != 1:
            filtered_df_air = filtered_df_air[filtered_df_air["FactValueNumeric"] <= 18]
            new_color_scale = [
                (0, '#b3eb73'),
                (1, '#b3eb73')     
            ]  
            isFiltered = 1
        else:
            filtered_df_air = filtered_df_air_copy
            isFiltered = 0
            new_color_scale = [
                (0, '#b3eb73'),
                (0.33, '#fbed71'),
                (0.66, '#efb35d'),
                (1, '#e86c75')     
            ] 
    elif prop_id == 'sarıbuton.n_clicks':
        if isFiltered != 2:
            filtered_df_air = filtered_df_air[(filtered_df_air["FactValueNumeric"] > 18) & (filtered_df_air["FactValueNumeric"] <= 31)]
            isFiltered = 2
            new_color_scale = [
                (0, '#fbed71'),
                (1, '#fbed71')     
            ] 
        else:
            filtered_df_air = filtered_df_air_copy
            isFiltered = 0
            new_color_scale = [
                (0, '#b3eb73'),
                (0.33, '#fbed71'),
                (0.66, '#efb35d'),
                (1, '#e86c75')     
            ] 
    elif prop_id == 'turuncubutton.n_clicks':
        if isFiltered != 3:
           filtered_df_air = filtered_df_air[(filtered_df_air["FactValueNumeric"] > 31) & (filtered_df_air["FactValueNumeric"] <= 48)]
           isFiltered = 3
           new_color_scale = [
                (0, '#efb35d'),
                (1, '#efb35d')     
            ] 
        else:
            filtered_df_air = filtered_df_air_copy
            isFiltered = 0
            new_color_scale = [
                (0, '#b3eb73'),
                (0.33, '#fbed71'),
                (0.66, '#efb35d'),
                (1, '#e86c75')     
            ] 
    elif prop_id == 'kırmızıbuton.n_clicks':
        if isFiltered != 4:
            filtered_df_air = filtered_df_air[filtered_df_air["FactValueNumeric"] > 48]
            isFiltered = 4
            new_color_scale = [
                (0, '#e86c75'),
                (1, '#e86c75')     
            ] 
        else:
            filtered_df_air = filtered_df_air_copy
            isFiltered = 0
            new_color_scale = [
                (0, '#b3eb73'),
                (0.33, '#fbed71'),
                (0.66, '#efb35d'),
                (1, '#e86c75')     
            ] 
    
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


    return fig



isHidden = 1
country_name=""
country_name_english=""
cloudcolor=[]

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
     Output('kursun', 'figure')],  
    [Input('Harita', 'clickData'),
     Input('closeButton', 'n_clicks')],
    [State('secilenyıl', 'value')],
)

def display_click_data(clickData, n_clicks, option_slctd):
    global isHidden,country_name,color,country_name_english
    if n_clicks and isHidden == 0:
        hide = {'display': 'none'}
        isHidden = 1
        clickData = None
        return hide,hide,"","", {'data': []} ,{'data': []} ,{'data': []},{'data': []} ,{'data': []} ,{'data': []},{'data': []}      # Boş bir figür döndür
    if clickData is not None:
        isHidden = 0  # clicked_location görünür hale gelir
        # Üzerine gelinen veriyi alma
        clicked_location = clickData['points'][0]['location']  
        #ülke ismi alma
        country_name = merged_df[merged_df['Country Code']==clicked_location]["Country Name"].unique()[0]
        country_name_english=country_name
        country_name = translate_to_turkish(country_name)
        if ' ' in country_name:
            country_name = country_name.split(' ')[0]
        #color parametre
        filtered_df_forcolor = merged_df.copy()
        filtered_df_forcolor = merged_df[(merged_df['Country Code'] == clicked_location) & 
                                                (merged_df['Year'] == option_slctd) & 
                                                (merged_df['Age Group'] == '[All]') &
                                                (merged_df['Sex'] == 'All') &
                                                (merged_df['Dim1_y'] == 'Total')
                                                ]
        death_number = filtered_df_forcolor['Number']
        text = ""
        if death_number.values[0] != 0:
            text = "Solunum yolu hastalıklarına(SYH) bağlı "+ str(option_slctd) +" yılı ölüm sayısı: " + str(int(death_number.values[0])) + " kişi"
        else:
            text = "Bu ülkenin ölüm verileri bulunmamaktadır."
        cloudcolor=colorchoose(filtered_df_forcolor["NormalizationForFactValueNumeric"])
        # Bilgi penceresinde görüntülenecek içeriği hazırlama
        style = {'position': 'fixed', 'top': 0, 'right': 0, 'margin-top': '6.25%', 'margin-right': '5%', 'margin-bottom': '6.25%', 'margin-left': '25%', 'width': '70.5%', 'height': '75%', 'background-color': 'rgb(255,255,255,0.95)', 'z-index': '1000', 'display': 'inline-block', 'border-radius': '15px','box-shadow': '0 8px 16px rgba(0, 0, 0, 0.2)','border': '1px solid rgb(135,135,135)'}
        style2 = {'display':'inline-block', 'background-color': cloudcolor.values[0][1],'width': '18%','height': '75%','position': 'fixed','margin-top': '5.75%','margin-bottom': '6.25%','margin-left': '5%','border-radius': '15px','box-shadow': '0 8px 16px rgba(0, 0, 0, 0.2)','border': '1px solid rgb(135,135,135)'}
        ### Oluşturduğumuz graphları callback kullanarak htmll kısmına gönderme.
        fig = histogram(option_slctd, clicked_location)
        fig2 = cizgikutu(clicked_location)
        fig3 = cizgi(clicked_location)
        fig4 = pasta(option_slctd, clicked_location)
        fig5 = balon(option_slctd, clicked_location)
        göstergefig = gösterge(option_slctd,clicked_location)
        kursunfig = kursun(clicked_location)
        return style, style2,cloudcolor.values[0][0],text, fig, fig2, fig3, fig4, fig5, göstergefig, kursunfig
    else:
        return {'display': 'none'},{'display': 'none'},"","", {'data': []},{'data': []} ,{'data': []},{'data': []} ,{'data': []} ,{'data': []}  ,{'data': []}      # Eğer clickData yoksa, clicked_location gizlenir ve boş bir figür döndür
    
def colorchoose(NormalizationForFactValueNumeric):
    def assign_color(value):
        if value < 0.13:
            return 'assets/yesil.png','rgb(218, 255, 219, 1)'
        elif 0.13 <= value < 0.44:
            return 'assets/sari.png','rgb(255, 248, 189, 1)'
        else:
            return 'assets/kirmizi.png','rgb(255, 218, 202, 1)'

    return NormalizationForFactValueNumeric.apply(assign_color)

    

### histogram chart for sex and age

def histogram(option_slctd,clickData):
    global width, height  #grafiği ölçeklendirmek için tarayıcı yükseklik ve genişliği kullanılır
    # Verilerimizi filtreleme
    filteredmerged_df = sexallexitmerged_df.copy()
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Year'] == option_slctd]
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Country Code']==clickData]
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Dim1_y']=='Total']
    filteredmerged_df = filteredmerged_df[~filteredmerged_df['Sex'].isin(['Unknown', 'All'])] 
    filteredmerged_df.loc[filteredmerged_df['Age Group'] == '[0]', 'Age Group'] = '[0-49]'
    
    age_group_unique[9] = 'Genel'
     
    # Yaş ve Cinsiyete göre gruplama
    age_sex_group_averagesall = filteredmerged_df.groupby(['Age Group', 'Sex'])['NormalizationForPerDeath'].mean()
    
    # age_sex_group_averages serisini DataFrame'e dönüştürme
    age_sex_group_averages_df = age_sex_group_averages.reset_index()
    
    # Cinsiyete göre gruplama
    male_averages = age_sex_group_averages_df[age_sex_group_averages_df['Sex'] == 'Male']
    female_averages = age_sex_group_averages_df[age_sex_group_averages_df['Sex'] == 'Female']
    
    # age_sex_group_averagesall serisini DataFrame'e dönüştürme
    age_sex_group_averagesall_df = age_sex_group_averagesall.reset_index()
    
    # Cinsiyete göre gruplama
    male_averages_all = age_sex_group_averagesall_df[age_sex_group_averagesall_df['Sex'] == 'Male']
    female_averages_all = age_sex_group_averagesall_df[age_sex_group_averagesall_df['Sex'] == 'Female']
    
    # Değerleri listeye alma
    male_averages_values = [float(value) for value in male_averages['NormalizationForPerDeath']]
    female_averages_values = [float(value) for value in female_averages['NormalizationForPerDeath']]
    male_averages_all_values = [float(value) for value in male_averages_all['NormalizationForPerDeath']]
    female_averages_all_values = [float(value) for value in female_averages_all['NormalizationForPerDeath']]

    # Figure oluşturma
    fig = go.Figure()
    #Traceler ile histogramlara kolonları ekleme veya bar oluşturma da diyebiliriz
    fig.add_trace(go.Bar(x=age_group_unique, y=male_averages_all_values, name= country_name +' Erkek Ortalaması', marker=dict(color='rgba(60, 162, 229, 0.96)')))
    fig.add_trace(go.Bar(x=age_group_unique, y=female_averages_all_values, name=country_name+ ' Kadın Ortalaması', marker=dict(color='rgba(234, 62, 62, 0.96)')))
    fig.add_trace(go.Bar(x=age_group_unique, y=male_averages_values, name='Dünya Erkek Ortalaması', marker=dict(color='rgba(50, 136, 193, 0.96)')))
    fig.add_trace(go.Bar(x=age_group_unique, y=female_averages_values, name='Dünya Kadın Ortalaması', marker=dict(color='rgba(193, 50, 50, 0.96)')))
    
    # Grafik düzenini ayarla
    fig.update_layout(
        title='Yaş Gruplarına Göre Cinsiyet Bazında ve Dünya Genelinde Ölüm Oranı', 
        titlefont=dict(color='black'),
        xaxis=dict(title='Yaş Grupları', tickfont=dict(color='black',size=10), titlefont=dict(color='black')),  # x ekseninin rengi siyah
        yaxis=dict(title='Ölüm Oranı', tickfont=dict(color='black'),titlefont=dict(color='black')),  # y ekseninin rengi siyah
        xaxis_tickangle=0, 
        barmode='group',
        width=width*0.46,
        height=height*0.2475,
        plot_bgcolor='rgba(0,0,0,0)',  # çubukların arka plan rengi
        paper_bgcolor='rgba(0,0,0,0)',  # kağıt arka plan rengi
        legend=dict(
            font=dict(color='black')) ,
        margin=dict(l=0, r=0, t=40, b=0),
        
    )

    return fig.to_dict()
        
def cizgikutu(clickData):
    global width, height, country_name_english
    filtered_df_fordeathcountry = merged_df.copy()
    filtered_df_fordeathcountry = merged_df[(merged_df['Country Code'] == clickData) & 
                                            (merged_df['Year'] >= 2010) & 
                                            (merged_df['Age Group'] == '[All]') &
                                            (merged_df['Sex'] == 'All') &
                                            (merged_df['Dim1_y'] == 'Total')
                                            ]

    # Sort the DataFrame by year
    filtered_df_fordeathcountry = filtered_df_fordeathcountry.sort_values(by='Year', ascending=True)

    # Calculate cumulative sum of 'Number' column
    filtered_df_fordeathcountry['Cumulative Deaths'] = filtered_df_fordeathcountry['Number'].cumsum()

    country_numbers = df_covid[df_covid['Name'] == country_name_english]['Deaths - cumulative total']
    country_numbers = country_numbers.astype(int)
    if country_numbers.empty:
        country_numbers = pd.Series([0]).append(country_numbers, ignore_index=True)


    first_matching_year = None 

    for year in range(2010, 2020):
        # Belirli bir yılın verilerini al
        filtered_year_data = filtered_df_fordeathcountry[filtered_df_fordeathcountry['Year'] == year]

        # Eğer belirli bir yılın verisi yoksa veya sıfır ise, devam et
        if filtered_year_data.empty:
            continue
        
        # Japan'ın toplam ölüm sayısını geçen ilk yılı bul
        if filtered_year_data['Cumulative Deaths'].values[0] > country_numbers.values[0]:
            first_matching_year = year-2010
            break  # İlk geçen yılı bulduktan sonra döngüden çık

    titletext = ""
    if first_matching_year == None:
        titletext = "Toplam Covid ölümüne yetişemedi."
    elif first_matching_year == 0:
        titletext = "Toplam Covid ölümüne 1 yılda yetişti."
    else:
        titletext = "Toplam Covid ölümüne "+ str(first_matching_year) + " yılda yetişti."


            # Plot the cumulative deaths
    fig = go.Figure()
    
    # Mavi alanı ekleyelim
    fig.add_trace(go.Scatter(x=filtered_df_fordeathcountry['Year'], 
                             y=filtered_df_fordeathcountry['Cumulative Deaths'], 
                             fill='tozeroy', 
                             mode='lines',
                             fillcolor='blue',  # Mavi renk kullanalım
                             line=dict(color='blue')))  # Çizgi rengini de mavi olarak ayarlayalım
    
        # Kırmızı alanı ekleyelim
    fig.add_trace(go.Scatter(x=filtered_df_fordeathcountry['Year'], 
                             y=[country_numbers.values[0]] * len(filtered_df_fordeathcountry),
                             mode='lines', 
                             fill='tozeroy', 
                             fillcolor='rgba(255, 0, 0, 0.7)',  # Kırmızı renk kullanalım
                             line=dict(color='rgba(255, 0, 0, 0.7)', width=0),  # Çizgi rengini ve kalınlığını ayarlayalım
                             marker=dict(color='red', size=10), 
                             showlegend=False))

    
    fig.update_layout(
        xaxis_title='Yıl',
        yaxis_title='Kümülatif Ölüm Sayısı',
        xaxis_tickangle=-45,
        xaxis_range=[filtered_df_fordeathcountry['Year'].min(), filtered_df_fordeathcountry['Year'].max()],
        showlegend=False,
        title_text = titletext,
        width=width*0.35,
        height=height*0.24,
        margin=dict(l=0, r=15, t=25, b=10),
        xaxis=dict(
            showgrid=False,
            linecolor='black',
            linewidth=2.5,
            tickfont=dict(color='black')  # x ekseninin yazılarını siyah renkte yap
        ),
        yaxis=dict(
            showgrid=False,
            linecolor='black',
            linewidth=2.5,
            tickfont=dict(color='black')  # y ekseninin yazılarını siyah renkte yap
        ),
        annotations=[
            dict(
                text="Covid 19 Kümülatif Ölüm Sayısı",
                x=filtered_df_fordeathcountry['Year'].median(),  
                y=country_numbers.median() * 0.3,
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(
                    color="black",  
                    size=14  
                )
            )
        ],
    
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig.to_dict()



def cizgi(clickData):
    global width, height
    #Verilerimizi grafiğe göre filtreleme
    filtered_df_fordeathcountry = merged_df.copy()
    filtered_df_fordeathcountry = merged_df[(merged_df['Country Code'] == clickData) & 
                                            (merged_df['Year'] >= 2010) & 
                                            (merged_df['Age Group'] == '[All]') &
                                            (merged_df['Sex'] == 'All') &
                                            (merged_df['Dim1_y'] == 'Total')
                                            ]
    #Yıla göre sıralı olarak düzenleme
    filtered_df_fordeathcountry = filtered_df_fordeathcountry.sort_values(by='Year', ascending=True)
    
    #frame oluşturma
    years = []
    deaths = []
    air_quality = []


    # Belirli bir aralıktaki yılları tek tek atama
    for i in range(2010, 2020):  # 2010'dan 2019'a kadar olan yılları kapsar
        years.append(filtered_df_fordeathcountry[filtered_df_fordeathcountry['Year'] == i]['Year'].iloc[0])
        deaths.append(filtered_df_fordeathcountry[filtered_df_fordeathcountry['Year'] == i]['NormalizationForPerDeath'].iloc[0])
        air_quality.append(filtered_df_fordeathcountry[filtered_df_fordeathcountry['Year'] == i]['NormalizationForFactValueNumeric'].iloc[0])


    #grafiği oluşturma 
    fig = go.Figure(        
        frames=[go.Frame(
            data=[
                go.Scatter(
                    x=years[:i+1],
                    y=deaths[:i+1],
                    mode='lines+markers',
                    name='Ölüm Sayıları'
                ),
                go.Scatter(
                    x=years[:i+1],
                    y=air_quality[:i+1],
                    mode='lines+markers',
                    name='PM2.5 seviyesi'
                )
            ]
        ) for i in range(len(years))])
    # Ölüm sayıları scatter plotunu ekle
    fig.add_trace(go.Scatter(x=[years[0]],
                             y=[deaths[0]],
                             mode='lines+markers', 
                             name='Ölüm Oranı'))

    # Hava kalitesi scatter plotunu ekle
    fig.add_trace(go.Scatter(x=[years[0]],
                             y=[air_quality[0]],
                             mode='lines+markers', 
                             name='PM2.5 seviyesi'))

    # Layout ayarları
    fig.update_layout(
    xaxis_title= country_name +' için 2010 sonrası pm2.5 seviyesi ve ölüm oranı',
    xaxis_title_font=dict(
    color='black'),
    yaxis_title='Normalize edilmiş veri',
    yaxis_title_font=dict(
        size=13,
        color='black',
        family='Arial'
    ),
    xaxis_tickangle=-45,
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=False,
        linecolor='black',
        linewidth=2.5,
        tickfont=dict(color='black')  # x ekseninin yazılarını siyah renkte yap
    ),
    yaxis=dict(
        showgrid=False,
        linecolor='black',
        linewidth=2.5,
        tickfont=dict(color='black')  # y ekseninin yazılarını siyah renkte yap
    ),
    width=width*0.35,
    height=height*0.24,
    margin=dict(l=0, r=0, t=0, b=10),
)
    fig.update_layout(updatemenus=[{'buttons': [{'args': [None],
                                                 'label': 'Play',
                                                 'method': 'animate'},],
                                    'direction': 'left',
                                    'pad': {'r': 0, 't': 0},
                                    'showactive': False,
                                    'bordercolor': 'red' ,
                                    'type': 'buttons',
                                    'x': 1.35,
                                    'xanchor': 'right',
                                    'y': 0.6,
                                    'yanchor': 'top'}])

    return fig.to_dict()

def pasta(option_slctd,clickData):
    global width, height
    #Verileri oluşturma ve seçme
    filteredmerged_df = merged_df.copy()
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Year'] == option_slctd]
    filteredmerged_df = filteredmerged_df[filteredmerged_df['Country Code']==clickData]
    
    def get_flag_image(country_name):
        response = requests.get(f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:Flag_of_{country_name}.svg&prop=imageinfo&iiprop=url&format=json")
        data = response.json()
        pages = data["query"]["pages"]
        if "-1" not in pages:
            image_url = pages[list(pages.keys())[0]]["imageinfo"][0]["url"]
            return image_url
        else:
            return None
            
    flag_image_url = get_flag_image(country_name_english)
    
    img_width = 0.22
    img_height = 0.200
    
    #pie chartta kullanılacak veriler için verilerin ortalamasını oluşturma
    labels = ['Şehir', 'Kasaba', 'Kentsel','Kırsal']
    filteredmerged_df['FactValueNumeric'] = pd.to_numeric(filteredmerged_df['FactValueNumeric'], errors='coerce')
    cities_mean = filteredmerged_df[(filteredmerged_df['Dim1_y'] == 'Cities') & (filteredmerged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
    rural_mean = filteredmerged_df[(filteredmerged_df['Dim1_y'] == 'Rural') & (filteredmerged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
    towns_mean = filteredmerged_df[(filteredmerged_df['Dim1_y'] == 'Towns') & (filteredmerged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()
    urban_mean = filteredmerged_df[(filteredmerged_df['Dim1_y'] == 'Urban') & (filteredmerged_df['Age group code'] == 'Age_all')]['FactValueNumeric'].mean()

    all_means = [cities_mean, towns_mean, urban_mean,rural_mean]
    formatted_values = ['{:.2f}'.format(value) for value in all_meansworld]
    formatted_values2 = ['{:.2f}'.format(value) for value in all_means]

    colors = ['#ffd166', '#ef476f', '#26547c', '#06d6a0']
    colors2 = ['#ffcc58cc', '#ec6564cc', '#3e80bfcc', '#a2d9cb']
    #Grafiği oluşturma
    # Dıştaki pasta grafiği
    outer_pie = go.Pie(
        labels=labels,
        values=formatted_values,
        textinfo='value',
        name='Outer Pie',
        hole=0.2, # İçteki pastanın boyutunu ayarlar, 0'dan 1'e kadar bir değer
        marker=dict(colors=colors,line=dict(width=7,color="white")),
        domain={'x':[0.3,0.9], 'y':[0.1,0.9]},  # x değerlerini değiştirerek pasta grafiğini sağa kaydırın
    )
    
    # İçteki pasta grafiği
    inner_pie = go.Pie(
        labels=labels,
        values=formatted_values2,
        name='Inner Pie',
        textinfo='value',
        hole=0.8, # Daha küçük bir değer seçebilirsiniz
        marker=dict(colors=colors2,line=dict(width=7,color="white")),
        domain={'x':[0.2,1], 'y':[0,1]}  # x değerlerini değiştirerek pasta grafiğini sağa kaydırın
    )

    
    
    layout = go.Layout()
    fig = go.Figure(data=[outer_pie, inner_pie], layout=layout)
    
    
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        # Pie Chartın ortasına boşluk ekleme
        annotations=[
            dict(
                text = '<span style="color:black">' + str(country_name) + ' ve Dünyanın<br>yerleşim bölgelerine göre  <br>pm2.5 ortalaması</span> <br><span style="font-size:16; color:black">' ,
                x=1.1, y=0.95,
                font_size=16,
                showarrow=False
            )
        ],
        width = width * 0.23,
        height = height * 0.495,
        legend=dict(y=0.5),font=dict(color='black')
    )

    
    fig.add_layout_image(
        dict(
            source=flag_image_url,
            xref="paper", yref="paper",
            x=0.74, y=0.455,
            sizex=img_width, sizey=img_height,
            layer = "below",
            xanchor="right", yanchor="bottom", sizing= "contain",
        ),


        )

    return fig.to_dict()

def balon(option_slctd,clickData):
    global width, height
    #verilerimizi filtrelemeyi 2farklı df kulanarak oluşturma
    selected_country = clickData
    filtered_merged_df = df_air.copy()
    filtered_merged_df = filtered_merged_df[filtered_merged_df['Period'] == option_slctd]
    filtered_merged_df = filtered_merged_df[filtered_merged_df['Dim1'] == 'Total']
    filtereddeath_merged_df = df_death.copy()
    filtereddeath_merged_df = filtereddeath_merged_df[filtereddeath_merged_df['Year'] == option_slctd]
    filtereddeath_merged_df = filtereddeath_merged_df[filtereddeath_merged_df['Age Group'] == '[All]']
    filtereddeath_merged_df = filtereddeath_merged_df[filtereddeath_merged_df['Sex'] == 'All']
    #komşu ülkeleri bulmak için apı defi hazırlamak
    def get_neighbors(country_code):
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and 'borders' in data[0]:
                return data[0]['borders']
        return None

    neighbor_countries = get_neighbors(selected_country)
    all_bubble = []
    #Komşu ülkelerin varlığını kontrol etmek.(JPN nın komşu ülkesi yok gibi)
    if neighbor_countries:
        all_bubble = neighbor_countries
        all_bubble.append(selected_country)
    else:
        all_bubble.append(selected_country)
    #Bubble lara rastgele renkler atama
    def generate_random_color():
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        return (red, green, blue)

    size = []
    sizecolor = []
    y = []
    x = []
    death = []
    #Baloncuklara pm2.5 değerlerini atama
    for country_code in all_bubble:
        # Belirli bir ülke koduna sahip olan satırların "FactValueNumeric" verilerini alın
        filtered_data = filtered_merged_df.loc[filtered_merged_df["SpatialDimValueCode"] == country_code, "FactValueNumeric"]
        
        # Filtrelenmiş verinin boş olup olmadığını kontrol edin
        if not filtered_data.empty:
            # Eğer veri varsa, ilk değeri alın
            first_value = filtered_data.iloc[0]
            size.append(first_value)  # Tek bir değeri listeye ekleyin
        else:
            # Eğer veri yoksa, 0 ekleyin ya da başka bir işlem yapın
            size.append(0)
            
        y.append(5)

        # sizecolor listesine rastgele renk ekleme
        sizecolor.append(generate_random_color())
        
    # Baloncukların boyutunu ayarlayaabilmek için
    max_size = max(size)
    for i in range(len(size)):
        size[i] = size[i] * (1/max_size*200)*0.3

    #Boyutlara göre sıralamak için sözlük oluşturma (ülke isimlerinin boyutlarla senkronize olması için)
    combined_dict = dict(zip(all_bubble, size))
    # Sözlüğü boyuta göre sıralama
    sorted_dict = dict(sorted(combined_dict.items(), key=lambda item: item[1]))  # item[1] boyutları temsil eder
    #Ülkelere ölüm sayılarını atama ve baloncuklar arasındaki mesafeyi ayarlama
    sumsizes = 0
    for key in sorted_dict:
        sumsizes += sorted_dict[key]
        x.append(sumsizes)
        filtered_death_data = filtereddeath_merged_df.loc[filtereddeath_merged_df["Country Code"] == key, "Number"].astype(float)
        if filtered_death_data.empty:
            death.append(0)
        else:
            death.extend(filtered_death_data)

    colors = sizecolor  # Bubble'ların renkleri
    colors = [f"rgb{color}" for color in sizecolor]

    #Baloncuklara yazılacak text'i oluşturmak için
    for i in range(len(all_bubble)):
        death[i]=int(death[i])
        if death[i] == 0:
            death[i] = ''    
        all_bubble[i] = str(list(sorted_dict.keys())[i]) + '<br>' + str(death[i])
        

    # Bubble chart'i oluşturma
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        marker=dict(
            size=list(sorted_dict.values()),
            color=colors,
            opacity=1
        ),
        hoverinfo="text",  # Metinleri fareyle üzerine gelindiğinde göster
        textposition="top center",  # Metin konumu
        hovertext=all_bubble,
        text=all_bubble,
        textfont=dict(
            family="Arial",  # Font ailesi
            size=13,         # Metin boyutu
            color="black"    # Metin rengi
        ),
    ))
    # Grafik özelliklerini ayarlama
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',  # Arka plan rengini şeffaf yapar
        paper_bgcolor='rgba(0,0,0,0)', # Kağıt (grafik dışındaki alan) arka plan rengini şeffaf yapar
        margin=dict(l=0, r=0, t=50, b=0), # Grafik içindeki beyaz kenarlıkları kaldırır ve üst kenara metin eklemek için biraz boşluk bırakır
        xaxis=dict(
            showgrid=False,  # x eksenindeki ızgaraları kaldırır
            showticklabels=False  # x eksenindeki sayı etiketlerini kaldırır
        ),  
        yaxis=dict(
            showgrid=False,  # y eksenindeki ızgaraları kaldırır
            showticklabels=False  # y eksenindeki sayı etiketlerini kaldırır
        ),
        width = width * 0.47,
        height = height * 0.2475
    )

    # Metni ekleyin
    fig.add_annotation(
        xref="paper",  # Metnin x koordinatının kağıdın içindeki bir oran olmasını sağlar
        yref="paper",  # Metnin y koordinatının kağıdın içindeki bir oran olmasını sağlar
        x=0.5,         # Metnin x konumu (0-1 arasında bir değer olarak kağıdın içindeki yüzdelik oran)
        y=1.15,        # Metnin y konumu (0-1 arasında bir değer olarak kağıdın içindeki yüzdelik oran)
        text= country_name + " ve Komşu Ülkeleri",  # Metin içeriği
        showarrow=False,        # Ok gösterme
        font=dict(
            family="Arial",     # Font ailesi
            size=24,            # Metin boyutu
            color= "black"
        )
    )
    # Aşağıya bilgi eklemek için
    fig.add_annotation(
        xref="paper",           # Metnin x konumunu kağıdın içindeki bir orana göre belirler
        yref="paper",           # Metnin y konumunu kağıdın içindeki bir orana göre belirler
        x=0.85,                 # Metnin x konumu (0-1 arasında bir değer olarak kağıdın içindeki yüzdelik oran)
        y=0.05,                 # Metnin y konumu (0-1 arasında bir değer olarak kağıdın içindeki yüzdelik oran)
        text="Baloncukların büyüklükleri havadaki pm2.5 seviyesini, üstündeki değerler ise ölüm sayısını temsil eder.",  # Metin içeriği
        showarrow=False,        # Ok gösterme
        font=dict(
            family="Arial",     # Font ailesi
            size=10,            # Metin boyutu
            color="black"       # Metin rengi
        )
    )

    return fig.to_dict()

def gösterge(option_slctd,clickData):

    global width, height
    #Verileri oluşturma ve seçme
    filteredmerged_df = merged_df.copy()
    filteredmerged_df = filteredmerged_df[(filteredmerged_df['Country Code'] == clickData) & 
                                          (filteredmerged_df['Age Group'] == '[All]') &
                                          (filteredmerged_df['Sex'] == 'All') 
                                          ]

    fact_value = filteredmerged_df[(filteredmerged_df["Year"]==option_slctd) & (filteredmerged_df["Dim1_y"]=="Total")]['FactValueNumeric']

    plot_bgcolor = 'rgba(0,0,0,0)'
    quadrant_colors = [plot_bgcolor, "#d3382e", "#f2a529", "#eff229", "#85e043"] 
    quadrant_text = ["", "<b>Çok yüksek</b>", "<b>Yüksek</b>", "<b>Orta</b>", "<b>Düşük</b>"]
    n_quadrants = len(quadrant_colors) - 1

    current_value = fact_value.values[0]
    min_value = 0
    max_value = 70
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    fig = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                rotation=90,
                hole=0.5,
                marker_colors=quadrant_colors,
                text=quadrant_text,
                textfont=dict(size=8,color="black"),
                textinfo="text",
                hoverinfo="skip",
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0,t=0,l=0,r=30),
            width=width*0.2,
            height=height*.2,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b> pm2.5 seviyesi </b><br>{current_value}",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle)*0.6,
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                )
            ]
        )
    )
    
    return fig.to_dict()

def kursun(clickData):
    
    filtered_selected_df = merged_df.copy()
    filtered_selected_df = filtered_selected_df[filtered_selected_df['Country Code']==clickData]
    filtered_selected_df = filtered_selected_df[(filtered_selected_df['Age Group'] == '[All]') &(filtered_selected_df['Sex'] == 'All')]
    max_year = filtered_selected_df['Year'].max()
    max_year=int(max_year)
    if max_year!=2010:
        max_yeareksi=max_year-1
    else:
        max_yeareksi=max_year
    
    mean_valueFactValue = filtered_selected_df[(filtered_selected_df["Year"]>=2010) & (filtered_selected_df["Dim1_y"]=="Total")]['FactValueNumeric'].mean()
    mean_valuePerc = filtered_selected_df[(filtered_selected_df["Year"]>=2010) & (filtered_selected_df["Dim1_y"]=="Total")]['Percentage of cause-specific deaths out of total deaths'].values[0].mean()
    mean_valuePop = filtered_selected_df[(filtered_selected_df["Year"] >= 2010) & (filtered_selected_df["Year"] <= max_year) & (filtered_selected_df["Dim1_y"] == "Total")]['Death rate per 100 000 population'].mean()

    fig = go.Figure()
    
    ### pm2.5
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        number = {"suffix": "μm"},
        value=filtered_selected_df[(filtered_selected_df["Year"]==max_year) & (filtered_selected_df["Dim1_y"]=="Total")]['FactValueNumeric'].values[0],
        delta={"reference":filtered_selected_df[(filtered_selected_df["Year"]==max_yeareksi) & (filtered_selected_df["Dim1_y"]=="Total")]['FactValueNumeric'].values[0],
               'decreasing': {
                   'color': "green",
               },
               'increasing': {
                   'color': "red",
               }},
        domain={'x': [0.25, 1], 'y': [0.13, 0.3]},
        gauge={
            'shape': "bullet",
            'axis': {'tickangle':0,'tickwidth':0.2,'tickfont':dict(size=8,color="black"),'range': [0,65]},
            'threshold': {
                'line': {'color': "blue", 'width': 1},
                'thickness': 0.5,
                'value': mean_valueFactValue,
            },
            'steps': [
                {'range': [0, 20], 'color': "#9ade5d"},
                {'range': [20,35], 'color': "#f0f259"},
                {'range': [35,65], 'color': "#d3382e"},],
            'bar': {'color': "black",'thickness':0.1}
        }
    ))
    
    #### death number for 1000
    
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        number = {"font":dict(size=14)},
        value=filtered_selected_df[(filtered_selected_df["Year"]==max_year) & (filtered_selected_df["Dim1_y"]=="Total")]['Death rate per 100 000 population'].values[0],
        delta={"reference":filtered_selected_df[(filtered_selected_df["Year"]==max_yeareksi) & (filtered_selected_df["Dim1_y"]=="Total")]['Death rate per 100 000 population'].values[0],
                'decreasing': {
                    'color': "green",
                },
                'increasing': {
                    'color': "red",
                }},
        domain={'x': [0.25, 1], 'y': [0.43, 0.6]},
        gauge={
            'shape': "bullet",
            'axis': {'tickangle':0,'tickwidth':0.2,'tickfont':dict(size=8,color="black"),'range': [0,120]},
            'threshold': {
                'line': {'color': "blue", 'width': 1},
                'thickness': 0.5,
                'value': mean_valuePop,
            },
            'steps': [
        {'range': [0,40], 'color': "#9ade5d"},
        {'range': [40,70], 'color': "#f0f259"},
        {'range': [70,120], 'color': "#d3382e"}],
            'bar': {'color': "black",'thickness':0.1}
        }
    ))
    
    ### death percentage
    
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=filtered_selected_df[(filtered_selected_df["Year"]==max_year) & (filtered_selected_df["Dim1_y"]=="Total")]['Percentage of cause-specific deaths out of total deaths'].values[0],
        number = {"prefix": "%"},
        delta={"reference": filtered_selected_df[(filtered_selected_df["Year"]==max_yeareksi) & (filtered_selected_df["Dim1_y"]=="Total")]['Percentage of cause-specific deaths out of total deaths'].values[0],
               'decreasing': {
                   'color': "green",
               },
               'increasing': {
                   'color': "red",
               }
               },
        domain={'x': [0.25, 1], 'y': [0.73, 0.9]},
        gauge={
            'shape': "bullet",
            'axis': {'tickangle':0,'tickwidth':0.2,'tickfont':dict(size=8,color="black"), 'range': [0,12]},
            'threshold': {
                'line': {'color': "blue", 'width': 1},
                'thickness': 0.5,
                'value': mean_valuePerc,
            },
            'steps': [
        {'range': [0,5], 'color': "#9ade5d"},
        {'range': [5,8], 'color': "#f0f259"},
        {'range': [8,12], 'color': "#d3382e"}],
            'bar': {'color': "black",'thickness':0.1}
        }
    ))

    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        width=width * 0.17,  # Genişlik parametresini yarıya indir
        height=height * 0.24,  # Yükseklik parametresini üçte bir oranında artır
        annotations=[
            dict(
                text="<span style='font-size:8;color:black'><b>SYH'a bağlı<br>Yüzdelik <br> Ölüm</b></span>",
                x=0.03,
                y=0.9,
                showarrow=False,
                xref="paper",
                yref="paper"
            ),
            dict(
                text="<span style='font-size:8;color:black'><b>100 000 <br>kişide <br>ölüm</b></span>",
                x=0.07,
                y=0.5,
                showarrow=False,
                xref="paper",
                yref="paper"
            ),
            dict(
                text="<span style='font-size:8;color:black'><b>pm2.5 <br> Seviyesi</b></span>",
                x=0.06,
                y=0.15,
                showarrow=False,
                xref="paper",
                yref="paper"
            )
        ]
    )



    return fig.to_dict()


#### radar callback

hovered_location = ""
@app.callback(
    [Output('hovered_location', 'style'),
     Output('gül', 'figure')],  
    [Input('Harita', 'hoverData')],
    [Input('secilenyıl', 'value')]

)
def display_hover_data(hoverData,option_slctd):
    global width, height
    global hovered_location
    location = ""
    RadarWorldForCountry = np.zeros(5, dtype=float)
    if hoverData is not None:
        # Üzerine gelinen veriyi alma
        location = hoverData['points'][0]['location']  
        if location != hovered_location:
            hovered_location = location
            # Radar grafiğini güncellemek için seçilen ülkenin verilerini kullanma
            filteredmerged_df = merged_df.copy()
            filteredmerged_df = filteredmerged_df[filteredmerged_df['Age Group'] == '[All]']
            filteredmerged_df = filteredmerged_df[filteredmerged_df['Dim1_y'] == 'Total']
            filteredmerged_df = filteredmerged_df[filteredmerged_df['Sex'] == 'All']
            filteredmerged_df = filteredmerged_df[filteredmerged_df['Year'] == option_slctd]
            filtered_selected_df= filteredmerged_df[filteredmerged_df['Country Code']==location]
            
            #### ismi çok kötü olan ülkeleri hoverdan siliyoruz
            if location=="MNG" or location=="IRN" or filtered_selected_df.empty:
                RadarWorldForCountry = np.zeros(5, dtype=float)
            else:
                
                # Üzerinde bulunduğumuz ülkenin RadarWorldForCountry metrisini oluşturma
                RadarWorldForCountry[0] = filtered_selected_df['NormalizationForNumber'].astype(float)
                RadarWorldForCountry[1] = filtered_selected_df['NormalizationForPerDeath'].astype(float)
                RadarWorldForCountry[2] = filtered_selected_df['NormalizationForAgeStandardizedDeathRate'].astype(float)
                RadarWorldForCountry[3] = filtered_selected_df['NormalizationForFactValueNumericLow'].astype(float)
                RadarWorldForCountry[4] = filtered_selected_df['NormalizationForFactValueNumericHigh'].astype(float)
    
                # Kategorilerimizi belirleme
                categories = ['Ölüm Sayısı','Yüzdelik <br> Ölüm Oranı','Yaşa Standardize <br> Edilmiş Oran', 'Max pm2.5 <br> seviyesi', 'Min pm2.5  <br> seviyesi']
        
           # Eğer verilerimiz yeterli değil ise,
            if RadarWorldForCountry[0] == 0:
                theta = np.linspace(0, 2*np.pi, 100)
                
                x = 0.5 * np.cos(theta)
                y = 0.5 * np.sin(theta)
                
                # Gözler
                eye_x = [0.3, -0.3]
                eye_y = [0.3, 0.3]
                
                # Ağız
                mouth_x = np.linspace(-0.3, 0.3, 100)
                mouth_y = 0.1 * np.cos(mouth_x * 5)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black')))  # Dış çizgi
                fig.add_trace(go.Scatter(x=eye_x, y=eye_y, mode='markers', marker=dict(color='black', size=10)))  # Gözler
                fig.add_trace(go.Scatter(x=mouth_x, y=mouth_y, mode='lines', line=dict(color='black')))  # Ağız
                
                fig.update_layout(
                    title='Ne yazık ki bu ülkenin yeterli verileri paylaşılmadı.',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    showlegend=False
                )
                style = {'position': 'fixed', 'top': str(hoverData['points'][0]['bbox']['y1'] + 10) + 'px', 'left': str(hoverData['points'][0]['bbox']['x1'] + 10) + 'px', 'padding': '10px', 'border': '1px solid black', 'background-color': 'white', 'display': 'block', 'z-index': 9999}
                return style,  fig.to_dict()
            
                # Verilerimiz yeterli ise
            else:
                # Figure oluşturma
                fig = go.Figure()
                # Dünya ortalaması için Barpolar oluşturma
                fig.add_trace(go.Barpolar(
                    r=RadarWorld,
                    theta=categories,
                    name='Dünya Ortalaması',
                    marker_color=['#ffa600'] * 6,
                    marker_line_color='white',
                    marker_line_width=0.2,  # Çubukların kalınlığını artırır
                    hoverinfo=['theta'] * 2,
                    opacity=0.7,
                    width=0.97,  # Çubukların genişliğini artırır
                    base=0,
                    thetaunit='radians', 
                ))
                # Üzerinde bulunduğumuz ülke ortalaması için Barpolar oluşturma
                fig.add_trace(go.Barpolar(
                    r=RadarWorldForCountry.tolist(),
                    theta=categories,
                    name='Seçilen Ülke Ortalaması',
                    marker_color=['#bc5090'] *6 ,
                    marker_line_color='white',
                    marker_line_width=0.2,  # Çubukların kalınlığını artırır
                    hoverinfo=['theta'] * 9,
                    opacity=0.7,  
                    width=0.97,  # Çubukların genişliğini artırır
                    base=0,
                    thetaunit='radians',  
                ))
                
                # Polar grafiğimizin görünümü ve davranışını özelleştirme
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            showline=False,
                            showticklabels=False,
                            linewidth=2,
                            gridcolor='rgba(0,0,0,0)',
                            gridwidth=2,
                        ),
                        angularaxis=dict(
                            tickfont=dict(
                                size=11,
    color='rgb(215, 99, 115)'  # Theta labellarının rengini belirleme
),
                            linewidth=3,
                            showline=False,
                            showticklabels=True,
                            rotation=90,  # Bu, kategori etiketlerini yatay hale getirir
                        )
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                    ),
                    title='Dünya ve Ülke Ortalaması Radar Grafiği',
                    title_font=dict(size=12,color='black'),
                    margin=dict(l=25, r=25, t=50, b=25),
                    polar_bgcolor='#e8ebf5',   
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.85)',
                    width = width * 0.25,
                    height = height * 0.33
                )
        
                style = {'position': 'fixed', 'top': str(hoverData['points'][0]['bbox']['y1'] + 10) + 'px', 'left': str(hoverData['points'][0]['bbox']['x1'] + 10) + 'px', 'padding': '10px', 'background-color': 'transparent', 'display': 'block', 'z-index': 9999,'width':'20%','height':'250px',}
                hoverData = None
                return style,  fig.to_dict()
        else:   
            hovered_location = ""
            location =""
            style = {'display': 'none'}
            return style, {'data': []}
    else:
        hovered_location = ""
        location =""
        style = {'display': 'none'}
        return style, {'data': []}
    
    

@app.callback(
    [Output('info_div', 'style'),
     Output('BolgeHaritasi', 'src'),
     Output('sunburst', 'figure'),
     Output('linearea', 'figure'),
     Output('info_div2', 'style')],
    [Input('closeButton2', 'n_clicks'),
     Input('closeButton3', 'n_clicks'),
     Input('info_circle1', 'n_clicks'),
     Input('info_circle2', 'n_clicks'),
     ],
    prevent_initial_call=True
)
def toggle_info_div(close_clicks,close_clicks2, info_clicks, info_clicks2):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    prop_id = ctx.triggered[0]['prop_id']
    if prop_id == 'closeButton2.n_clicks' or prop_id == 'closeButton3.n_clicks':
        return {'display': 'none'}, "", {'data': []}, {'data': []}, {'display': 'none'}
    elif prop_id == 'info_circle1.n_clicks':
        sunburstfig = sunburst()
        lineareafig = linearea()
        return {'position': 'absolute', 'margin-top': '5%', 'margin-right': '5%', 'margin-bottom': '5%', 'margin-left': '5%', 'width': '90%', 'height': '80%', 'background-color': 'rgba(0, 0, 0, 0.8)', 'z-index': '1000', 'display': 'block'}, "assets/regionmap.png", sunburstfig, lineareafig, {'display': 'none'}
    elif prop_id == 'info_circle2.n_clicks':
        return {'display': 'none'}, "", {'data': []}, {'data': []}, {'position': 'absolute', 'margin-top': '5%', 'margin-right': '5%', 'margin-bottom': '5%', 'margin-left': '5%', 'width': '90%', 'height': '80%', 'background-color': 'rgba(0, 0, 0, 0.8)', 'z-index': '1000', 'display': 'block','overflow': 'scroll'}
    else:
        raise dash.exceptions.PreventUpdate

def sunburst():
    
    new_color_scale = [
            (0, '#b3eb73'),
            (0.5, '#fbed71'),
            (0.55, '#efb35d'),
            (1, '#e86c75')     ]    

    df_air['NormalizationForFactValueNumeric'] = pd.to_numeric(df_air['NormalizationForFactValueNumeric'], errors='coerce')


    fig = px.sunburst(df_air, path=['ParentLocation', 'Location'], values='NormalizationForFactValueNumeric',
                      color='NormalizationForFactValueNumeric', hover_data=['ParentLocation'],
                      color_continuous_scale=new_color_scale,
                      color_continuous_midpoint=np.average(df_air['NormalizationForFactValueNumeric'], weights=df_air['NormalizationForFactValueNumeric']))

    fig.update_layout(
        width = width * 0.315,
        height = height * 0.4)
    return fig.to_dict()

def linearea():
    
    filtered_df_for_filledareaplotforair = df_air.copy

    # filtered_df_for_filledareaplotforair fonksiyonunu çağırarak gerçek DataFrame'i al
    result_df = filtered_df_for_filledareaplotforair()

    # DataFrame'i "ParentLocation" ve "Period" sütunlarına göre gruplayacak ve her bir grubun ortalamasını hesaplayacak
    region_mean_values = result_df.groupby(["ParentLocation", "Period"]).mean().reset_index()



    color_palette = {
        'Africa': '#5E1675',                      
        'South-East Asia': '#39A7FF',                        
        'Europe': '#337357',                      
        'Americas': '#FFD23F',  
        'Eastern Mediterranean': '#211951',
        'Western Pacific': '#FF4B91'                    
    }

    fig = px.area(region_mean_values, x="Period", y="FactValueNumericHigh", color="ParentLocation", 
                  line_group="ParentLocation", color_discrete_map=color_palette,
                  custom_data=["Period", "FactValueNumericHigh"])

    fig.update_traces(hovertemplate="<br>".join([
        "Year: %{customdata[0]}",
        "Percentage: %{customdata[1]:.3f}"
    ]), line_width=0)

    fig.update_yaxes(matches=None)

    fig.update_layout(
        plot_bgcolor='white',  # Arka plan rengi
        paper_bgcolor='white',  # Kağıt rengi (grafik dışındaki alan)
        width = width * 0.315,
        height = height * 0.4
    )

    return fig.to_dict()










#tarayıcı genişliğini ve yüksekliğini alma
app.clientside_callback(
    """
    function updateBrowserInfo() {
        var browserWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        var browserHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
        return [browserWidth, browserHeight];
    }
    """,
    Output('browser-info', 'children'),
    [Input('dummy-input', 'children')]
)

# app.clientside_callback(
#     """
#     function close_clicked_location(n_clicks) {
#         if (n_clicks > 0 && document.getElementById("info_div").style.display != "none") {
#             document.getElementById("info_div").style.display = "none";
#             console.log('imdat');
#             return {'display': 'none'};
#         }
#     }
#     """,
#     Output('info_div', 'style'),
#     Input('closeButton2', 'n_clicks')
# )


#Width ve Height değerlerini global değişkenlere atama
@app.callback(
    Output('display-browser-info', 'children'),
    [Input('dummy-input', 'children'),
     Input('browser-info', 'children')]
)
def display_browser_info(dummy, browser_info):
    global width
    global height
    if browser_info:
        browser_width, browser_height = browser_info
        width = browser_width
        height = browser_height
    return None
    
    
    
    
    


# Uygulamayı çalıştırma
if __name__ == '__main__':
    app.run_server(debug=True)
