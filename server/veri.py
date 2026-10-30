"""data/ altındaki JSON dosyalarını yükler ve ortak yardımcıları sağlar."""

from __future__ import annotations

import json
import os
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
    "Prototip: ürün bilgileri orzax.com.tr ürün sayfalarından alınmıştır ve katalog yalnızca Orzax ürünlerini içerir. "
    "Etkileşim kuralları, karne eşikleri ve kanıt kartları medikal kurul onayı bekler."
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
    return katalog_dogrula(_yukle("urunler.json")["urunler"])


# --------------------------------------------------------------------------- #
# Katalog doğrulaması: şüpheli satırlar karantinaya alınır, hesaplamalara katılmaz.
# --------------------------------------------------------------------------- #

# Etiketteki miktarın beslenme referans değeri (BRD) yüzdesine bölümü, o maddenin BRD'sini verir. Bir maddenin
# katalogdaki ürünlerden çıkan BRD'lerinin ortancası esas alınır; bir satır bu değerin yarısı ile iki katı dışında
# kalıyorsa miktar ile yüzde birbirini tutmuyor demektir. Kural en az KONSENSUS_EN_AZ satırı olan maddelere uygulanır.
BRD_TOLERANSI = 2
KONSENSUS_EN_AZ = 3
_BIRIM_ADLARI = {1_000: ("mg", "µg"), 1 / 1_000: ("µg", "mg")}


def brd_yuzdesi(metin: str | None) -> float | None:
    """'%500', '%9285,70', 'NE* %100' → sayı; '**' (BRD yok) ya da boş → None."""
    m = re.search(r"\d[\d.,]*", metin or "")
    if not m:
        return None
    sayi = m.group(0)
    if "," in sayi:
        sayi = sayi.replace(".", "").replace(",", ".")
    return float(sayi) or None


def _ima_edilen_brd(em_id: str, satir: dict) -> float | None:
    std = standart_miktar(em_id, satir["miktar"], satir["birim"])
    yuzde = brd_yuzdesi(satir["brd"])
    return std * 100 / yuzde if std and yuzde else None


