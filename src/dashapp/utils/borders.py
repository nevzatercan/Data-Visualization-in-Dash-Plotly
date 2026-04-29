"""Statik komşu ülke eşlemesi.

``data/static/borders.json`` dosyasından yüklenir.  Dosya
``scripts/fetch_borders.py`` ile üretilir; kaynak kodu değişikliği
gerektirmeden yeniden çekilebilir.

Kullanım::

    from dashapp.utils.borders import get_neighbors

    neighbors = get_neighbors("TUR")   # ["ARM", "AZE", ...]
    neighbors = get_neighbors("JPN")   # []   (ada ülke)
    neighbors = get_neighbors("ZZZ")   # []   (bilinmeyen)
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_BORDERS_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "static" / "borders.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, list[str]]:
    if _BORDERS_FILE.exists():
        return json.loads(_BORDERS_FILE.read_text(encoding="utf-8"))
    return {}


def get_neighbors(iso3: str) -> list[str]:
    """``iso3`` kodlu ülkenin komşularını döndür (liste boş olabilir)."""
    return _load().get(iso3, [])
