"""Toplu kullanım sayaçları (v0.3 Bölüm 11). Kişisel veri tutulmaz.

Yalnızca şu alanlar sayılır: araç adı, hedef kodu, etken madde kimliği (kural tablosundaki sabit kimlik; serbest metin
asla), kart durumu, köprü soruldu ve yaş aralığı. Kullanıcının yazdığı metin, cinsiyet, gebelik, ilaç grubu ve yaşın
kendisi tutulmaz. Sayaçlar bellektedir; sunucu yeniden başlarsa sıfırlanır. Diske ve loga yazılmaz.

Haftalık çıktı ("kartı olmayan en çok sorulan 5 madde") `TB_SAYAC_ANAHTARI` tanımlıysa `/sayaclar` adresinden,
`Authorization: Bearer <anahtar>` başlığıyla alınır; anahtar tanımlı değilse adres 404 döner.
"""

from __future__ import annotations

import threading
from collections import Counter
from datetime import datetime, timezone

from . import veri

_KILIT = threading.Lock()
_SAYACLAR: dict[str, Counter] = {}
_BASLANGIC = datetime.now(timezone.utc).isoformat(timespec="seconds")
# Kanıt kartlı derinlik araçları: kapıdan sonra çağrılmaları köprünün kabul edildiğine dair dolaylı işarettir.
DERINLIK_ARACLARI = {"etken_madde_rehberi", "urun_rehberi", "karsilastir", "kisisel_rutin", "yasam_karnesi"}


def yas_araligi(yas: int | None) -> str | None:
    if yas is None:
        return None
    return "1–10" if yas <= 10 else "11–17" if yas <= 17 else "18–64" if yas <= 64 else "65 ve üzeri"


def _artir(ad: str, anahtar: str) -> None:
    _SAYACLAR.setdefault(ad, Counter())[anahtar] += 1


def _madde_kimligi(ad: str | None) -> str | None:
    """Yalnızca kural tablosunda tanımlı kimlik döner; tanınmayan serbest metin 'tanimsiz' sayılır."""
    if not ad:
        return None
    from .araclar import _rehber_id  # döngüsel içe aktarmayı önler

    return _rehber_id(ad) or "tanimsiz"


def kaydet(arac: str, yanit: dict, *, etken_madde: str | None = None, yas: int | None = None) -> None:
    with _KILIT:
        _artir("arac", arac)
        if yanit.get("hedef"):
            _artir("hedef", yanit["hedef"])
        kimlikler = []
        if etken_madde:
            kimlikler.append(_madde_kimligi(etken_madde))
        for m in yanit.get("maddeler", []):
            kimlikler.append(_madde_kimligi(m.get("etken_madde", "").split(" (")[0]))
        for em_id in filter(None, kimlikler):
            _artir("etken_madde", em_id)
            durum = veri.kart_durumu(em_id) if em_id != "tanimsiz" else "tanimsiz"
            _artir("kart_durumu", f"{em_id}:{durum}")
            if durum in (veri.KART_HAZIRLANIYOR, "tanimsiz"):
                _artir("kartsiz_madde", em_id)
        if yanit.get("kopru"):
            _artir("kopru", "soruldu")
        if arac in DERINLIK_ARACLARI:
            _artir("kopru", f"derinlik_cagrisi:{arac}")
        if yas_araligi(yas):
            _artir("yas_araligi", yas_araligi(yas))


def rapor() -> dict:
    with _KILIT:
        kopya = {ad: dict(c) for ad, c in _SAYACLAR.items()}
        kartsiz = _SAYACLAR.get("kartsiz_madde", Counter()).most_common(5)
    return {
        "baslangic": _BASLANGIC,
        "sayaclar": kopya,
        "karti_olmayan_en_cok_sorulan_5_madde": [{"etken_madde": k, "sayi": n} for k, n in kartsiz],
        "not": ("Toplu sayaçlardır; kişisel veri ve serbest metin tutulmaz. 'derinlik_cagrisi' köprünün kabul edildiğine "
                "dair dolaylı göstergedir: durumsuz sunucu aynı sohbetin çağrılarını birbirine bağlamaz."),
    }


def sifirla() -> None:
    with _KILIT:
        _SAYACLAR.clear()
