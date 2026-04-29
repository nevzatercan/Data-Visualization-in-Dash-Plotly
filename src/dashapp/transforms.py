"""Tekrarlı veri filtreleme ve sade dönüşüm yardımcıları.

Mevcut callback'lerde 20+ kez geçen `df[df['Dim1_y']=='Total']` benzeri
örüntüleri ve `series.values[0]` gibi empty-Series riskli erişimleri
tek bir merkeze toplar.

Kullanım:
    from dashapp.transforms import filter_total, safe_first, colorchoose
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

# Plan'da tanımlı eşik değerleri — UI'da renk kodlamasıyla eşleşir.
_GREEN_LIMIT = 0.13
_YELLOW_LIMIT = 0.44

_COLOR_GREEN = ("assets/yesil.png", "rgb(218, 255, 219, 1)")
_COLOR_YELLOW = ("assets/sari.png", "rgb(255, 248, 189, 1)")
_COLOR_RED = ("assets/kirmizi.png", "rgb(255, 218, 202, 1)")


def filter_total(
    df: pd.DataFrame,
    *,
    year: Optional[int] = None,
    country: Optional[str] = None,
    sex: Optional[str] = "All",
    age: Optional[str] = "[All]",
    dim1_y: Optional[str] = "Total",
    dim1: Optional[str] = None,
) -> pd.DataFrame:
    """Veri çerçevesini standart filtre seti ile daralt.

    Tüm parametreler opsiyoneldir; verilmezse o sütuna filtre uygulanmaz.
    Default'lar projedeki en sık kullanılan kombinasyonu yansıtır:
    Sex='All', Age Group='[All]', Dim1_y='Total'.

    Args:
        df: Filtrelenecek DataFrame (genelde merged_df).
        year: 'Year' sütununa eşitlik filtresi.
        country: 'Country Code' sütununa eşitlik filtresi.
        sex: 'Sex' sütununa eşitlik filtresi (default 'All', None ile kapatılır).
        age: 'Age Group' sütununa eşitlik filtresi (default '[All]', None ile kapatılır).
        dim1_y: 'Dim1_y' sütununa eşitlik filtresi (default 'Total', None ile kapatılır).
        dim1: 'Dim1' sütununa eşitlik filtresi (df_air için).

    Returns:
        Filtrelenmiş DataFrame görünümü (kopya değil — caller mutate ediyorsa
        kendi `.copy()`'sini almalı).
    """
    mask = pd.Series(True, index=df.index)
    if year is not None:
        # df_air 'Period' kullanır, merged_df 'Year'.
        if "Year" in df.columns:
            mask &= df["Year"] == year
        elif "Period" in df.columns:
            mask &= df["Period"] == year
    if country is not None:
        if "Country Code" in df.columns:
            mask &= df["Country Code"] == country
        elif "SpatialDimValueCode" in df.columns:
            mask &= df["SpatialDimValueCode"] == country
    if sex is not None and "Sex" in df.columns:
        mask &= df["Sex"] == sex
    if age is not None and "Age Group" in df.columns:
        mask &= df["Age Group"] == age
    if dim1_y is not None and "Dim1_y" in df.columns:
        mask &= df["Dim1_y"] == dim1_y
    if dim1 is not None and "Dim1" in df.columns:
        mask &= df["Dim1"] == dim1
    return df[mask]


def safe_first(series: pd.Series, default: Any = None) -> Any:
    """Series'in ilk değerini güvenli şekilde döndür.

    Boş Series, NaN ilk değer veya tip dönüşüm hatasında `default` döner.
    `series.values[0]` ve `series.iloc[0]` çağrılarının yerine kullanılır.
    """
    if series is None or len(series) == 0:
        return default
    value = series.iloc[0]
    if pd.isna(value):
        return default
    return value


def colorchoose(normalization_value: float) -> tuple[str, str]:
    """PM2.5 normalleştirilmiş değere göre asset yolu + arka plan rengi.

    Plan'da `app.py:888-897`'de bulunan inline `colorchoose` fonksiyonu
    buraya taşındı. Boş/NaN giriş için yeşil eşiğin altı kabul edilir.

    Returns:
        (asset_path, rgba_color) tuple'ı.
    """
    if normalization_value is None or pd.isna(normalization_value):
        return _COLOR_GREEN
    if normalization_value < _GREEN_LIMIT:
        return _COLOR_GREEN
    if normalization_value < _YELLOW_LIMIT:
        return _COLOR_YELLOW
    return _COLOR_RED
