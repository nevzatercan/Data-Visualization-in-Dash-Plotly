"""Seçili ülke + komşuları PM2.5 ve ölüm oranı baloncuk grafiği.

Komşu listesi yerel ``data/static/borders.json`` dosyasından okunur;
restcountries.com çağrısı yapılmaz.
"""

from __future__ import annotations

import plotly.graph_objects as go

from dashapp.data_loader import load_air, load_death
from dashapp.theme import CHART_COLORS, TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total
from dashapp.utils.borders import get_neighbors


def figure(
    year: int,
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
    country_name: str = "",
) -> dict:
    """Seçili ülke ve komşu ülkeler PM2.5 baloncuk grafiği.

    Baloncuk boyutu PM2.5 seviyesini, üstündeki değer ölüm oranını
    temsil eder.  max_size == 0 olduğunda (veri yoksa) grafik boş döner.

    Parameters
    ----------
    year:
        Seçili yıl.
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları.
    country_name:
        Başlıkta gösterilecek Türkçe ülke adı.
    """
    air = load_air()
    death = load_death()

    filtered_air = filter_total(air, year=year, dim1="Total", dim1_y=None)
    filtered_death = filter_total(death, year=year, dim1_y=None)

    neighbors = get_neighbors(iso)
    all_bubble = [*neighbors, iso]  # komşular önce, seçili ülke sonda

    # Her ülkeye PM2.5 ata
    sizes: list[float] = []
    for code in all_bubble:
        row = filtered_air.loc[filtered_air["SpatialDimValueCode"] == code, "FactValueNumeric"]
        sizes.append(float(row.iloc[0]) if not row.empty else 0.0)

    max_size = max(sizes, default=0.0)
    if max_size == 0:
        # Veri yok — boş dönebiliriz veya seçili ülkeye 1 atayabiliriz
        sizes = [1.0] * len(all_bubble)
        max_size = 1.0

    # Ölçeklenmiş boyutlar
    scaled = [s * (1 / max_size * 200) * 0.3 for s in sizes]

    # Boyuta göre sırala
    combined = sorted(zip(all_bubble, scaled), key=lambda t: t[1])
    sorted_codes = [t[0] for t in combined]
    sorted_sizes = [t[1] for t in combined]

    # Ölüm oranlarını al
    death_labels: list[str] = []
    for code in sorted_codes:
        row = filtered_death.loc[
            filtered_death["Country Code"] == code,
            "Percentage of cause-specific deaths out of total deaths",
        ].astype(float)
        val = float(row.iloc[0]) if not row.empty else 0.0
        death_labels.append("" if val == 0 else str(val))

    # x koordinatları: kümülatif boyut toplamı
    x_pos: list[float] = []
    cumsum = 0.0
    for s in sorted_sizes:
        cumsum += s
        x_pos.append(cumsum)

    y_pos = [5] * len(sorted_codes)
    # Palette'ten döngüsel renk — random yerine tutarlı
    colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(sorted_codes))]
    texts = [f"{code}<br>{dl}" for code, dl in zip(sorted_codes, death_labels)]

    fig = go.Figure(data=go.Scatter(
        x=x_pos, y=y_pos,
        mode="markers+text",
        marker=dict(size=sorted_sizes, color=colors, opacity=0.85),
        hoverinfo="text",
        textposition="top center",
        hovertext=texts,
        text=[f"%{t}" for t in texts],
        textfont=dict(size=11, color="rgba(255,255,255,0.85)"),
    ))

    display_name = country_name or iso
    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        showlegend=False,
        margin=dict(l=0, r=0, t=48, b=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        width=width * 0.47,
        height=height * 0.2475,
    )
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.12,
        text=f"{display_name} ve Komşu Ülkeleri — PM2.5 Karşılaştırması",
        showarrow=False,
        font=dict(size=13, color="rgba(255,255,255,0.85)"),
    )
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=-0.08,
        text="Boyut → PM2.5 seviyesi  ·  Üstteki % → ölüm oranı",
        showarrow=False,
        font=dict(size=9, color="rgba(255,255,255,0.40)"),
    )
    return fig.to_dict()
