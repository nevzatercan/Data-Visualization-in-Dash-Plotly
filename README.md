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

veya:

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python app.py
```

Tarayıcıda http://localhost:8050 adresini aç.

## Veri kaynakları

- `death.csv` — DSÖ Solunum yolu hastalıklarına bağlı ölüm verileri
- `air.csv` — DSÖ PM2.5 hava kalitesi verileri (2010-2019)
- `covid.csv` — COVID-19 kümülatif ölüm verileri

## Geliştirme

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Yapı

Proje şu an monolitik tek dosya hâlinde (`app.py`, ~2000 satır). Aşamalı bir modülerleştirme süreci devam ediyor; sonraki commit'lerde `src/dashapp/` altında modüler bir yapıya geçilecek.
