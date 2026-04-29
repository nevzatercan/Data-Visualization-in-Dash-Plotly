"""Dünya ülkeleri GeoJSON dosyasını indir ve assets/geojson/ klasörüne kaydet.

Kaynak: Natural Earth 110m admin-0 ülke sınırları (datasets/geo-countries).
Feature property `ISO_A3` → WHO veri setindeki 3-harfli ISO kodlarıyla eşleşir.

Tek seferlik çalıştır:
    python scripts/fetch_countries_geojson.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import urlretrieve

DEST = Path(__file__).resolve().parent.parent / "assets" / "geojson" / "countries.geojson"

URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"Zaten mevcut: {DEST}  ({DEST.stat().st_size // 1024} KB)")
        sys.exit(0)

    print(f"İndiriliyor: {URL}")
    tmp, _ = urlretrieve(URL)
    # Doğrulama: geçerli GeoJSON mi?
    with open(tmp) as f:
        data = json.load(f)
    n = len(data.get("features", []))
    print(f"  {n} ülke özelliği doğrulandı.")

    Path(tmp).replace(DEST)
    print(f"Kaydedildi: {DEST}  ({DEST.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
