"""dcc.Store bileşenleri — uygulama genelindeki state.

Her store ``storage_type='memory'`` olarak tanımlanmıştır:
- Sekme bazlı izolasyon sağlar (multi-user güvenli).
- Sayfa yenilenmesinde sıfırlanır (default değerlere döner).

Stores
------
viewport-store : {width: int, height: int}
    Tarayıcı boyutu. JS clientside callback tarafından doldurulur.
filter-store   : {is_filtered: int}
    Renk filtre butonu durumu (0 = aktif filtre yok, 1-4 = yeşil/sarı/turuncu/kırmızı).
panel-store    : {is_hidden: int}
    Ülke detay panelinin görünürlük durumu (0 = görünür, 1 = gizli).
hover-store    : {last_iso3: str}
    Son hover edilen ülke ISO-3 kodu. Tekrar render'ı önlemek için kullanılır.
"""

from __future__ import annotations

from dash import dcc


def make_stores() -> list:
    """4 dcc.Store bileşenini liste olarak döndürür."""
    return [
        dcc.Store(id="viewport-store", storage_type="memory", data={"width": 1300, "height": 800}),
        dcc.Store(id="filter-store",   storage_type="memory", data={"is_filtered": 0}),
        dcc.Store(id="panel-store",    storage_type="memory", data={"is_hidden": 1}),
        dcc.Store(id="hover-store",    storage_type="memory", data={"last_iso3": ""}),
    ]
