#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSÖ ölüm verileri + PM2.5 hava kalitesi + COVID — etkileşimli Dash paneli.

Giriş noktası. Uygulama mantığı src/dashapp/ altında organize edilmiştir:
  data_loader.py  — veri yükleme (lru_cache)
  transforms.py   — filtre ve yardımcı fonksiyonlar
  theme.py        — ortak Plotly layout + renk sabitleri
  layout/         — Dash bileşenleri (toolbar, paneller, modallar, store'lar)
  charts/         — 10 grafik modülü
  callbacks/      — 5 callback modülü; register_callbacks(app) ile bağlanır
"""

from dashapp import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
