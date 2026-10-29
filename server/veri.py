"""data/ altındaki JSON dosyalarını yükler ve ortak yardımcıları sağlar."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

VERI_DIZINI = Path(__file__).resolve().parent.parent / "data"

UYARI = (
    "Takviye edici gıdalar ilaç değildir. "
    "Kişisel kullanım miktarı ve tedavi için hekiminize danışın."
)
GELISTIRICI = "Orzax tarafından geliştirilmiştir."
VERI_NOTU = (
    "Prototip: ürün, marka, beyan ve analiz verileri temsilidir; gerçek etiket, "
    "regülasyon onayı veya medikal kurul görüşü yerine geçmez."
)

_TR_HARF = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiucgiosu")


def normalize(metin: str) -> str:
    """Türkçe karakterleri sadeleştirip küçük harfe çevirir; harf/rakam dışını boşluk yapar."""
    metin = metin.translate(_TR_HARF).casefold()
    return re.sub(r"[^a-z0-9]+", " ", metin).strip()


def _yukle(goreli_yol: str) -> dict:
    with open(VERI_DIZINI / goreli_yol, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def urunler() -> list[dict]:
    return _yukle("urunler.json")["urunler"]


@lru_cache(maxsize=1)
def kurallar() -> dict:
    return _yukle("kurallar.json")


@lru_cache(maxsize=1)
def beyanlar() -> dict:
    return _yukle("beyanlar/beyanlar.json")["beyanlar"]


def zarf(govde: dict) -> dict:
    """Her araç yanıtına ortak alanları ekler."""
    return {**govde, "uyari": UYARI, "gelistirici": GELISTIRICI, "veri_notu": VERI_NOTU}


def etken_madde_id(ad: str) -> str | None:
    """Serbest metinle yazılmış etken madde adını kurallar.json kimliğine çevirir."""
    aranan = normalize(ad)
    for em_id, bilgi in kurallar()["etken_maddeler"].items():
        if aranan == em_id or aranan in (normalize(e) for e in bilgi["esanlamlar"]):
            return em_id
    return None


def etken_madde_adi(em_id: str) -> str:
    return kurallar()["etken_maddeler"].get(em_id, {}).get("ad", em_id)


def standart_miktar(em_id: str, miktar: float, birim: str) -> float | None:
    """Miktarı etken maddenin standart birimine çevirir. Çevrilemezse None döner."""
    hedef = _birim_kodu(kurallar()["etken_maddeler"][em_id]["birim"])
    kaynak = _birim_kodu(birim)
    carpan = {"g": 1_000_000, "mg": 1_000, "ug": 1}
    if kaynak == "iu":
        # Uluslararası birim yalnızca D vitamini için çevrilir: 40 IU = 1 µg.
        if em_id != "d3":
            return None
        return (miktar / 40) / carpan[hedef]
    if kaynak not in carpan:
        return None
    return miktar * carpan[kaynak] / carpan[hedef]


def _birim_kodu(birim: str) -> str:
    """'µg', 'μg', 'mcg', 'ug' gibi yazımları tek koda indirir."""
    b = birim.strip().casefold().replace("\u03bc", "u").replace("\u00b5", "u")
    return {"mcg": "ug", "iu": "iu", "ui": "iu"}.get(b, b)


def ust_sinir(em_id: str, yas: float | None) -> dict | None:
    """Yaşa uygun üst sınır kaydını döndürür; tanımlı değilse None."""
    kayit = kurallar()["ust_sinirlar"].get(em_id)
    if not kayit or yas is None:
        return None
    for d in kayit["degerler"]:
        if yas >= d["yas_min"] and (d["yas_max"] is None or yas < d["yas_max"] + 1):
            return {
                "deger": d["deger"],
                "birim": kurallar()["etken_maddeler"][em_id]["birim"],
                "tur": kayit["tur"],
                "kapsam": kayit["kapsam"],
                "kaynak": kayit["kaynak"],
            }
    return None


def seffaflik(urun: dict) -> dict:
    mensei = urun.get("mensei") or {}
    rozet = bool(
        urun.get("parti_analizi_yayimliyor")
        and mensei.get("uretim_ulkesi")
        and mensei.get("hammadde_kaynagi")
    )
    return {
        "parti_analizi": "Yayımlıyor" if urun.get("parti_analizi_yayimliyor") else "Yayımlamıyor",
        "mensei": "Açık" if mensei.get("uretim_ulkesi") else "Belirtilmemiş",
        "hammadde_kaynagi": "Açık" if mensei.get("hammadde_kaynagi") else "Belirtilmemiş",
        "seffaflik_rozeti": rozet,
        "rozet_olcutu": "Parti analizi, hammadde kaynağı ve menşe birlikte yayımlanıyorsa verilir.",
    }


def urun_ara(sorgu: str) -> list[dict]:
    """Ürün adına göre arar. Tam eşleşme varsa yalnız onu, yoksa tüm kelimeleri içerenleri döndürür."""
    s = normalize(sorgu)
    if not s:
        return []
    tam = [u for u in urunler() if normalize(u["ad"]) == s or u["id"] == sorgu.strip()]
    if tam:
        return tam
    kelimeler = s.split()
    return [
        u for u in urunler()
        if all(k in normalize(u["ad"]).split() or k in normalize(u["ad"]).replace(" ", "") for k in kelimeler)
    ]
