"""Chart modülleri ve utils için Faz 3 testleri.

Her grafik modülü ``figure(...)`` ile çağrıldığında:
- dict dönmeli
- exception fırlatmamalı
- ülke verisi yoksa da çökmemeli

Ayrıca borders ve translations utility'leri test edilir.
"""

from __future__ import annotations

import pytest

import dashapp.charts.balon as balon_mod
import dashapp.charts.cizgi as cizgi_mod
import dashapp.charts.cizgikutu as cizgikutu_mod
import dashapp.charts.gosterge as gosterge_mod
import dashapp.charts.histogram as histogram_mod
import dashapp.charts.kursun as kursun_mod
import dashapp.charts.linearea as linearea_mod
import dashapp.charts.pasta as pasta_mod
import dashapp.charts.radar as radar_mod
import dashapp.charts.sunburst as sunburst_mod
from dashapp.utils.borders import get_neighbors
from dashapp.utils.translations import to_turkish


# ---------------------------------------------------------------------------
# Chart modülleri — TUR (veri var)
# ---------------------------------------------------------------------------

def test_histogram_tur():
    result = histogram_mod.figure(2018, "TUR", country_name="Türkiye")
    assert isinstance(result, dict)


def test_cizgikutu_tur():
    result = cizgikutu_mod.figure("TUR", country_name_english="Turkey")
    assert isinstance(result, dict)


def test_cizgi_tur():
    result = cizgi_mod.figure("TUR", country_name="Türkiye")
    assert isinstance(result, dict)


def test_pasta_tur():
    result = pasta_mod.figure(2018, "TUR", country_name="Türkiye")
    assert isinstance(result, dict)


def test_balon_tur():
    result = balon_mod.figure(2018, "TUR", country_name="Türkiye")
    assert isinstance(result, dict)


def test_gosterge_tur():
    result = gosterge_mod.figure(2018, "TUR")
    assert isinstance(result, dict)


def test_kursun_tur():
    result = kursun_mod.figure("TUR")
    assert isinstance(result, dict)


def test_sunburst():
    result = sunburst_mod.figure()
    assert isinstance(result, dict)


def test_linearea():
    result = linearea_mod.figure()
    assert isinstance(result, dict)


def test_radar_tur():
    result = radar_mod.figure("TUR", 2018)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Chart modülleri — ZZZ (veri yok)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fn", [
    lambda: histogram_mod.figure(2018, "ZZZ"),
    lambda: cizgikutu_mod.figure("ZZZ"),
    lambda: cizgi_mod.figure("ZZZ"),
    lambda: pasta_mod.figure(2018, "ZZZ"),
    lambda: balon_mod.figure(2018, "ZZZ"),
    lambda: gosterge_mod.figure(2018, "ZZZ"),
    lambda: kursun_mod.figure("ZZZ"),
    lambda: radar_mod.figure("ZZZ", 2018),
], ids=["histogram", "cizgikutu", "cizgi", "pasta", "balon", "gosterge", "kursun", "radar"])
def test_chart_module_missing_country_no_crash(fn):
    result = fn()
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# borders utility
# ---------------------------------------------------------------------------

def test_get_neighbors_tur():
    neighbors = get_neighbors("TUR")
    assert isinstance(neighbors, list)
    assert len(neighbors) > 0
    assert "IRN" in neighbors or "GRC" in neighbors  # Türkiye komşuları


def test_get_neighbors_jpn():
    """Ada ülkeleri boş liste döndürmeli."""
    neighbors = get_neighbors("JPN")
    assert neighbors == []


def test_get_neighbors_unknown():
    """Bilinmeyen ISO kodu için boş liste döndürmeli."""
    neighbors = get_neighbors("ZZZ")
    assert neighbors == []


# ---------------------------------------------------------------------------
# translations utility
# ---------------------------------------------------------------------------

def test_to_turkish_known():
    assert to_turkish("Turkey") == "Türkiye"
    assert to_turkish("Germany") == "Almanya"
    assert to_turkish("Japan") == "Japonya"


def test_to_turkish_fallback():
    """Sözlükte olmayan isim orijinalini döndürmeli."""
    result = to_turkish("SomeUnknownCountryXYZ")
    assert result == "SomeUnknownCountryXYZ"


def test_to_turkish_coverage():
    """En az 150 ülke eşleme var."""
    from dashapp.utils.translations import COUNTRY_TR
    assert len(COUNTRY_TR) >= 150


# ---------------------------------------------------------------------------
# Balon — ZeroDivisionError guard
# ---------------------------------------------------------------------------

def test_balon_island_no_crash():
    """Komşusu olmayan ada ülkesi (JPN) için ZeroDivisionError olmamalı."""
    result = balon_mod.figure(2018, "JPN", country_name="Japonya")
    assert isinstance(result, dict)
