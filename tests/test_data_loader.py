"""Veri yükleme katmanı için smoke test'ler."""

from __future__ import annotations

from dashapp.data_loader import (
    load_air,
    load_covid,
    load_death,
    load_merged,
    load_sex_age_breakdown,
    world_radar_means,
    world_residence_means,
)


def test_load_air_has_expected_columns():
    df = load_air()
    assert len(df) > 0
    assert "Period" in df.columns
    assert "FactValueNumeric" in df.columns
    assert "ParentLocation" in df.columns


def test_load_air_uses_turkish_region_names():
    """ParentLocation Africa/Europe değil, Afrika/Avrupa olmalı."""
    df = load_air()
    regions = set(df["ParentLocation"].dropna().unique())
    assert {"Afrika", "Avrupa", "Amerika"}.issubset(regions)
    assert "Africa" not in regions


def test_load_death_fixes_corrupted_country_names():
    """Kaynak verideki 'T?rkiye' ve 'R?union' düzeltilmiş olmalı."""
    df = load_death()
    names = set(df["Country Name"].dropna().unique())
    assert "Türkiye" in names
    assert "Réunion" in names
    assert "T?rkiye" not in names
    assert "R?union" not in names


def test_load_covid_returns_nonempty():
    df = load_covid()
    assert len(df) > 0
    assert "Name" in df.columns
    assert "Deaths - cumulative total" in df.columns


def test_load_merged_has_normalization_columns():
    df = load_merged()
    assert len(df) > 0
    expected = {
        "NormalizationForNumber",
        "NormalizationForPerDeath",
        "NormalizationForAgeStandardizedDeathRate",
        "NormalizationForFactValueNumericLow",
        "NormalizationForFactValueNumericHigh",
        "NormalizationForFactValueNumeric",
    }
    assert expected.issubset(set(df.columns))


def test_load_sex_age_breakdown_only_aggregate_groups():
    """[0]..[45-49] alt grupları [0-49]'a birleştirilmiş olmalı."""
    df = load_sex_age_breakdown()
    age_groups = set(df["Age Group"].unique())
    assert "[0-49]" in age_groups
    sub_groups = ["[0]", "[1-4]", "[5-9]", "[10-14]", "[15-19]",
                  "[20-24]", "[25-29]", "[30-34]", "[35-39]", "[40-44]", "[45-49]"]
    for sub in sub_groups:
        assert sub not in age_groups, f"{sub} hâlâ var, agregeye giriş başarısız"


def test_load_sex_age_breakdown_no_unknown_or_all_sex():
    """Sex breakdown sadece Male/Female içermeli."""
    df = load_sex_age_breakdown()
    sexes = set(df["Sex"].unique())
    assert sexes == {"Male", "Female"}


def test_world_radar_returns_5_metrics():
    radar = world_radar_means()
    assert len(radar) == 5
    # Normalleştirilmiş değerlerin tümü 0-10 aralığında olmalı (NormalizationForNumber * 10)
    assert all(0 <= v <= 10 for v in radar)


def test_world_residence_has_required_keys():
    means = world_residence_means()
    expected = {"Cities", "Towns", "Urban", "Rural", "Total"}
    assert expected.issubset(means.keys())
    for value in means.values():
        assert value > 0  # PM2.5 ortalamaları pozitif olmalı


def test_lru_cache_returns_same_instance():
    """Aynı çağrı bellek içinde tek kopya tutmalı."""
    a = load_air()
    b = load_air()
    assert a is b
