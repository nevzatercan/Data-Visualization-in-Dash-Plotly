"""Yerleşim bölgesine göre PM2.5 iç içe pasta grafiği + ülke bayrağı."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go

from dashapp.data_loader import load_merged, world_residence_means
from dashapp.theme import TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total

_FLAGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "img" / "flags"


def _flag_source(iso: str) -> str | None:
    """Yerel SVG yolu varsa Dash asset URL'si döndür, yoksa None."""
    path = _FLAGS_DIR / f"{iso}.svg"
    if path.exists():
        # Dash /assets/ prefix'i ile serve eder
        return f"/assets/img/flags/{iso}.svg"
    return None


def figure(
    year: int,
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
    country_name: str = "",
    country_name_english: str = "",
) -> dict:
    """Yerleşim tipine göre PM2.5 ortalaması iç içe pasta grafiği.

    Dış halka: seçili ülke; iç halka: dünya ortalaması.
    Merkeze ülke bayrağı eklenir (yerel assets'ten).

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
    country_name_english:
        Bayrağı aramak için kullanılmaz — iso3 yeterli.
    """
    merged = load_merged()
    residence = world_residence_means()

    df = filter_total(merged, year=year, country=iso, sex=None, age=None, dim1_y=None)
    df = df.copy()
    df["FactValueNumeric"] = df["FactValueNumeric"].astype(float)

    labels = ["Şehir", "Kasaba", "Kentsel", "Kırsal"]
    dim_keys = ["Cities", "Towns", "Urban", "Rural"]

    country_means = []
    for dk in dim_keys:
        subset = df[(df["Dim1_y"] == dk) & (df["Age group code"] == "Age_all")]["FactValueNumeric"]
        country_means.append(float(subset.mean()) if not subset.empty else 0.0)

    world_means = [residence.get(dk, 0.0) for dk in dim_keys]

    formatted_country = [f"{v:.2f}" for v in country_means]
    formatted_world = [f"{v:.2f}" for v in world_means]

    # Dış halka: CHART_COLORS paleti (opaklık 0.90)
    colors_outer = [
        "rgba( 56, 189, 248, 0.90)",   # sky-400
        "rgba(251, 113, 133, 0.90)",   # rose-400
        "rgba( 52, 211, 153, 0.90)",   # emerald-400
        "rgba(251, 191,  36, 0.90)",   # amber-400
    ]
    # İç halka: aynı tonlar, daha saydam
    colors_inner = [
        "rgba( 56, 189, 248, 0.35)",
        "rgba(251, 113, 133, 0.35)",
        "rgba( 52, 211, 153, 0.35)",
        "rgba(251, 191,  36, 0.35)",
    ]

    outer = go.Pie(
        labels=labels, values=formatted_country, textinfo="value",
        name="Outer Pie", hole=0.2,
        marker=dict(colors=colors_outer, line=dict(width=5, color="rgba(10,18,36,0.80)")),
        domain={"x": [0.3, 0.9], "y": [0.1, 0.9]},
    )
    inner = go.Pie(
        labels=labels, values=formatted_world, name="Inner Pie",
        textinfo="value", hole=0.8,
        marker=dict(colors=colors_inner, line=dict(width=5, color="rgba(10,18,36,0.80)")),
        domain={"x": [0.2, 1.0], "y": [0.0, 1.0]},
    )

    display_name = country_name or iso
    fig = go.Figure(data=[outer, inner])
    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        showlegend=True,
        margin=dict(l=0, r=0, t=0, b=0),
        width=width * 0.23,
        height=height * 0.495,
        legend=dict(y=0.5),
        annotations=[
            dict(
                text=f'<span style="color:rgba(255,255,255,0.85);font-weight:bold">{display_name} ve Dünyanın<br>yerleşim bölgelerine göre<br>pm2.5 ortalaması</span>',
                x=1.05, y=0.95, font_size=16, showarrow=False,
            ),
            dict(text="<span>Şehir: en az 50.000 nüfuslu (km² başına >1.500 nüfuslu)</span>", x=1.05, y=0.09, font_size=9, showarrow=False),
            dict(text="<span>Kentsel: en az 5.000 nüfuslu (km² başına >300 nüfuslu)</span>", x=1.03, y=0.06, font_size=9, showarrow=False),
            dict(text="<span>Kırsal: en az 1.000 nüfuslu (km² başına <300 nüfuslu)</span>", x=0.498, y=0.03, font_size=9, showarrow=False),
            dict(text="<span>Kasaba: en az 1.000 nüfuslu (km² başına >300 nüfuslu)</span>", x=1.03, y=0.0, font_size=9, showarrow=False),
        ],
    )

    flag_src = _flag_source(iso)
    if flag_src:
        fig.add_layout_image(dict(
            source=flag_src,
            xref="paper", yref="paper",
            x=0.74, y=0.455,
            sizex=0.22, sizey=0.20,
            layer="below",
            xanchor="right", yanchor="bottom",
            sizing="contain",
        ))

    return fig.to_dict()
