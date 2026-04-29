"""Grafik fonksiyonları için smoke test'ler.

Hem verisi tam ülke hem verisi olmayan ülke (ZZZ) için her grafik
fonksiyonunun exception atmadan dict döndürmesini doğrular. Eksik
veri kontrolü Faz 2'nin temel hedefiydi: 'IndexError ile çökmeme'.

pasta/balon hariç (Wikipedia + restcountries network'üne bağımlı,
Faz 3'te statik dosyalara taşınacak).
"""

from __future__ import annotations

import pytest

import app


@pytest.fixture(autouse=True)
def setup_module_globals():
    """histogram/cizgikutu için country_name globalleri lazım."""
    app.country_name = "Türkiye"
    app.country_name_english = "Turkey"


CHART_FUNCTIONS = [
    pytest.param(lambda iso: app.histogram(2018, iso), id="histogram"),
    pytest.param(lambda iso: app.cizgikutu(iso), id="cizgikutu"),
    pytest.param(lambda iso: app.cizgi(iso), id="cizgi"),
    pytest.param(lambda iso: app.gösterge(2018, iso), id="gösterge"),
    pytest.param(lambda iso: app.kursun(iso), id="kursun"),
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
    """display_hover_data bir Dash callback'i; doğrudan çağrılamıyor
    (callback context lazım) — bu yüzden underlying logic'i radar
    metric'leri üzerinden test edelim."""
    from dashapp.transforms import filter_total, safe_first
    from dashapp.data_loader import load_merged

    df = load_merged()
    result = filter_total(df, year=2018, country="ZZZ")
    assert result.empty
    # Empty Series'ten safe_first NaN değil default'u dönmeli
    assert safe_first(result["NormalizationForNumber"], default=0) == 0
