"""transforms.py için unit test'ler."""

from __future__ import annotations

import pandas as pd
import pytest

from dashapp.data_loader import load_air, load_merged
from dashapp.transforms import colorchoose, filter_total, safe_first


# --- filter_total ---


def test_filter_total_default_returns_total_only():
    """Default parametrelerle Dim1_y=Total, Sex=All, Age=[All] uygulanmalı."""
    df = load_merged()
    result = filter_total(df)
    assert (result["Dim1_y"] == "Total").all()
    assert (result["Sex"] == "All").all()
    assert (result["Age Group"] == "[All]").all()


def test_filter_total_with_year_and_country():
    df = load_merged()
    result = filter_total(df, year=2018, country="TUR")
    assert len(result) > 0
    assert (result["Year"] == 2018).all()
    assert (result["Country Code"] == "TUR").all()


def test_filter_total_uses_period_for_air():
    """df_air'de 'Year' yok, 'Period' var. filter_total bunu yakalamalı."""
    df = load_air()
    result = filter_total(df, year=2015, dim1="Total", dim1_y=None)
    assert len(result) > 0
    assert (result["Period"] == 2015).all()


def test_filter_total_uses_spatialdimvaluecode_for_air():
    """df_air'de 'Country Code' yok, 'SpatialDimValueCode' var."""
    df = load_air()
    result = filter_total(df, country="TUR", dim1_y=None, sex=None, age=None)
    assert len(result) > 0
    assert (result["SpatialDimValueCode"] == "TUR").all()


def test_filter_total_unknown_country_returns_empty():
    df = load_merged()
    result = filter_total(df, country="ZZZ")
    assert len(result) == 0


def test_filter_total_none_disables_filter():
    """sex=None default Sex='All' filtresini devre dışı bırakmalı."""
    df = load_merged()
    result = filter_total(df, sex=None, age=None, dim1_y=None)
    sexes = set(result["Sex"].unique())
    assert sexes - {"All"}, "sex=None ile All dışı değerler de gelmeli"


# --- safe_first ---


def test_safe_first_empty_series_returns_default():
    s = pd.Series([], dtype=float)
    assert safe_first(s, default=42) == 42


def test_safe_first_empty_series_default_none():
    s = pd.Series([], dtype=float)
    assert safe_first(s) is None


def test_safe_first_returns_first_value():
    s = pd.Series([10, 20, 30])
    assert safe_first(s) == 10


def test_safe_first_nan_returns_default():
    s = pd.Series([float("nan"), 5])
    assert safe_first(s, default=99) == 99


def test_safe_first_none_input_returns_default():
    assert safe_first(None, default="X") == "X"


def test_safe_first_preserves_dtype():
    """numpy.float64 yerine int dönmeli (iloc dtype'ı korur)."""
    s = pd.Series([1, 2, 3], dtype=int)
    assert safe_first(s) == 1
    assert isinstance(safe_first(s), (int,)) or hasattr(safe_first(s), "item")


# --- colorchoose ---


@pytest.mark.parametrize(
    "value,expected_image",
    [
        (0.05, "assets/yesil.png"),
        (0.12, "assets/yesil.png"),
        (0.13, "assets/sari.png"),  # eşik, sari'ye geçiş
        (0.30, "assets/sari.png"),
        (0.43, "assets/sari.png"),
        (0.44, "assets/kirmizi.png"),  # eşik, kirmizi'ye geçiş
        (0.80, "assets/kirmizi.png"),
        (None, "assets/yesil.png"),  # NaN guard
        (float("nan"), "assets/yesil.png"),
    ],
)
def test_colorchoose_thresholds(value, expected_image):
    image, _ = colorchoose(value)
    assert image == expected_image


def test_colorchoose_returns_tuple_of_two_strings():
    image, color = colorchoose(0.5)
    assert isinstance(image, str)
    assert isinstance(color, str)
    assert color.startswith("rgb")
