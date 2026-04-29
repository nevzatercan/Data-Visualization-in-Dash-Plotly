# Dash Veri Görselleştirme Paneli

DSÖ ölüm verileri, hava kalitesi (PM2.5) ve COVID-19 verilerini birleştiren etkileşimli görselleştirme paneli. 2023'te yazılmış bir bitirme projesinin modernize edilmiş hâli.

## Özellikler

- Choropleth + scatter overlay'lenmiş dünya haritası
- Yıl slider'ı (2010-2019) ve PM2.5 renk-bandı filtreleri
- Ülke tıklamasında: histogram, çizgi, kutu, pasta, balon, gösterge, kurşun grafikleri
- Hover'da dünya vs. ülke karşılaştırması (radar grafiği)
- Bölgesel sunburst ve zaman serisi alan grafikleri

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Veriyi hazırla

Ham CSV'leri Parquet'e çevir (tek seferlik, idempotent):

```bash
python scripts/convert_to_parquet.py
```

Çıktı: `data/processed/{death,air,covid}.parquet`. Boyut: 30 MB → ~4.5 MB.

## Çalıştırma

```bash
python app.py
```

Tarayıcıda http://localhost:8050 adresini aç.

## Veri kaynakları

- `data/raw/death.csv` — DSÖ Solunum yolu hastalıklarına bağlı ölüm verileri
- `data/raw/air.csv` — DSÖ PM2.5 hava kalitesi verileri (2010-2019)
- `data/raw/covid.csv` — COVID-19 kümülatif ölüm verileri

## Geliştirme

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Yapı

```
app.py                    # Dash uygulaması (henüz monolitik, küçülüyor)
src/dashapp/
  data_loader.py          # Parquet'ten lru_cache'li veri yükleme
data/
  raw/*.csv               # Ham veri (versiyon kontrolünde)
  processed/*.parquet     # Türetilmiş veri (gitignore'da)
scripts/
  convert_to_parquet.py   # Tek seferlik dönüşüm
```

Aşamalı modülerleştirme devam ediyor; sonraki fazlarda `transforms.py`, `charts/`, `callbacks/`, `layout/` modülleri eklenecek.
