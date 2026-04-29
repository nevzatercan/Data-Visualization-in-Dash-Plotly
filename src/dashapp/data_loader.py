"""Veri yükleme katmanı.

Tüm DataFrame'ler Parquet'ten okunur ve `lru_cache` ile bellek içinde
tek kopya tutulur. Modül seviyesinde I/O yapılmaz; ilk çağrı geldiğinde
veri yüklenir, sonraki çağrılar cache'ten döner.

Kullanım:
    from dashapp.data_loader import load_air, load_death, load_covid, load_merged

    df = load_air()
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED = ROOT / "data" / "processed"

# Sunburst grafiğinde kullanılan bölge adları İngilizce → Türkçe.
_REGION_TR = {
    "Africa": "Afrika",
    "South-East Asia": "Güney Doğu Asya",
    "Europe": "Avrupa",
    "Americas": "Amerika",
    "Eastern Mediterranean": "Ortadoğu",
    "Western Pacific": "Batı Pasifik",
}


@lru_cache(maxsize=1)
def load_air() -> pd.DataFrame:
    """PM2.5 hava kalitesi verilerini yükle (~9.5K satır)."""
    df = pd.read_parquet(PROCESSED / "air.parquet")
    df["FactValueNumeric"] = df["FactValueNumeric"].astype(float).round(4)
    df = df[pd.to_numeric(df["FactValueNumeric"], errors="coerce").notna()].copy()
    df["FactValueNumeric"] = pd.to_numeric(df["FactValueNumeric"], errors="coerce")

    fv = df["FactValueNumeric"]
    df["NormalizationForFactValueNumeric"] = (fv - fv.min()) / (fv.max() - fv.min())
    df["ParentLocation"] = df["ParentLocation"].replace(_REGION_TR)
    return df


@lru_cache(maxsize=1)
def load_death() -> pd.DataFrame:
    """Solunum yolu hastalıklarına bağlı ölüm verilerini yükle (~310K satır)."""
    df = pd.read_parquet(PROCESSED / "death.parquet")
    df["Percentage of cause-specific deaths out of total deaths"] = (
        df["Percentage of cause-specific deaths out of total deaths"].astype(float).round(4)
    )

    air = load_air()
    missing_codes = air[~air["SpatialDimValueCode"].isin(df["Country Code"])][
        "SpatialDimValueCode"
    ].unique()
    missing_names = air[~air["Location"].isin(df["Country Name"])]["Location"].unique()
    code_name_map = dict(zip(air["SpatialDimValueCode"], air["Location"]))

    filler_by_code = [
        {
            "Country Code": code,
            "Country Name": code_name_map.get(code, "Unknown"),
            "Year": year,
            "Dim1": "Total",
            "Age Group": "[All]",
            "Sex": "All",
            "Number": 0,
            "Percentage of cause-specific deaths out of total deaths": 0.0,
        }
        for code in missing_codes
        for year in range(2010, 2020)
    ]
    filler_by_name = [
        {
            "Country Name": name,
            "Year": year,
            "Dim1": "Total",
            "Age Group": "[All]",
            "Sex": "All",
            "Number": 0,
            "Percentage of cause-specific deaths out of total deaths": 0.0,
        }
        for name in missing_names
        for year in range(2010, 2020)
    ]
    if filler_by_code:
        df = pd.concat([df, pd.DataFrame(filler_by_code)], ignore_index=True)
    if filler_by_name:
        df = pd.concat([df, pd.DataFrame(filler_by_name)], ignore_index=True)
    return df


@lru_cache(maxsize=1)
def load_covid() -> pd.DataFrame:
    """COVID-19 kümülatif ölüm verilerini yükle (~240 satır)."""
    return pd.read_parquet(PROCESSED / "covid.parquet")


@lru_cache(maxsize=1)
def load_merged() -> pd.DataFrame:
    """Death + Air merge edilmiş, normalize sütunları eklenmiş ana DataFrame."""
    death = load_death()
    air = load_air()
    merged = pd.merge(
        death,
        air,
        left_on=["Country Code", "Year"],
        right_on=["SpatialDimValueCode", "Period"],
        how="inner",
    )

    drop_cols = [
        "IndicatorCode", "ValueType", "Location type", "Period type",
        "IsLatestYear", "Dim1 type", "Dim1ValueCode", "Dim2 type", "Dim2",
        "Dim2ValueCode", "Dim3", "DataSourceDimValueCode", "Dim3ValueCode",
        "DataSource", "FactValueUoM", "FactValueNumericLowPrefix",
        "FactValueNumericHighPrefix", "FactValueTranslationID", "FactComments",
        "Language", "DateModified", "Dim3 type", "Indicator",
        "ParentLocationCode", "ParentLocation", "SpatialDimValueCode",
        "Location", "Period", "FactValueNumericPrefix",
    ]
    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])
    merged = merged[~merged["Age Group"].isin(["[Unknown]"])]

    merged.dropna(
        subset=["Percentage of cause-specific deaths out of total deaths"], inplace=True
    )
    merged.dropna(subset=["FactValueNumeric"], inplace=True)
    merged["Percentage of cause-specific deaths out of total deaths"] = pd.to_numeric(
        merged["Percentage of cause-specific deaths out of total deaths"], errors="coerce"
    )
    merged["FactValueNumeric"] = pd.to_numeric(merged["FactValueNumeric"], errors="coerce")

    for col, target in [
        ("Number", "NormalizationForNumber"),
        ("Percentage of cause-specific deaths out of total deaths", "NormalizationForPerDeath"),
        ("Age-standardized death rate per 100 000 standard population",
         "NormalizationForAgeStandardizedDeathRate"),
        ("FactValueNumericLow", "NormalizationForFactValueNumericLow"),
        ("FactValueNumericHigh", "NormalizationForFactValueNumericHigh"),
        ("FactValueNumeric", "NormalizationForFactValueNumeric"),
    ]:
        s = merged[col]
        merged[target] = (s - s.min()) / (s.max() - s.min())
    return merged


@lru_cache(maxsize=1)
def load_sex_age_breakdown() -> pd.DataFrame:
    """Cinsiyet ve yaş gruplarına göre ölüm oranları.

    11 gençlik grubu ([0]..[45-49]) (ülke,yıl,cinsiyet) bazında ortalanıp
    [0-49] olarak tek bir grupta birleştirilir.
    """
    df = load_merged()
    df = df[~df["Sex"].isin(["Unknown", "All"])].copy()

    young_groups = [
        "[0]", "[1-4]", "[5-9]", "[10-14]", "[15-19]",
        "[20-24]", "[25-29]", "[30-34]", "[35-39]", "[40-44]", "[45-49]",
    ]
    keys = ["Country Code", "Year", "Sex"]
    young_mean = (
        df[df["Age Group"].isin(young_groups)]
        .groupby(keys, observed=True)["NormalizationForPerDeath"]
        .mean()
        .rename("_young_mean")
    )

    zero_mask = df["Age Group"] == "[0]"
    zero_rows = df.loc[zero_mask].merge(young_mean, on=keys, how="left")
    df.loc[zero_mask, "NormalizationForPerDeath"] = zero_rows["_young_mean"].values
    df.loc[zero_mask, "Age Group"] = "[0-49]"
    df = df[~df["Age Group"].isin(young_groups[1:])]
    return df


@lru_cache(maxsize=1)
def world_radar_means() -> np.ndarray:
    """5 metriğin dünya ortalaması (radar grafiği baseline'ı)."""
    df = load_merged()
    radar = np.empty(5)
    radar[0] = df["NormalizationForNumber"].mean() * 10
    radar[1] = df["NormalizationForPerDeath"].mean()
    radar[2] = df["NormalizationForAgeStandardizedDeathRate"].mean()
    radar[3] = df["NormalizationForFactValueNumericLow"].mean()
    radar[4] = df["NormalizationForFactValueNumericHigh"].mean()
    return radar


@lru_cache(maxsize=1)
def world_residence_means() -> dict[str, float]:
    """Yerleşim türüne göre dünya PM2.5 ortalaması (pasta grafiği için)."""
    df = load_merged()
    return {
        kind: df[(df["Dim1_y"] == kind) & (df["Age group code"] == "Age_all")][
            "FactValueNumeric"
        ].mean()
        for kind in ("Cities", "Towns", "Urban", "Rural", "Total")
    }
