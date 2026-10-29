"""orzax.com.tr ürün sayfalarından katalog verisini çıkarır.

Kullanım:
    python scripts/orzax_katalog.py indir     # sitemap'teki Türkçe ürün sayfalarını data/ham/orzax/ altına indirir
    python scripts/orzax_katalog.py ayristir  # önbellekteki sayfalardan data/urunler.json üretir

Yalnızca etiket bilgisi alınır: içerik tablosu, bileşim, sağlık beyanı, kullanım şekli.
Fiyat ve tanıtım metni alınmaz. Reçeteli ürünler kapsam dışıdır.
Beyanlar data/beyanlar/urun_beyanlari.json dosyasına ayrı yazılır.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "data" / "ham" / "orzax"
SAYFALAR = HAM / "sayfalar"
CIKTI = KOK / "data" / "urunler.json"
BEYANLAR = KOK / "data" / "beyanlar" / "urun_beyanlari.json"
KURALLAR = KOK / "data" / "kurallar.json"
SITE = "https://www.orzax.com.tr"
SITEMAPLER = ["product-sitemap1.xml", "product-sitemap2.xml"]
BEKLEME_SN = 1.0
KAPSAM_DISI_KATEGORI = {"Reçeteli Ürünler"}

_TR_HARF = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiucgiosu")


def normalize(metin: str) -> str:
    metin = metin.translate(_TR_HARF).casefold()
    return re.sub(r"[^a-z0-9]+", " ", metin).strip()


# --------------------------------------------------------------------------- #
# İndirme
# --------------------------------------------------------------------------- #


def _getir(url: str) -> tuple[str, str]:
    istek = urllib.request.Request(url, headers={"User-Agent": "TakviyeBilimi-katalog/0.1"})
    with urllib.request.urlopen(istek, timeout=30) as yanit:
        return yanit.geturl(), yanit.read().decode("utf-8", errors="replace")


def indir() -> None:
    SAYFALAR.mkdir(parents=True, exist_ok=True)
    urller: list[str] = []
    for sm in SITEMAPLER:
        _, xml = _getir(f"{SITE}/{sm}")
        urller += re.findall(r"<loc>([^<]+)</loc>", xml)
    urller = [u for u in urller if "/en/" not in u and not u.rstrip("/").endswith("urunlerimiz")
              and not re.search(r"\.(jpe?g|png|webp)$", u)]
    yonlenen = {}
    for u in urller:
        dosya = SAYFALAR / f"{u.rstrip('/').rsplit('/', 1)[-1]}.html"
        if dosya.exists() and dosya.stat().st_size > 0:
            continue
        son_url, govde = _getir(u)
        if son_url.rstrip("/") != u.rstrip("/"):
            yonlenen[u] = son_url
        dosya.write_text(govde, encoding="utf-8")
        time.sleep(BEKLEME_SN)
    (HAM / "indirme.json").write_text(json.dumps({
        "tarih": dt.date.today().isoformat(), "urller": urller, "yonlenen": yonlenen,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(urller)} URL, {len(yonlenen)} yönlendirme")


# --------------------------------------------------------------------------- #
# Ayrıştırma
# --------------------------------------------------------------------------- #

_MIKTAR = re.compile(
    r"^(?P<sayi>\d[\d.,]*(?:\s*x\s*10\^?\d+)?)\s*(?P<birim>mg|g|µg|μg|mcg|ug|IU|KOB|kob|cfu|CFU|ml|mL)\b(?P<ek>.*)$"
)
_BIRIMSIZ_SAYI = re.compile(r"^\d[\d.,]*$")
# BRD hücresi: yüzde ("%60", "100%", "NE* %100") ya da "beslenme referans değeri yok" işareti ("**").
_BRD = re.compile(r"^(?:NE\*?\s*)?(?:%\s*\d[\d.,]*|\d[\d.,]*\s*%)\*?$|^\*{1,2}$")
_KOSUL = re.compile(r"faydal[ıi] etkinin sağlanabilmesi|olumlu etkinin|faydalı etki", re.I)


def _satirlar(govde: str) -> list[str]:
    govde = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", govde, flags=re.S)
    metin = html.unescape(re.sub(r"<[^>]+>", "\n", govde))
    # Sitede "ş" yerine "ș" (virgüllü s) ve matematik "𝜇" karakterleri geçebiliyor.
    metin = metin.replace("\U0001d707", "µ").replace("μ", "µ").replace("ș", "ş").replace("Ș", "Ş")
    return [re.sub(r"\s+", " ", s).strip() for s in metin.split("\n") if s.strip()]


def _sayi_cevir(s: str) -> float | None:
    if "x" in s.casefold():
        return None
    s = s.replace(" ", "")
    # Türkçe yazım: 1.000 binlik, 2,5 ondalık.
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", s):
        s = s.replace(".", "")
    return float(s.replace(",", "."))


def _birim(b: str) -> str:
    b = b.replace("μ", "µ")
    return {"mcg": "µg", "ug": "µg", "kob": "KOB", "cfu": "KOB", "CFU": "KOB", "mL": "ml"}.get(b, b)


def _bolum(satirlar: list[str], baslik: str, bitisler: tuple[str, ...]) -> list[str]:
    if baslik not in satirlar:
        return []
    i = satirlar.index(baslik) + 1
    j = next((k for k in range(i, len(satirlar)) if satirlar[k] in bitisler or satirlar[k].endswith("₺")), len(satirlar))
    return satirlar[i:j]


def _icerik_tablosu(satirlar: list[str]) -> tuple[str | None, list[dict]]:
    if "İçerik" not in satirlar:
        return None, []
    i = satirlar.index("İçerik") + 1
    porsiyon = None
    if satirlar[i].casefold().startswith("her"):
        porsiyon = satirlar[i].rstrip(":")
        i += 1
    ilk_porsiyon = porsiyon
    satirlar_ = []
    for s in satirlar[i:]:
        # Sütun başlıkları ilk satırla iç içe gelir: Adı, <ad>, Miktarı, <miktar>, *BRD, <brd>
        if s in ("Adı", "Miktarı", "*BRD"):
            continue
        if s.startswith("*Beslenme referans") or s in ("Bileşimi", "Sağlık Beyanı", "Kullanım Şekli"):
            break
        satirlar_.append(s)
    # Hücreler sırayla gelir: ad, miktar, BRD. Sitede bazen BRD ya da miktar hücresi eksik,
    # bazen ad iki kez yazılmış olur. Hücre türüne bakarak okunur; okunamayan değer tahmin edilmez, not düşülür.
    kayitlar: list[dict] = []
    son: dict | None = None
    asama = "ad"  # sıradaki beklenen hücre: ad | miktar | brd

    def yeni(ad: str) -> dict:
        k = {"ad": ad, "porsiyon": porsiyon, "miktar": None, "birim": None, "miktar_metni": None, "brd": None, "okuma_notlari": []}
        kayitlar.append(k)
        return k

    for h in satirlar_:
        if re.match(r"^Her .{1,25}$", h) and not _MIKTAR.search(h):
            # Tablo içinde ikinci porsiyon grubu (ör. "Her Shot'ta").
            if son is not None and asama == "miktar":
                son["okuma_notlari"].append("Miktar hücresi sitede boş.")
            porsiyon, asama = h.rstrip(":"), "ad"
            continue
        if h == "-":
            h = ""
        miktar_mi = _MIKTAR.match(h) or _BIRIMSIZ_SAYI.match(h)
        if asama == "miktar" and son is not None and h == "":
            son["okuma_notlari"].append("Miktar hücresi sitede boş.")
            asama = "brd"
            continue
        if asama == "miktar" and son is not None:
            if miktar_mi:
                m = _MIKTAR.match(h)
                son.update(miktar_metni=h, miktar=_sayi_cevir(m["sayi"]) if m else None,
                           birim=_birim(m["birim"]) if m else None)
                if not m:
                    son["okuma_notlari"].append(f"Miktar sitede birimsiz yazılmış: '{h}'.")
                asama = "brd"
                continue
            if _BRD.match(h):
                son["okuma_notlari"].append("Miktar hücresi sitede boş.")
                son["brd"] = h if h.strip("*") else None
                asama = "ad"
                continue
            if normalize(h) == normalize(son["ad"]):
                continue  # Ad hücresi tekrarlanmış.
            son["okuma_notlari"].append("Miktar hücresi sitede boş.")
            son, asama = yeni(h), "miktar"
            continue
        if asama == "brd" and son is not None:
            if _BRD.match(h):
                son["brd"] = h if h.strip("*") else None
                asama = "ad"
                continue
            if miktar_mi:
                son["okuma_notlari"].append(f"BRD hücresinde miktar yazıyor: '{h}'.")
                asama = "ad"
                continue
            son, asama = yeni(h), "miktar"
            continue
        # asama == "ad"
        if _BRD.match(h) or miktar_mi:
            if son is not None:
                son["okuma_notlari"].append(f"Tabloda sahipsiz hücre: '{h}'.")
            continue
        son, asama = yeni(h), "miktar"
    if son is not None and asama == "miktar":
        son["okuma_notlari"].append("Miktar hücresi sitede boş.")
    return ilk_porsiyon, kayitlar


def _beyanlar(satirlar: list[str]) -> tuple[list[str], list[str], list[str]]:
    ham = _bolum(satirlar, "Sağlık Beyanı", ("Kullanım Şekli", "Bileşimi"))
    saglik, beslenme, kosul = [], [], []
    for s in ham:
        s = s.rstrip("*").strip()
        if not s:
            continue
        if _KOSUL.search(s):
            kosul.append(s)
        elif re.match(r"^bu gıda .* (içerir|kaynağıdır)", s, re.I):
            beslenme.append(s)
        else:
            saglik.append(s)
    return saglik, beslenme, kosul


def _yas(kullanim: str) -> dict:
    k = kullanim.casefold()
    m = re.search(r"(\d+)\s*yaş\s*ve\s*üzeri", k)
    if m:
        return {"min": int(m[1]), "max": None}
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*yaş", k)
    if m:
        ust = None if "yetişkin" in k else int(m[2])
        return {"min": int(m[1]), "max": ust}
    if "yetişkin" in k and "çocuk" not in k:
        return {"min": 18, "max": None}
    return {"min": None, "max": None}


def _etken_madde_eslestir(ad: str, esanlam: dict[str, str]) -> str | None:
    """Etiketteki adı kimliğe çevirir. Yalnızca tam eşleşme: "Magnezyum Bisglisinat" (bileşik) magnezyuma eşlenmez."""
    temiz = re.sub(r"[*+#]+$", "", ad).strip()
    adaylar = [normalize(temiz), normalize(re.sub(r"\(.*?\)", "", temiz))]
    for a in adaylar:
        if a in esanlam:
            return esanlam[a]
    if adaylar[0].startswith("probiyotik karisimi"):
        return "probiyotik"
    return None


_KULLANIM_BIRIMI = (
    r"(?:(?:efervesan|dil ?alti|dilaltina|cignenebilir|softgel|softjel|bitkisel)\s+)*"
    r"(ml|damla|tablet|kapsul|sase|puf|sprey|puskurtme|tup|olcek|shot|jel form|adet|gummy)"
)
_ESBIRIM = {"puskurtme": "sprey", "puf": "sprey"}
_SAYI = r"(\d+(?:,\d+)?)"


def _sade(metin: str) -> str:
    """Türkçe harfleri sadeleştirir, noktalamayı korur ("1-2" aralığı bozulmasın)."""
    return re.sub(r"\s+", " ", metin.translate(_TR_HARF).casefold())


def _gunluk_kullanim(porsiyon: str | None, kullanim: str | None) -> dict | None:
    """Porsiyon ("Her 2 Tablette") ile etiketteki kullanımı ("1 veya 2 tablet") karşılaştırıp günlük çarpanı bulur.

    Çarpan, porsiyon başına miktarın günlük miktara dönüşmesi içindir. Birimler eşleşmezse None döner.
    """
    if not porsiyon or not kullanim:
        return None
    p = re.search(r"her\s*" + _SAYI + r"?\s*" + _KULLANIM_BIRIMI, _sade(porsiyon))
    k_metin = _sade(kullanim)
    k = re.search(_SAYI + r"((?:\s*(?:,|-|–|veya|ya da)\s*\d+(?:,\d+)?)*)\s*" + _KULLANIM_BIRIMI, k_metin)
    if not p or not k:
        return None
    p_birim, k_birim = _ESBIRIM.get(p[2], p[2]), _ESBIRIM.get(k[3], k[3])
    if p_birim != k_birim:
        return None
    sayi = lambda x: float(x.replace(",", "."))
    p_adet = sayi(p[1]) if p[1] else 1.0
    degerler = [sayi(k[1])] + [sayi(x) for x in re.findall(r"\d+(?:,\d+)?", k[2] or "")]
    kez = re.search(r"gunde\s*(\d+)\s*kez", k_metin)
    tekrar = float(kez[1]) if kez else 1.0
    k_min, k_max = min(degerler) * tekrar, max(degerler) * tekrar
    return {"birim": k_birim, "en_az": k_min, "en_cok": k_max,
            "carpan_en_az": k_min / p_adet, "carpan_en_cok": k_max / p_adet}


MAKULLUK_KATSAYISI = 10
_BIRIM_CARPANI = {"g": 1_000_000, "mg": 1_000, "µg": 1}


def _makul_degil(em_id: str, satir: dict, kurallar: dict) -> bool:
    """Porsiyondaki miktar EFSA yetişkin üst sınırının MAKULLUK_KATSAYISI katını aşıyorsa True."""
    sinir = kurallar["ust_sinirlar"].get(em_id, {})
    yetiskin = [d["deger"] for d in sinir.get("degerler", []) if d["yas_max"] is None]
    hedef = kurallar["etken_maddeler"][em_id]["birim"]
    if not yetiskin or satir["miktar"] is None or satir["birim"] not in _BIRIM_CARPANI or hedef not in _BIRIM_CARPANI:
        return False
    standart = satir["miktar"] * _BIRIM_CARPANI[satir["birim"]] / _BIRIM_CARPANI[hedef]
    return standart > MAKULLUK_KATSAYISI * yetiskin[0]


def ayristir() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from json_yaz import yaz

    kurallar = json.loads(KURALLAR.read_text(encoding="utf-8"))
    esanlam = {}
    for em_id, bilgi in kurallar["etken_maddeler"].items():
        esanlam[normalize(em_id)] = em_id
        for e in bilgi["esanlamlar"]:
            esanlam[normalize(e)] = em_id
    indirme = json.loads((HAM / "indirme.json").read_text(encoding="utf-8"))
    tarih = indirme["tarih"]
    urunler, beyanlar, atlanan, eslesmeyen = [], {}, [], {}
    for url in indirme["urller"]:
        if url in indirme["yonlenen"]:
            atlanan.append({"url": url, "neden": "Ürün sayfası yok (seri sayfasına yönleniyor)."})
            continue
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        satirlar = _satirlar((SAYFALAR / f"{slug}.html").read_text(encoding="utf-8"))
        if "Ürünler" not in satirlar:
            atlanan.append({"url": url, "neden": "Ürün şablonu bulunamadı."})
            continue
        i = satirlar.index("Ürünler")
        kategori, ad = satirlar[i + 2], satirlar[i + 3]
        if kategori in KAPSAM_DISI_KATEGORI:
            atlanan.append({"url": url, "neden": f"Kapsam dışı kategori: {kategori}"})
            continue
        porsiyon, tablo = _icerik_tablosu(satirlar)
        if not tablo:
            atlanan.append({"url": url, "neden": "İçerik tablosu okunamadı."})
            continue
        if all(not r["miktar_metni"] for r in tablo):
            atlanan.append({"url": url, "neden": "İçerik tablosunda miktar yok (ör. haricen kullanılan ürün)."})
            continue
        kullanim = _bolum(satirlar, "Kullanım Şekli", ("Kullanım Şekli:",))
        kullanim_metni = next((s for s in kullanim if "₺" not in s and not re.fullmatch(r"[\d.,]+\s*\w+", s)), None)
        etkenler = []
        for r in tablo:
            em_id = _etken_madde_eslestir(r["ad"], esanlam)
            if em_id is None:
                eslesmeyen.setdefault(r["ad"], []).append(ad)
            elif _makul_degil(em_id, r, kurallar):
                # Ör. "25 mg D3 vitamini": birim sitede büyük olasılıkla hatalı. Doğru değer tahmin edilmez;
                # miktar hesaplamalara katılmaz, not düşülür.
                r["okuma_notlari"].append(
                    f"'{r['miktar_metni']}' EFSA yetişkin üst sınırının {MAKULLUK_KATSAYISI} katından fazla; birim sitede "
                    "büyük olasılıkla hatalı. Değer hesaplamalara katılmadı."
                )
                r["miktar"], r["birim"] = None, None
            gunluk = _gunluk_kullanim(r["porsiyon"], kullanim_metni)
            etkenler.append({
                "etiketteki_ad": r["ad"], "etken_madde": em_id, "porsiyon": r["porsiyon"],
                "miktar": r["miktar"], "birim": r["birim"], "miktar_metni": r["miktar_metni"], "brd": r["brd"],
                "gunluk_carpan": None if gunluk is None else gunluk["carpan_en_cok"],
                "okuma_notlari": r["okuma_notlari"],
            })
        bilesim = _bolum(satirlar, "Bileşimi", ("Sağlık Beyanı", "Kullanım Şekli"))
        saglik, beslenme, kosul = _beyanlar(satirlar)
        beyanlar[slug] = {"saglik": saglik, "beslenme": beslenme, "kullanim_kosullari": kosul,
                          "kaynak": {"url": url, "erisim_tarihi": tarih}}
        urunler.append({
            "id": slug,
            "ad": ad,
            "marka": "Orzax",
            "seri": kategori,
            "porsiyon": porsiyon,
            "etken_maddeler": etkenler,
            "bilesim": " ".join(bilesim) or None,
            "etiketteki_kullanim": kullanim_metni,
            "gunluk_kullanim": _gunluk_kullanim(porsiyon, kullanim_metni),
            "yas_siniri": _yas(kullanim_metni or ""),
            "kaynak": {"url": url, "erisim_tarihi": tarih},
        })
    # Sitede aynı adı taşıyan ürünler (ör. iki farklı miktarlı "Ocean Selenyum Tablet") ilk içeriğin miktarıyla ayrılır.
    adlar = [normalize(u["ad"]) for u in urunler]
    for u in urunler:
        if adlar.count(normalize(u["ad"])) > 1:
            u["ad_sitede"] = u["ad"]
            u["ad"] = f"{u['ad']} ({u['etken_maddeler'][0]['miktar_metni']})"
    urunler.sort(key=lambda u: normalize(u["ad"]))
    yaz(CIKTI, {
        "_not": ("Ürün verileri orzax.com.tr ürün sayfalarından scripts/orzax_katalog.py ile alınmıştır. "
                 "Yalnızca etiket bilgisi (içerik, bileşim, kullanım) saklanır; fiyat ve tanıtım metni alınmaz. "
                 "Katalog şu an yalnızca Orzax ürünlerini içerir. Sitedeki tablo hataları 'okuma_notlari' alanında işaretlidir; "
                 "okunamayan değer tahmin edilmez."),
        "erisim_tarihi": tarih,
        "urunler": urunler,
        "atlanan_sayfalar": atlanan,
    })
    yaz(BEYANLAR, {
        "_not": ("Ürün sağlık ve beslenme beyanları, ürün sayfalarındaki metinlerle kelimesi kelimesine saklanır. "
                 "Sayfalar TGK Beslenme ve Sağlık Beyanları Yönetmeliği'ne atıf yapar. 'kullanim_kosullari' beyanın "
                 "yönetmelikteki koşuludur; kişiye doz önerisi değildir."),
        "erisim_tarihi": tarih,
        "urunler": dict(sorted(beyanlar.items())),
    })
    yaz(HAM / "eslesmeyen_etken_maddeler.json", dict(sorted(eslesmeyen.items())))
    print(f"{len(urunler)} ürün, {len(atlanan)} atlanan, {len(eslesmeyen)} eşleşmeyen etken madde adı")


if __name__ == "__main__":
    {"indir": indir, "ayristir": ayristir}[sys.argv[1] if len(sys.argv) > 1 else "ayristir"]()
