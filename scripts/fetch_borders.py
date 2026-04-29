#!/usr/bin/env python3
"""Restcountries.com'dan komşu ülke verilerini çekip data/static/borders.json'a yazar.

Tek seferlik script — ağ bağlantısı gerektirir.
Çıktı: {"TUR": ["ARM", "AZE", ...], ...}

Kullanım:
    python scripts/fetch_borders.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "static" / "borders.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://restcountries.com/v3.1/all?fields=cca3,borders"
FALLBACK_URL = "https://restcountries.com/v3.1/alpha/{code}?fields=cca3,borders"


def fetch_all() -> dict[str, list[str]]:
    """Tüm ülkeleri tek API çağrısıyla al."""
    try:
        resp = requests.get(BASE_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {item["cca3"]: item.get("borders", []) for item in data}
    except Exception as exc:
        print(f"Toplu çekme başarısız: {exc}  — tek tek denenecek")
        return {}


def fetch_one(code: str) -> list[str]:
    """Tek ülke çek (fallback)."""
    try:
        resp = requests.get(FALLBACK_URL.format(code=code), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            item = data[0] if isinstance(data, list) else data
            return item.get("borders", [])
    except Exception:
        pass
    return []


def main() -> None:
    print("Komşu verisi çekiliyor…")
    borders = fetch_all()

    if not borders:
        # Fallback: veri setindeki ISO3 kodlarını bir şekilde doldur
        print("Toplu çekme başarısız, bireysel çekmeye geçiliyor…")
        try:
            from dashapp.data_loader import load_air
            codes = load_air()["SpatialDimValueCode"].dropna().unique().tolist()
        except Exception:
            codes = []

        for i, code in enumerate(codes):
            borders[code] = fetch_one(code)
            if i % 20 == 0:
                print(f"  {i}/{len(codes)} tamamlandı")
            time.sleep(0.05)

    OUTPUT.write_text(json.dumps(borders, ensure_ascii=False, indent=2))
    print(f"Tamamlandı: {len(borders)} ülke → {OUTPUT}")


if __name__ == "__main__":
    main()
