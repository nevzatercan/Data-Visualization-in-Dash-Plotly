"""Grafik modülleri için smoke testler.

Her chart modülünün ``figure(...)`` metodunu doğrudan çağırır.
Hem verisi tam ülke (TUR) hem verisi olmayan ülke (ZZZ) için
exception atmadan dict döndürmesini doğrular.

Not: Bu testler Faz 4 sonrası app.py wrapper fonksiyonlarına
bağımlılıktan arındırılmıştır; chart modülleri doğrudan test edilir.
"""

from __future__ import annotations

import pytest

import dashapp.charts.histogram as _histogram
import dashapp.charts.cizgikutu as _cizgikutu
import dashapp.charts.cizgi as _cizgi
import dashapp.charts.gosterge as _gosterge
import dashapp.charts.kursun as _kursun


CHART_FUNCTIONS = [
    pytest.param(lambda iso: _histogram.figure(2018, iso, country_name="Türkiye"), id="histogram"),
    pytest.param(lambda iso: _cizgikutu.figure(iso, country_name_english="Turkey"), id="cizgikutu"),
    pytest.param(lambda iso: _cizgi.figure(iso, country_name="Türkiye"), id="cizgi"),
    pytest.param(lambda iso: _gosterge.figure(2018, iso), id="gösterge"),
    pytest.param(lambda iso: _kursun.figure(iso), id="kursun"),
]


@pytest.mark.parametrize("chart_fn", CHART_FUNCTIONS)
def test_chart_with_existing_country(chart_fn):
    """Verisi tam ülkede grafik fonksiyonu dict döndürmeli."""
    result = chart_fn("TUR")
    assert isinstance(result, dict)


@pytest.mark.parametrize("chart_fn", CHART_FUNCTIONS)
def test_chart_with_missing_country_does_not_crash(chart_fn):
    """Verisi olmayan ülkede çökmemeli — Faz 2'nin asıl hedefi."""
    result = chart_fn("ZZZ")
    assert isinstance(result, dict)


@pytest.mark.parametrize("chart_fn", CHART_FUNCTIONS)
def test_chart_with_mng_irn_does_not_crash(chart_fn):
    """Eskiden hover'dan elenen ülkeler artık tıklamada da çalışmalı."""
    for iso in ("MNG", "IRN"):
        result = chart_fn(iso)
        assert isinstance(result, dict), f"{iso} için crash"


def test_radar_hover_no_crash_on_empty_country():
    """Empty country için radar safe_first default döndürmeli."""
    from dashapp.transforms import filter_total, safe_first
    from dashapp.data_loader import load_merged

    df = load_merged()
    result = filter_total(df, year=2018, country="ZZZ")
    assert result.empty
    assert safe_first(result["NormalizationForNumber"], default=0) == 0