def katalog_dogrula(liste: list[dict]) -> list[dict]:
    """Her içerik satırına, şüpheliyse 'karantina' alanı ekler: gerekçe ve varsa olası doğru birim."""
    tanimli = kurallar()["etken_maddeler"]
    satirlar = [(e["etken_madde"], e) for u in liste for e in u["etken_maddeler"] if e["etken_madde"] in tanimli]
    orneklem: dict[str, list[float]] = {}
    for em_id, e in satirlar:
        b = _ima_edilen_brd(em_id, e)
        if b:
            orneklem.setdefault(em_id, []).append(b)
    konsensus = {em_id: sorted(v)[len(v) // 2] for em_id, v in orneklem.items() if len(v) >= KONSENSUS_EN_AZ}

    for em_id, e in satirlar:
        e.pop("karantina", None)
        if e["miktar"] is None and e["miktar_metni"] and _birim_kodu(tanimli[em_id]["birim"]) in ("g", "mg", "ug"):
            # Ayrıştırıcı miktarı okuyamadı ya da makul bulmadı (birimsiz, üst sınırın çok üstünde).
            e["karantina"] = {"gerekce": " ".join(e["okuma_notlari"]) or f"'{e['miktar_metni']}' okunamadı."}
            continue
        b = _ima_edilen_brd(em_id, e)
        if b is None or em_id not in konsensus:
            continue
        oran = b / konsensus[em_id]
        if 1 / BRD_TOLERANSI <= oran <= BRD_TOLERANSI:
            continue
        kayit = {"gerekce": (
            f"Etiketteki miktar ({e['miktar_metni']}) ile beslenme referans değeri yüzdesi ({e['brd']}) birbirini tutmuyor."
        )}
        for katsayi, (eski, yeni) in _BIRIM_ADLARI.items():
            if _birim_kodu(e["birim"]) == _birim_kodu(eski) and katsayi / BRD_TOLERANSI <= oran <= katsayi * BRD_TOLERANSI:
                kayit["olasi_birim"] = yeni
                kayit["gerekce"] += f" Yüzdeyle tutarlı birim {yeni}; sitedeki birim büyük olasılıkla hatalı."
        e["karantina"] = kayit
    return liste


def satir_miktari(satir: dict) -> float | None:
    """İçerik satırının standart birimdeki miktarı; karantinadaki ya da çevrilemeyen satırda None."""
    if satir.get("karantina") or not satir["etken_madde"]:
        return None
    return standart_miktar(satir["etken_madde"], satir["miktar"], satir["birim"])


@lru_cache(maxsize=1)
def kurallar() -> dict:
    return _yukle("kurallar.json")


@lru_cache(maxsize=1)
def karne_kurallari() -> list[dict]:
    return _yukle("karne_kurallari.json")["kurallar"]


@lru_cache(maxsize=1)
def katalog_tarihi() -> str:
    return _yukle("urunler.json")["erisim_tarihi"]


@lru_cache(maxsize=1)
def beyanlar() -> dict:
    return _yukle("beyanlar/beyanlar.json")["beyanlar"]


@lru_cache(maxsize=1)
def urun_beyanlari() -> dict:
    """Ürün id'si → ürün sayfasındaki sağlık ve beslenme beyanları."""
    return _yukle("beyanlar/urun_beyanlari.json")["urunler"]


@lru_cache(maxsize=1)
def _zorunlu_uyarilar() -> dict:
    return _yukle("zorunlu_uyarilar.json")["uyarilar"]


def zorunlu_uyarilar(em_id: str) -> list[dict]:
    """Kanıt kartından bağımsız güvenlik uyarıları. Kurul onayı beklerken de (taslak etiketiyle) sunulur."""
    return _zorunlu_uyarilar().get(em_id, [])


@lru_cache(maxsize=1)
def kaynak_kayitlari() -> dict:
    return _yukle("kaynaklar.json")["kaynaklar"]


def _kaynak_gorunumu(k: dict) -> dict:
    """Kaynağı yanıt şemasına çevirir: baslik, kurum_veya_dergi, yil, tur, url, pmid."""
    url = k.get("url") or (f"https://doi.org/{k['doi']}" if k.get("doi") else f"https://pubmed.ncbi.nlm.nih.gov/{k['pmid']}/")
    return {
        "baslik": k["baslik"],
        "kurum_veya_dergi": k["kurum_veya_dergi"],
        "yil": k.get("yil"),
        "tur": k["tur"],
        "url": url,
        "pmid": k.get("pmid"),
        **({"erisim_tarihi": k["erisim_tarihi"]} if k.get("erisim_tarihi") else {}),
    }


def kaynaklar(kimlikler, ekler: list[dict] | None = None) -> list[dict]:
    """Kimlikleri yanıt şemasındaki kaynak listesine çevirir. Doğrulanmamış kaynak listeye girmez."""
    kayitlar = kaynak_kayitlari()
    # İnsan incelemesi bekleyen üretici içeriği (yasaklı ifade bulgusu) de gösterilmez.
    liste = [
        _kaynak_gorunumu(kayitlar[k]) for k in dict.fromkeys(kimlikler)
        if kayitlar[k].get("dogrulandi") and kayitlar[k].get("inceleme") != "gerekli"
    ]
    for e in ekler or []:
        if e not in liste:
            liste.append(e)
    return liste


def urun_kaynagi(u: dict) -> dict:
    """Ürün sayfası, üretici içeriği olarak kaynak gösterilir."""
    return {
        "baslik": f"{u['ad']} ürün sayfası",
        "kurum_veya_dergi": u["marka"],
        "yil": int(u["kaynak"]["erisim_tarihi"][:4]),
        "tur": "uretici_icerigi",
        "url": u["kaynak"]["url"],
        "pmid": None,
        "erisim_tarihi": u["kaynak"]["erisim_tarihi"],
    }


def zarf(govde: dict, kaynak_listesi: list[dict]) -> dict:
    """Her araç yanıtına ortak alanları ekler. Her yanıt en az bir kaynak taşır."""
    if not kaynak_listesi:
        raise ValueError("Araç yanıtı kaynaksız olamaz.")
    return {**govde, "kaynaklar": kaynak_listesi, "uyari": UYARI, "gelistirici": GELISTIRICI, "veri_notu": VERI_NOTU}


def etken_madde_id(ad: str) -> str | None:
    """Serbest metinle yazılmış etken madde adını kurallar.json kimliğine çevirir."""
    aranan = normalize(ad)
    for em_id, bilgi in kurallar()["etken_maddeler"].items():
        if aranan in (em_id, normalize(bilgi["ad"])) or aranan in (normalize(e) for e in bilgi["esanlamlar"]):
            return em_id
    return None


def etken_madde_adi(em_id: str) -> str:
    return kurallar()["etken_maddeler"].get(em_id, {}).get("ad", em_id)


def standart_miktar(em_id: str, miktar: float | None, birim: str | None) -> float | None:
    """Miktarı etken maddenin standart birimine çevirir. Çevrilemezse None döner."""
    if miktar is None or birim is None:
        return None
    hedef = _birim_kodu(kurallar()["etken_maddeler"][em_id]["birim"])
    kaynak = _birim_kodu(birim)
    carpan = {"g": 1_000_000, "mg": 1_000, "ug": 1}
    if kaynak == "iu":
        # Uluslararası birim yalnızca D vitamini için çevrilir: 40 IU = 1 µg.
        if em_id != "d3":
            return None
        return (miktar / 40) / carpan[hedef]
    if kaynak not in carpan or hedef not in carpan:
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
                "kaynaklar": kayit["kaynaklar"],
            }
    return None


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


# --------------------------------------------------------------------------- #
# Kanıt tabanı: data/etken_maddeler/<id>/monografi.json ve kartlar/*.json
# --------------------------------------------------------------------------- #

def taslaklar_gosterilsin() -> bool:
    """Kurul onayı almamış kartlar yalnızca TB_TASLAK_GOSTER=1 iken (test ve deneme) sunulur."""
    return os.environ.get("TB_TASLAK_GOSTER") == "1"


@lru_cache(maxsize=1)
def _monografiler() -> dict[str, dict]:
    sonuc = {}
    for yol in sorted((VERI_DIZINI / "etken_maddeler").glob("*/monografi.json")):
        m = json.loads(yol.read_text(encoding="utf-8"))
        m["kartlar"] = [
            json.loads(k.read_text(encoding="utf-8")) for k in sorted((yol.parent / "kartlar").glob("*.json"))
        ]
        sonuc[m["id"]] = m
    return sonuc


def monografi(em_id: str) -> dict | None:
    """Sunulabilir monografiyi döndürür: onaylı ya da taslak gösterimi açıkken taslak. Kartlar da aynı süzgeçten geçer."""
    m = _monografiler().get(em_id)
    if m is None or not _sunulabilir(m):
        return None
    return {**m, "kartlar": [k for k in m["kartlar"] if _sunulabilir(k)]}


def kanit_tabani_kimlikleri() -> list[str]:
    return sorted(_monografiler())


def _sunulabilir(kayit: dict) -> bool:
    return kayit["durum"] == "onaylandi" or (kayit["durum"] == "taslak" and taslaklar_gosterilsin())
