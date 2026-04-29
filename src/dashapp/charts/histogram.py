"""Yaş-cinsiyet bazlı ölüm oranı histogramı (grup bar grafiği)."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from dashapp.data_loader import load_sex_age_breakdown
from dashapp.theme import TRANSPARENT_LAYOUT
from dashapp.transforms import filter_total


def figure(
    year: int,
    iso: str,
    *,
    width: float = 1280,
    height: float = 800,
    country_name: str = "",
) -> dict:
    """Yaş gruplarına göre cinsiyet bazında ve dünya genelinde ölüm oranı bar grafiği.

    Parameters
    ----------
    year:
        Seçili yıl.
    iso:
        3 harfli ISO ülke kodu.
    width, height:
        Tarayıcı boyutları (grafik ölçekleme için).
    country_name:
        Gösterilecek Türkçe ülke adı.
    """
    df = load_sex_age_breakdown()
    display_name = country_name or iso

    # Ülkeye özel veri
    country_df = filter_total(df, year=year, country=iso, sex=None, age=None)
    country_df = country_df[~country_df["Sex"].isin(["Unknown", "All"])]

    # Dünya ortalaması
    world_df = filter_total(df, year=year, sex=None, age=None)
    world_df = world_df[~world_df["Sex"].isin(["Unknown", "All"])]

    age_groups = df["Age Group"].unique()
    # [0-49]'u sona taşı
    age_groups = np.roll(age_groups, -1)
    age_labels = list(age_groups)
    if len(age_labels) > 9:
        age_labels[9] = "Genel"

    def _means(src_df: "pd.DataFrame", sex: str) -> list[float]:  # type: ignore[name-defined]
        grp = (
            src_df[src_df["Sex"] == sex]
            .groupby("Age Group", observed=True)["NormalizationForPerDeath"]
            .mean()
            .reindex(age_groups)
            .fillna(0)
        )
        return grp.tolist()

    male_country = _means(country_df, "Male")
    female_country = _means(country_df, "Female")
    male_world = _means(world_df, "Male")
    female_world = _means(world_df, "Female")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=age_labels, y=male_country, name=f"{display_name} Erkek Ortalaması", marker_color="rgba(60,162,229,0.96)"))
    fig.add_trace(go.Bar(x=age_labels, y=female_country, name=f"{display_name} Kadın Ortalaması", marker_color="rgba(234,62,62,0.96)"))
    fig.add_trace(go.Bar(x=age_labels, y=male_world, name="Dünya Erkek Ortalaması", marker_color="rgba(50,136,193,0.96)"))
    fig.add_trace(go.Bar(x=age_labels, y=female_world, name="Dünya Kadın Ortalaması", marker_color="rgba(193,50,50,0.96)"))

    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        title="Yaş Gruplarına Göre Cinsiyet Bazında ve Dünya Genelinde Ölüm Oranı",
        xaxis=dict(title="Yaş Grupları", tickangle=0, tickfont=dict(color="black", size=10), titlefont=dict(color="black")),
        yaxis=dict(title="Ölüm Oranı", tickfont=dict(color="black"), titlefont=dict(color="black")),
        barmode="group",
        width=width * 0.46,
        height=height * 0.2475,
        legend=dict(font=dict(color="black")),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig.to_dict()
