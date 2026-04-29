#!/usr/bin/env python3
"""ISO3 → SVG bayrak dosyalarını flagcdn.com'dan indirip assets/img/flags/'a yazar.

Tek seferlik script — ağ bağlantısı gerektirir.
ISO3 kodunu ISO2'ye çevirmek için restcountries.com kullanılır.

Kullanım:
    python scripts/fetch_flags.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
FLAGS_DIR = ROOT / "assets" / "img" / "flags"
FLAGS_DIR.mkdir(parents=True, exist_ok=True)

BORDERS_FILE = ROOT / "data" / "static" / "borders.json"
ISO2_URL = "https://restcountries.com/v3.1/all?fields=cca3,cca2"
FLAG_URL = "https://flagcdn.com/{iso2}.svg"


def get_iso2_map() -> dict[str, str]:
    """ISO3 → ISO2 eşlemesini al."""
    resp = requests.get(ISO2_URL, timeout=30)
    resp.raise_for_status()
    return {item["cca3"]: item["cca2"].lower() for item in resp.json()}


def fetch_flag(iso2: str) -> bytes | None:
    try:
        resp = requests.get(FLAG_URL.format(iso2=iso2), timeout=10)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None


def main() -> None:
    print("ISO3 → ISO2 haritası alınıyor…")
    iso2_map = get_iso2_map()

    # veri setindeki ISO3 kodlarını yükle
    codes: list[str] = []
    try:
        from dashapp.data_loader import load_air
        codes = load_air()["SpatialDimValueCode"].dropna().unique().tolist()
        print(f"Veri setinden {len(codes)} ülke kodu alındı")
    except Exception:
        codes = list(iso2_map.keys())
        print(f"data_loader bulunamadı, tüm ülkeler ({len(codes)}) denenecek")

    downloaded = 0
    skipped = 0
    missing = 0

    for code in codes:
        target = FLAGS_DIR / f"{code}.svg"
        if target.exists():
            skipped += 1
            continue

        iso2 = iso2_map.get(code)
        if not iso2:
            missing += 1
            continue

        data = fetch_flag(iso2)
        if data:
            target.write_bytes(data)
            downloaded += 1
        else:
            missing += 1
        time.sleep(0.03)

    print(f"Tamamlandı: {downloaded} indirildi, {skipped} zaten vardı, {missing} bulunamadı")
    print(f"Bayraklar: {FLAGS_DIR}")


if __name__ == "__main__":
    main()
