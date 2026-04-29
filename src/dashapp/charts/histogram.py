"""Yaş-cinsiyet bazlı ölüm oranı histogramı (grup bar grafiği)."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from dashapp.data_loader import load_sex_age_breakdown
from dashapp.theme import CHART_COLORS, CHART_MARGIN, TRANSPARENT_LAYOUT
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
    c = CHART_COLORS
    fig.add_trace(go.Bar(x=age_labels, y=male_country, name=f"{display_name} Erkek", marker_color=c[0]))
    fig.add_trace(go.Bar(x=age_labels, y=female_country, name=f"{display_name} Kadın", marker_color=c[1]))
    fig.add_trace(go.Bar(x=age_labels, y=male_world, name="Dünya Erkek Ort.", marker_color=c[4]))
    fig.add_trace(go.Bar(x=age_labels, y=female_world, name="Dünya Kadın Ort.", marker_color=c[7]))

    fig.update_layout(
        **TRANSPARENT_LAYOUT,
        title=dict(text="Yaş & Cinsiyet Bazında Ölüm Oranı", **{k: v for k, v in dict(font=dict(size=12), x=0.5, xanchor="center").items()}),
        xaxis=dict(title="Yaş Grupları", tickangle=-30),
        yaxis=dict(title="Ölüm Oranı"),
        barmode="group",
        width=width * 0.46,
        height=height * 0.2475,
        legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
        margin=CHART_MARGIN,
    )
    return fig.to_dict()
