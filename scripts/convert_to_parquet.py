"""data/raw/*.csv → data/processed/*.parquet dönüşümü.

Tek seferlik, idempotent. Her run'da Parquet dosyaları yeniden üretir.
Parquet, hem ~5x daha küçük hem ~10x daha hızlı yüklenir; ayrıca dtype
bilgilerini ve `category` türlerini korur.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def convert_death() -> None:
    df = pd.read_csv(
        RAW / "death.csv",
        header=6,
        sep=";",
        encoding="utf-8",
        on_bad_lines="warn",
    )
    df.loc[df["Country Code"] == "TUR", "Region Name"] = "Europe"
    df.loc[df["Country Name"] == "T?rkiye", "Country Name"] = "Türkiye"
    df.loc[df["Country Name"] == "R?union", "Country Name"] = "Réunion"
    df.to_parquet(PROCESSED / "death.parquet", index=False)
    print(f"  death.parquet: {len(df):,} satır")


def convert_air() -> None:
    df = pd.read_csv(RAW / "air.csv", header=0, sep=",", encoding="utf-8")
    df.to_parquet(PROCESSED / "air.parquet", index=False)
    print(f"  air.parquet:   {len(df):,} satır")


def convert_covid() -> None:
    df = pd.read_csv(RAW / "covid.csv", header=0, sep=",", encoding="utf-8")
    df.to_parquet(PROCESSED / "covid.parquet", index=False)
    print(f"  covid.parquet: {len(df):,} satır")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    print(f"data/raw/ → data/processed/ (içine yazılıyor: {PROCESSED})")
    convert_death()
    convert_air()
    convert_covid()
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
