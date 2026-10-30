"""Araçların iş mantığı. Saf fonksiyonlardır: hiçbir girdi saklanmaz veya loglanmaz."""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from . import veri

# --------------------------------------------------------------------------- #
# 1. urun_rehberi
# --------------------------------------------------------------------------- #


ETIKET_UYARISI_NOTU = "Etiket uyarıları ürün sayfasında yayımlanmıyor; ambalajdaki uyarıları okuyun."
# TB-22: "katkıda bulunur" beyanlarının ne anlama geldiği.
BEYAN_ACIKLAMASI = (
    "Bu ifadeler ürün sayfasındaki sağlık beyanlarıdır; maddenin vücudun normal işleyişine katkısını anlatan yasal "
    "kalıplardır. Eksikliği olmayan birinde yorgunluğu gidereceğini ya da ek fayda sağlayacağını göstermez."
)
PARTI_ANALIZI_NOTU = "Katalogdaki ürünler için yayımlanmış parti analizi bulunmuyor."
DEMO_NOTU = "DEMO: gerçek bir parti analizi değildir; kartın nasıl görüneceğini gösterir."


def _etiket_miktari(em: dict, u: dict) -> str:
    if not em.get("miktar_metni"):
        return "Ürün sayfasında yazmıyor"
    porsiyon = em.get("porsiyon") or u.get("porsiyon")
    return f"{em['miktar_metni']} ({porsiyon.casefold()})" if porsiyon else em["miktar_metni"]


# Etkileşim bayrağında ilaç grubunun kısa adı (v0.3 Ek 2).
_ILAC_KISA = {
    "kan_sulandirici_varfarin": "varfarin", "kan_sulandirici_diger": "diğer kan sulandırıcılar",
    "tiroid_hormonu": "tiroid hormonu", "antibiyotik_kinolon_tetrasiklin": "kinolon/tetrasiklin antibiyotikler",
    "mide_asidi_baskilayici": "mide asidi baskılayıcılar", "metformin": "metformin", "antiepileptik": "sara ilaçları",
    "metotreksat": "metotreksat",
}


def etkilesim_bayraklari(u: dict, ilac_grubu: list[str] | None = None) -> list[dict]:
    """Ürünün içerdiği maddeler için ilaç grubu kuralları: "K vitamini — varfarin: hekime danışın".

    Kullanıcı o ilaç grubunu belirttiyse bayrak kırmızıdır. Kural tablosu medikal kurul onayı bekler.
    """
    kimlikler = {e["etken_madde"] for e in u["etken_maddeler"] if e["etken_madde"]}
    kimlikler |= {veri.KATALOG_GRUBU.get(e, e) for e in kimlikler}
    kullanilan = set(ilac_grubu or [])
    bayraklar = []
    for kural in veri.kurallar()["etkilesimler"]:
        kosul = kural["kosul"]
        gruplar = _liste(kosul.get("ilac_grubu", []))
        maddeler = [e for e in _liste(kosul["etken_madde"]) if e in kimlikler]
        if not gruplar or not maddeler:
            continue
        ilac = ", ".join(dict.fromkeys(_ILAC_KISA.get(g, g) for g in gruplar))
        bayraklar.append({
            "metin": f"{', '.join(veri.etken_madde_adi(e) for e in maddeler)} — {ilac}: hekime danışın",
            "ilac_grubu": gruplar,
            "kirmizi": bool(kullanilan & set(gruplar)),
            "mesaj": kural["mesaj"],
        })
    return bayraklar


# Bileşim metninden okunan özellikler (v0.3 Ek 12). Yalnızca etikette geçen ifade yazılır; geçmiyorsa tahmin edilmez.
_TATLANDIRICI = ["ksilitol", "sukraloz", "steviol glikozit", "stevia", "sorbitol", "maltitol", "izomalt", "eritritol",
                 "aspartam", "asesülfam", "sakarin", "mannitol"]
_SEKER = ["şeker", "glukoz şurubu", "glikoz şurubu", "sakaroz", "fruktoz", "dekstroz", "bal", "invert şeker"]
_D3_KAYNAGI = [("lanolin", "lanolin (koyun yünü yağı)"), ("liken", "liken (bitkisel)"), ("vegan", "vegan olarak belirtilmiş")]
_K_FORMU = re.compile(r"mk[\s-]?[47]|menak\w{0,3}non[\s-]?[47]|fillokinon")


def _gecenler(metin: str, adlar: list[str]) -> list[str]:
    return [a for a in adlar if re.search(rf"(?<![a-zçğıöşü]){re.escape(a)}(?![a-zçğıöşü])", metin)]


def bilesim_ozeti(u: dict) -> dict:
    metin = (u.get("bilesim") or "").casefold()
    kimlikler = {e["etken_madde"] for e in u["etken_maddeler"]}
    ozet: dict = {"tatlandiricilar": _gecenler(metin, _TATLANDIRICI), "seker_ve_seker_kaynaklari": _gecenler(metin, _SEKER)}
    if "d3" in kimlikler:
        ozet["d3_kaynagi"] = "; ".join(d for a, d in _D3_KAYNAGI if a in metin) or "Etikette belirtilmemiş"
    if "k2" in kimlikler:
        m = _K_FORMU.search(metin)
        ozet["k_vitamini_formu"] = ("Etikette belirtilmemiş" if not m else "K1 (fillokinon)" if "fillo" in m.group(0)
                                    else f"MK-{m.group(0)[-1]} (menakinon-{m.group(0)[-1]})")
    ozet["not"] = "Yalnızca bileşim metninde geçen ifadeler yazılır; geçmeyen bilgi tahmin edilmez."
    return ozet


def _urun_karti(u: dict, yas: int | None = None) -> dict:
    etkenler = []
    for em in u["etken_maddeler"]:
        em_id = em["etken_madde"]
        std = veri.satir_miktari(em)
        # v0.3 Ek 10: yaş verildiyse o yaş grubunun EFSA sınırı, verilmediyse yetişkin sınırı.
        sinir = veri.ust_sinir(em_id, 18 if yas is None else yas) if em_id else None
        etkenler.append({
            "etken_madde": em["etiketteki_ad"],
            # "Bu üründeki miktar" bloğu: yalnızca rakam, yorum yok.
            "bu_urundeki_miktar": {
                "etiketteki_miktar": _etiket_miktari(em, u),
                "beslenme_referans_degeri": em["brd"],
                "standart_birimde": None if std is None else f"{_sayi(std)} {veri.kurallar()['etken_maddeler'][em_id]['birim']}",
                "yetiskin_ust_siniri": _sinir_metni(em_id, veri.ust_sinir(em_id, 18)) if em_id else None,
                **({"yas_grubu_ust_siniri": _sinir_metni(em_id, sinir)} if em_id and yas is not None else {}),
            },
            # Görsel kartın EFSA göstergesi için sayılar (standart birimde); metin alanları modelde kalır.
            "olcek": {
                "miktar": std,
                "birim": veri.kurallar()["etken_maddeler"][em_id]["birim"] if em_id else None,
                "ust_sinir": sinir["deger"] if sinir else None,
                "sinir_grubu": "yetişkin" if yas is None else "yaş grubu",
                **({"oran_metni": _oran_metni(std, sinir, yas)} if std is not None and sinir else {}),
            },
            **({"okuma_notu": " ".join(em["okuma_notlari"])} if em["okuma_notlari"] else {}),
            **({"dogrulanamadi": _karantina_metni(em)} if em.get("karantina") else {}),
        })
    beyan = veri.urun_beyanlari().get(u["id"], {})
    return {
        "ad": u["ad"],
        "marka": u["marka"],
        "seri": u["seri"],
        "porsiyon": u["porsiyon"],
        "etken_maddeler": etkenler,
        "bilesim": u["bilesim"],
        "bilesim_ozeti": bilesim_ozeti(u),
        "etiketteki_kullanim": u["etiketteki_kullanim"],
        "yas_siniri": _yas_metni(u["yas_siniri"]),
        "etkilesim_bayraklari": etkilesim_bayraklari(u),
        # v0.3 Ek 9: ilgili madde sayfadan anlaşılmıyorsa liste boş kalır; "Sayfada belirtilmemiş" yazılmaz.
        "urun_sayfasi_beyanlari": [
            {"metin": b["metin"], "ilgili_etken_madde": [veri.etken_madde_adi(e) for e in b["etken_maddeler"]]}
            for b in veri.urun_saglik_beyanlari(u)
        ],
        "beslenme_beyanlari": beyan.get("beslenme", []),
        "beyan_kullanim_kosullari": beyan.get("kullanim_kosullari", []),
        "beyan_notu": "Ürüne ait etki ifadesi yalnızca ürün sayfasındaki bu beyanlardır; regülasyon onayı ayrıca doğrulanmadı.",
        "beyan_aciklamasi": BEYAN_ACIKLAMASI,
        "etiket_uyarilari": ETIKET_UYARISI_NOTU,
        "parti_analizi": "Bu ürün için yayımlanmış parti analizi var." if veri.gercek_parti_analizi_var(u["id"]) else PARTI_ANALIZI_NOTU,
        "urun_sayfasi": u["kaynak"]["url"],
        "erisim_tarihi": u["kaynak"]["erisim_tarihi"],
    }


def _oran_metni(std: float, sinir: dict, yas: int | None) -> str:
    oran = round(std / sinir["deger"] * 100)
    grup = "yetişkin üst sınırının" if yas is None else "yaş grubu üst sınırının"
    return (f"Porsiyonda {_sayi(std)} {sinir['birim']}: {_sayi(sinir['deger'])} {sinir['birim']} olan EFSA {grup} {veri.yuzde(oran)}. "
            "Bu bir güvenlik tavanıdır, alınması gereken miktar değildir.")


def _karantina_metni(em: dict) -> str:
    k = em["karantina"]
    return f"Bu satır doğrulanamadı ve hesaplamalara katılmadı. {k['gerekce']}"


def _urun_kaynaklari(u: dict) -> list[dict]:
    """Ürün sayfası ve karttaki EFSA değerlerinin kaynakları."""
    sinir_kaynaklari = [
        k for em in u["etken_maddeler"] if em["etken_madde"]
        for k in veri.kurallar()["ust_sinirlar"].get(em["etken_madde"], {}).get("kaynaklar", [])
    ]
    return [veri.urun_kaynagi(u), *veri.kaynaklar(sinir_kaynaklari or ["efsa_ul_ozet_2025"])]


def _yas_disinda(ys: dict, yas: float) -> bool:
    return ys["min"] is not None and (yas < ys["min"] or (ys["max"] is not None and yas > ys["max"]))


def urun_rehberi(urun: str, yas: int | None = None) -> dict:
    adaylar = veri.urun_ara(urun)
    if len(adaylar) == 1:
        u = adaylar[0]
        ozet = f"{u['ad']} ({u['marka']}) için etiket bilgileri. Ürün düzeyindeki etki ifadeleri yalnızca ürün sayfasındaki beyanlardan gelir."
        yas_uyarisi = None
        if yas is not None and _yas_disinda(u["yas_siniri"], yas):
            yas_uyarisi = (f"Bu ürün etikette {_yas_metni(u['yas_siniri'])} için. {yas} yaş bu aralığın dışında; "
                           "bu yaşta kullanımı hekime danışılmalıdır.")
            ozet = yas_uyarisi + " " + ozet
        return veri.zarf({
            "kisa_ozet": ozet,
            **({"yas_uyarisi": yas_uyarisi} if yas_uyarisi else {}),
            **({"yas": yas} if yas is not None else {}),
            "urun": _urun_karti(u, yas),
        }, _urun_kaynaklari(u))
    if len(adaylar) > 1:
        return veri.zarf({
            "kisa_ozet": f"'{urun}' birden fazla ürünle eşleşti. Hangisini kastettiğinizi belirtin.",
            "adaylar": sorted((a["ad"] for a in adaylar), key=veri.normalize),
            "siralama_olcutu": "Alfabetik.",
        }, veri.kaynaklar(["orzax_urunler"]))
    # Eşleşme yoksa sorgudaki kelimelerden en az birini içeren ürünler; sorguda bir etken madde geçiyorsa adaylar
    # o maddeyi içerenlerle sınırlanır (v0.3 Ek 5): alakasız aday listelenmez.
    kelimeler = set(veri.normalize(urun).split())
    em_id = veri.sorgudaki_etken_madde(urun)
    benzer = sorted(
        (x["ad"] for x in veri.urunler() if kelimeler & set(veri.normalize(x["ad"]).split())
         and (em_id is None or _katalog_eslesmesi(em_id, x))),
        key=veri.normalize,
    )
    return veri.zarf({
        "kisa_ozet": (f"'{urun}' katalogda bulunamadı. Katalog şu an yalnızca Orzax ürünlerini içeriyor; başka markaların "
                      "etiket verisi yok. Orzax ürünüyse adını kutudaki gibi yazmayı deneyin."),
        "benzer_adli_urunler": benzer[:20],
        "katalogdaki_urun_sayisi": len(veri.urunler()),
        "katalog_kapsami": "Katalog şu an yalnızca Orzax ürünlerini içerir.",
        "siralama_olcutu": "Alfabetik. Ücretli veya öncelikli sıralama yoktur.",
    }, veri.kaynaklar(["orzax_urunler"]))


# --------------------------------------------------------------------------- #
# 2. parti_analizi
# --------------------------------------------------------------------------- #

_GS1_PARTI = re.compile(r"\(10\)\s*([A-Za-z0-9\-]+)")
_PARTI_PARAM = re.compile(r"[?&](?:parti|lot|batch)=([A-Za-z0-9\-]+)", re.IGNORECASE)


def _parti_no_coz(girdi: str) -> str:
    """Karekod içeriğinden (URL, GS1 metni) ya da düz metinden parti numarasını çıkarır."""
    g = girdi.strip()
    for desen in (_GS1_PARTI, _PARTI_PARAM):
        m = desen.search(g)
        if m:
            return m.group(1)
    if "/" in g:
        return g.rstrip("/").rsplit("/", 1)[-1]
    return g


def parti_analizi(karekod_veya_parti_no: str) -> dict:
    parti_no = _parti_no_coz(karekod_veya_parti_no)
    p = veri.parti_bul(parti_no)
    if p is None:
        return veri.zarf({
            "kisa_ozet": f"'{parti_no}' parti numarası için yayımlanmış analiz bulunamadı. {PARTI_ANALIZI_NOTU}",
            "aranan_parti_no": parti_no,
            "not": "Parti numarası kutunun alt ya da yan yüzünde, son kullanma tarihinin yanında yazar. "
                   "Ürünün etiket bilgileri için ürün rehberine bakılabilir.",
            "kopru": {"soru": "Ürünün adını yazarsanız etiket bilgisini Takviye Bilimi'nde gösterebilirim; ister misiniz?",
                      "evet_ise": [{"arac": "urun_rehberi", "parametreler": {"urun": "<kutudaki ürün adı>"}}]},
        }, veri.kaynaklar(["orzax_urunler"]))
    u = next(x for x in veri.urunler() if x["id"] == p["urun_id"])
    sonuclar = [{
        "etken_madde": veri.etken_madde_adi(r["etken_madde"]),
        "etiketteki": r["etiketteki"], "olculen": r["olculen"], "birim": r["birim"],
        # Ölçülenin etiketteki miktara oranı; yorum yok.
        "etikete_orani": round(r["olculen"] / r["etiketteki"] * 100),
    } for r in p["sonuclar"]]
    ozet = f"{u['ad']} · parti {p['parti_no']}: {len(sonuclar)} etken madde için etiketteki ve ölçülen miktar."
    return veri.zarf({
        "kisa_ozet": (DEMO_NOTU + " " if p["demo"] else "") + ozet,
        **({"demo": True, "demo_notu": p["not"]} if p["demo"] else {}),
        "aranan_parti_no": p["parti_no"],
        "urun": u["ad"],
        "laboratuvar": p["laboratuvar"],
        "analiz_tarihi": p["analiz_tarihi"],
        "sonuclar": sonuclar,
        "okuma_notu": "Oran, ölçülen miktarın etiketteki miktara yüzdesidir; ürün etkisi ya da güvenliği hakkında yorum değildir.",
        "kopru": {"soru": f"{u['ad']} ürününün etiket bilgisini Takviye Bilimi'nde görmek ister misiniz?",
                  "evet_ise": [{"arac": "urun_rehberi", "parametreler": {"urun": u["ad"]}}]},
    }, [veri.urun_kaynagi(u)])


# --------------------------------------------------------------------------- #
# 3. kisisel_rutin
# --------------------------------------------------------------------------- #

IlacGrubu = Literal[
    "yok",
    "kan_sulandirici_varfarin",
    "kan_sulandirici_diger",
    "tiroid_hormonu",
    "antibiyotik_kinolon_tetrasiklin",
    "mide_asidi_baskilayici",
    "metformin",
    "antiepileptik",
    "metotreksat",
    "diger",
]
Evre = Literal["yok", "gebelik_planliyor", "gebe", "emziriyor"]
_EVRE_ADLARI = {"gebelik_planliyor": "Gebelik planlama", "gebe": "Gebelik", "emziriyor": "Emzirme"}
Cinsiyet = Literal["kadin", "erkek", "belirtmek_istemiyor"]


class Icerik(BaseModel):
    etken_madde: str = Field(description="Ör. 'D vitamini', 'magnezyum', 'kalsiyum'")
    miktar: float = Field(ge=0, description="Günlük porsiyondaki miktar")
    birim: str = Field(description="mg, µg veya IU")


class DigerUrun(BaseModel):
    ad: str = Field(description="Ürünün adı, ör. 'Multivitamin'")
    icerikler: list[Icerik]


def _sayi(x: float) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".")


def _sinir_metni(em_id: str, sinir: dict | None) -> str | None:
    if sinir:
        tur = "üst sınır" if sinir["tur"] == "ust_sinir" else "güvenli alım düzeyi"
        return f"{_sayi(sinir['deger'])} {sinir['birim']} / gün (EFSA {tur})"
    kayit = veri.kurallar()["ust_sinirlar"].get(em_id)
    return kayit["kapsam"] if kayit else None


def _yas_metni(ys: dict) -> str:
    if ys["min"] is None:
        return "Ürün sayfasında belirtilmemiş"
    if ys["max"] is None:
        return f"{ys['min']} yaş ve üzeri"
    return f"{ys['min']}–{ys['max']} yaş"


# Üst sınırın bu oranına ulaşan toplam için bilgi notu verilir (TB-27).
YAKINLIK_ESIGI = 0.75


def kisisel_rutin(
    yas: int,
    cinsiyet: str,
    evre: str = "yok",
    ilac_grubu: list[str] | None = None,
    mevcut_urunler: list[str] | None = None,
    diger_urun_icerikleri: list[DigerUrun] | None = None,
) -> dict:
    ilaclar = {i for i in (ilac_grubu or []) if i != "yok"}
    kurallar = veri.kurallar()

    # Her etken madde için: hangi üründen ne kadar geliyor (standart birimde).
    icerik_kaynaklari: dict[str, list[tuple[str, float | None]]] = {}
    tanimsiz_urunler: list[str] = []
    tanimsiz_icerikler: list[str] = []
    bulunan_urunler: list[dict] = []
    kurali_olmayan: list[str] = []
    carpansiz: set[str] = set()
    belirsiz_urunler: dict[str, list[str]] = {}

    for ad in mevcut_urunler or []:
        eslesen = veri.urun_ara(ad)
        if len(eslesen) == 1:
            u = eslesen[0]
            bulunan_urunler.append(u)
            for em in u["etken_maddeler"]:
                if em["etken_madde"] is None:
                    kurali_olmayan.append(f"{u['ad']}: {em['etiketteki_ad']}")
                    continue
                std = veri.satir_miktari(em)
                # Etiketteki en yüksek günlük kullanım esas alınır; hesaplanamazsa porsiyon başına miktar kullanılır.
                carpan = em.get("gunluk_carpan")
                if carpan is None:
                    carpansiz.add(u["ad"])
                icerik_kaynaklari.setdefault(em["etken_madde"], []).append(
                    (u["ad"], None if std is None else std * (carpan or 1))
                )
        elif eslesen:
            belirsiz_urunler[ad] = [e["ad"] for e in eslesen]
        else:
            tanimsiz_urunler.append(ad)

    for diger in diger_urun_icerikleri or []:
        if isinstance(diger, dict):
            diger = DigerUrun.model_validate(diger)
        for ic in diger.icerikler:
            em_id = veri.etken_madde_id(ic.etken_madde)
            if em_id is None:
                tanimsiz_icerikler.append(f"{diger.ad}: {ic.etken_madde}")
                continue
            icerik_kaynaklari.setdefault(em_id, []).append(
                (diger.ad, veri.standart_miktar(em_id, ic.miktar, ic.birim))
            )

    # Toplam etken maddeler (ör. omega-3 = EPA + DHA).
    for toplam_id, parcalar in kurallar["toplamlar"].items():
        parca_kaynaklari = [k for p in parcalar for k in icerik_kaynaklari.get(p, [])]
        if parca_kaynaklari:
            icerik_kaynaklari.setdefault(toplam_id, []).extend(parca_kaynaklari)

    # Tekrar eden etken maddeler. Toplamı olan parçalar (EPA, DHA) toplam altında sayılır.
    parca_idleri = {p for parcalar in kurallar["toplamlar"].values() for p in parcalar}
    tekrar_edenler = []
    for em_id, liste in icerik_kaynaklari.items():
        if em_id in parca_idleri:
            continue
        urun_adlari = sorted({ad for ad, _ in liste})
        if len(urun_adlari) > 1:
            tekrar_edenler.append({"etken_madde": veri.etken_madde_adi(em_id), "urunler": urun_adlari})

    # Üst sınır karşılaştırması: yalnızca rakam, yorum yok. Miktarı doğrulanamayan içerik sessizce düşmez:
    # o maddenin satırı "eksik" işaretlenir, aşım ancak doğrulanan kısım bile sınırı geçiyorsa kesin sayılır.
    ust_sinir_kontrolu = []
    sinir_kaynaklari: list[str] = []
    dogrulanamayan = []
    for em_id, liste in icerik_kaynaklari.items():
        gecerli = [(ad, m) for ad, m in liste if m is not None]
        eksikler = sorted({ad for ad, m in liste if m is None}, key=veri.normalize)
        if em_id not in parca_idleri:
            dogrulanamayan += [f"{ad}: {veri.etken_madde_adi(em_id)}" for ad in eksikler]
        sinir = veri.ust_sinir(em_id, yas)
        if sinir is None:
            continue
        toplam = sum(m for _, m in gecerli)
        asiyor = toplam > sinir["deger"]
        oran = toplam / sinir["deger"] if sinir["deger"] else 0
        ust_sinir_kontrolu.append({
            "etken_madde": veri.etken_madde_adi(em_id),
            "takviyelerden_toplam": (
                f"{_sayi(toplam)} {sinir['birim']} / gün" + (" (yalnızca doğrulanan içerikler)" if eksikler else "")
                if gecerli else "Hesaplanamadı"
            ),
            "efsa_degeri": _sinir_metni(em_id, sinir),
            "asiyor": True if asiyor else (None if eksikler else False),
            "kontrol": "eksik" if eksikler else "tam",
            # Görsel kartın yığılmış çubuğu için: ürün başına katkı ve sınır (standart birimde).
            "katkilar": [{"urun": ad, "miktar": round(m, 3)} for ad, m in gecerli],
            "toplam_deger": round(toplam, 3),
            "sinir_degeri": sinir["deger"],
            "birim": sinir["birim"],
            # TB-27: sınıra yakınlık bilgi notudur; doz önerisi değildir.
            **({"sinira_yakinlik": (
                f"Takviyelerden gelen toplam, EFSA değerinin yaklaşık {veri.yuzde(round(oran * 100))}. Besinlerden gelen miktar "
                "bu toplama dahil değil. Bu bir doz önerisi değildir."
            )} if not asiyor and oran >= YAKINLIK_ESIGI else {}),
            **({"dogrulanamayan_urunler": eksikler} if eksikler else {}),
            "kapsam": sinir["kapsam"],
        })
        sinir_kaynaklari += sinir["kaynaklar"]
    asimlar = [k for k in ust_sinir_kontrolu if k["asiyor"]]
    eksik_kontroller = [k for k in ust_sinir_kontrolu if k["kontrol"] == "eksik"]

    # Etiketteki kullanım ve yaş sınırı.
    etiket_bilgileri = []
    for u in bulunan_urunler:
        ys = u["yas_siniri"]
        yas_disi = _yas_disinda(ys, yas)
        etiket_bilgileri.append({
            "urun": u["ad"],
            "etiketteki_kullanim": u["etiketteki_kullanim"],
            "yas_siniri": _yas_metni(ys),
            "yas_siniri_disinda": yas_disi,
            "uyarilar": ETIKET_UYARISI_NOTU,
        })

    # Etkileşim kuralları.
    etkilesimler = []
    sorular: list[str] = []
    for kural in kurallar["etkilesimler"]:
        kosul = kural["kosul"]
        em_listesi = _liste(kosul["etken_madde"])
        mevcut_em = [e for e in em_listesi if e in icerik_kaynaklari]
        if not mevcut_em:
            continue
        if "ilac_grubu" in kosul and not ilaclar.intersection(_liste(kosul["ilac_grubu"])):
            continue
        if "diger_etken_madde" in kosul and kosul["diger_etken_madde"] not in icerik_kaynaklari:
            continue
        if "evre" in kosul and evre not in kosul["evre"]:
            continue
        etkilesimler.append({
            "konu": " + ".join(
                [veri.etken_madde_adi(e) for e in mevcut_em]
                + ([kurallar["ilac_gruplari"][i] for i in _liste(kosul.get("ilac_grubu", [])) if i in ilaclar])
                + ([veri.etken_madde_adi(kosul["diger_etken_madde"])] if "diger_etken_madde" in kosul else [])
                + ([_EVRE_ADLARI[evre]] if "evre" in kosul else [])
            ),
            "seviye": kural["seviye"],
            "mesaj": kural["mesaj"],
        })
        sorular.append(kural["soru"])
        sinir_kaynaklari += kural.get("kaynaklar", [])

    for s in kurallar["ilac_sorulari"]:
        if s["ilac_grubu"] in ilaclar:
            sorular.append(s["soru"])

    # Hekime sorulacak sorular: bulgulardan türetilir; doz önerisi içermez.
    for a in asimlar:
        sorular.append(
            f"Kullandığım ürünlerden gelen toplam {a['etken_madde']} miktarı EFSA değerinin üzerinde görünüyor. Bu kombinasyonu nasıl değerlendirirsiniz?"
        )
    for t in tekrar_edenler:
        sorular.append(f"{t['etken_madde']} birden fazla üründe var ({', '.join(t['urunler'])}). Bunları birlikte kullanmam gerekli mi?")
    for e in etiket_bilgileri:
        if e["yas_siniri_disinda"]:
            sorular.append(f"{e['urun']} etiketteki yaş aralığının ({e['yas_siniri']}) dışında. Bu yaşta kullanımı uygun mu?")
    if evre in ("gebe", "emziriyor", "gebelik_planliyor") and (bulunan_urunler or diger_urun_icerikleri):
        etiket_metni = {"gebe": "gebelikte", "emziriyor": "emzirme döneminde", "gebelik_planliyor": "gebelik planlarken"}[evre]
        sorular.append(f"Kullandığım takviyeler {etiket_metni} uygun mu, hangilerini sürdürmeliyim?")
    if evre == "gebelik_planliyor" and "folik_asit" not in icerik_kaynaklari:
        sorular.append("Gebelik planlıyorum; folik asit kullanımı hakkında ne önerirsiniz?")
    if cinsiyet == "erkek" and "demir" in icerik_kaynaklari:
        sorular.append("Demir içeren bir ürün kullanıyorum; demir düzeyimin ölçülmesi gerekir mi?")
    if "d3" in icerik_kaynaklari:
        sorular.append("D vitamini düzeyimin ölçülmesi gerekir mi?")

    dogrulanamayan = sorted(set(dogrulanamayan), key=veri.normalize)
    ozet_parcalari = [
        f"{len(tekrar_edenler)} tekrar eden etken madde",
        f"{len(asimlar)} EFSA değeri aşımı",
        f"{len(etkilesimler)} etkileşim veya zamanlama notu",
    ]
    eksik_metni = ""
    if dogrulanamayan:
        eksik_metni = f" {len(dogrulanamayan)} içerik doğrulanamadı ve hesaba katılmadı"
        if eksik_kontroller:
            eksik_metni += (
                "; şu maddelerde üst sınır kontrolü eksik: "
                + ", ".join(k["etken_madde"] for k in eksik_kontroller)
            )
        eksik_metni += "."
    return veri.zarf({
        "kisa_ozet": (
            "Rutin kontrolü: " + ", ".join(ozet_parcalari) + "." + eksik_metni
            + " Bu bir değerlendirme değildir; sonuçları hekiminiz veya eczacınızla konuşun."
        ),
        "tekrar_eden_etken_maddeler": tekrar_edenler,
        "ust_sinir_kontrolu": ust_sinir_kontrolu,
        "ust_sinir_notu": (
            "Toplamlar yalnızca girilen takviyelerden, etiketteki en yüksek günlük kullanıma göre hesaplanmıştır; "
            "besinlerden gelen miktar dahil değildir."
        ),
        "gunluk_miktari_hesaplanamayan_urunler": sorted(carpansiz, key=veri.normalize),
        "kural_tanimli_olmayan_icerikler": kurali_olmayan,
        "etiket_bilgileri": etiket_bilgileri,
        "etkilesim_ve_zamanlama": etkilesimler,
        "hekime_sorulacak_sorular": list(dict.fromkeys(sorular)),
        "taninmayan_urunler": tanimsiz_urunler,
        "birden_fazla_eslesen_urunler": belirsiz_urunler,
        "taninmayan_icerikler": tanimsiz_icerikler,
        "dogrulanamayan_icerikler": dogrulanamayan,
        **({"dogrulanamayan_notu": (
            "Bu içeriklerin miktarı ürün sayfasında hatalı ya da okunamaz görünüyor veya birimi çevrilemedi. "
            "Toplamlar ve üst sınır karşılaştırması bu içerikler olmadan hesaplandı; ambalajdaki etiketi kontrol edin."
        )} if dogrulanamayan else {}),
        "gizlilik": "Girilen bilgiler yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, veri.kaynaklar(["efsa_ul_ozet_2025", *sinir_kaynaklari], [veri.urun_kaynagi(u) for u in bulunan_urunler]))


def _liste(x) -> list:
    return x if isinstance(x, list) else [x]


# --------------------------------------------------------------------------- #
# 4. yasam_karnesi
# --------------------------------------------------------------------------- #

# Seçenekler: (etiket, kod, alt, üst). Aralık sınırları puan eşikleriyle (_puanla) birebir hizalıdır;
# bir seçenek iki puan düzeyine taşmaz (testle zorunlu). Kategorik sorularda alt/üst yoktur.
_SECENEKLER: dict[str, list[tuple]] = {
    "hareket_gun": [
        ("Hiç", "0_gun", 0, 0), ("1–2 gün", "1_2_gun", 1, 2), ("3–4 gün", "3_4_gun", 3, 4), ("5–7 gün", "5_7_gun", 5, 7),
    ],
    # Tıklanabilir soru kartı en fazla 4 seçenek alır (TB-08): 9 saatin üstü tek seçenektir.
    "uyku_saat": [
        ("6 saatten az", "6_saatten_az", 0, 5.99), ("6 ile 7 saat arası", "6_7_saat", 6, 6.99),
        ("7–9 saat", "7_9_saat", 7, 9), ("9 saatten fazla", "9_saatten_fazla", 9.01, 24),
    ],
    "sebze_meyve_porsiyon": [
        ("0–2 porsiyon", "0_2_porsiyon", 0, 2.99), ("3–4 porsiyon", "3_4_porsiyon", 3, 4.99),
        ("5 porsiyon ya da daha fazla", "5_ve_uzeri", 5, 30),
    ],
    "balik_haftalik": [
        ("Hiç", "hic", 0, 0), ("Ayda 1–3 kez", "ayda_1_3", 0.25, 0.99), ("Haftada 1 kez", "haftada_1", 1, 1.99),
        ("Haftada 2 kez ya da daha sık", "haftada_2_ve_uzeri", 2, 21),
    ],
    "sigara": [("Hayır", "hayir"), ("Ara sıra", "ara_sira"), ("Her gün", "her_gun")],
    "stres": [("Hiç", "hic"), ("Bazen", "bazen"), ("Sık", "sik"), ("Neredeyse her gün", "neredeyse_her_gun")],
}
_ARALIKLAR = {(a, s[1]): (s[2], s[3]) for a, liste in _SECENEKLER.items() for s in liste if len(s) == 4}
_ETIKETLER = {(a, s[1]): s[0] for a, liste in _SECENEKLER.items() for s in liste}

SORULAR = [
    {"anahtar": "hareket_gun", "soru": "Son bir haftada kaç gün en az 30 dakika tempolu hareket ettin?", "sayi_araligi": "0–7"},
    {"anahtar": "uyku_saat", "soru": "Gece ortalama kaç saat uyuyorsun?", "sayi_araligi": "0–24"},
    {"anahtar": "sebze_meyve_porsiyon", "soru": "Günde kaç porsiyon sebze ve meyve yiyorsun? (1 porsiyon ≈ 1 avuç ya da 1 orta boy meyve)", "sayi_araligi": "0–30"},
    {"anahtar": "balik_haftalik", "soru": "Haftada kaç kez balık yiyorsun?", "sayi_araligi": "0–21"},
    {"anahtar": "sigara", "soru": "Sigara ya da tütün kullanıyor musun?"},
    {"anahtar": "stres", "soru": "Son iki haftada kendini ne sıklıkla gergin ya da tükenmiş hissettin?"},
]
for _s in SORULAR:
    _s["secenekler"] = [{"etiket": x[0], "deger": x[1]} for x in _SECENEKLER[_s["anahtar"]]]

SORU_YONERGESI = (
    "Soruları iki adımda, seçenekleriyle sorun: önce ilk dört soru (hareket, uyku, sebze-meyve, balık), sonra kalan "
    "iki soru (tütün, stres). Her soruda en fazla 4 seçenek vardır. Kullanıcı bir seçenek seçerse seçenek kodunu "
    "(ör. '1_2_gun'), sayı verirse sayıyı iletin."
)

ESIK_NOTU = (
    "Eşikler yetişkinler için genel halk sağlığı önerilerinden sadeleştirilmiştir: haftada en az 150 dakika "
    "orta yoğunlukta hareket (WHO), gecede 7–9 saat uyku (National Sleep Foundation), günde en az 400 g sebze-meyve "
    "(WHO; karnede 5 porsiyon olarak sadeleştirildi), haftada 1–2 kez deniz ürünü (American Heart Association; "
    "karnede haftada 1 kez ve üzeri iyi sayılır). Gecede 9 saatten uzun uyku 'orta' sayılır. "
    "Prototiptir; medikal kurul onayı bekler."
)
KARNE_KAYNAKLARI = [
    "who_fiziksel_aktivite_2020", "nsf_uyku_suresi_2015", "who_saglikli_beslenme", "aha_deniz_urunleri_2018", "who_tutun",
]

# Puan: 2 = iyi, 1 = orta, 0 = gelişmeli
_SEVIYE = {2: "iyi", 1: "orta", 0: "gelişmeli"}

# ilk_adim mevcut seviyeye göre bir basamak yukarıyı hedefler (TB-09): anahtar cevabın puanıdır (0 ya da 1).
_HEDEFLER = {
    "sigara": {
        "alan": "Tütün",
        "hedef": "Bırakmak için bir tarih belirle.",
        "ilk_adim": {
            0: "ALO 171 Sigara Bırakma Danışma Hattı'nı ara ya da aile hekiminden sigara bırakma desteği iste.",
            1: "Ara sıra içtiğin durumları not et; ALO 171 ya da aile hekiminden bırakma desteği iste.",
        },
    },
    "hareket_gun": {
        "alan": "Hareket",
        "hedef": "Haftada 5 gün 30 dakika tempolu hareket.",
        "ilk_adim": {
            0: "Bu hafta 2 güne birer 20 dakikalık yürüyüş koy; günü ve saati takvime yaz.",
            1: "Hareket ettiğin günlere bu hafta bir gün daha ekle; günü ve saati takvime yaz.",
        },
    },
    "uyku_saat": {
        "alan": "Uyku",
        "hedef": "Gecede 7–9 saat uyku.",
        "ilk_adim": {
            0: "Bu hafta yatış saatini 30 dakika öne al ve her gün aynı saatte kalk.",
            1: "Her gün aynı saatte yat ve kalk; hafta sonu da bu saatleri koru.",
        },
    },
    "sebze_meyve_porsiyon": {
        "alan": "Sebze ve meyve",
        "hedef": "Günde en az 5 porsiyon sebze ve meyve.",
        "ilk_adim": {
            0: "Her ana öğüne bir porsiyon sebze ya da salata ekle.",
            1: "Bir ara öğünü bir porsiyon meyve ya da çiğ sebzeyle değiştir.",
        },
    },
    "balik_haftalik": {
        "alan": "Balık",
        "hedef": "Haftada 1–2 kez balık.",
        "ilk_adim": {
            0: "Bu ay menüye iki balık günü koy; balık yemiyorsan bunu hekiminle ya da diyetisyenle konuş.",
            1: "Haftalık menüye sabit bir balık günü koy.",
        },
    },
    "stres": {
        "alan": "Stres",
        "hedef": "Her gün kendine ayrılmış kısa bir dinlenme zamanı.",
        "ilk_adim": {
            0: "Günde 10 dakika ekransız yürüyüş ya da sessiz bir mola planla; bu his sürüyorsa hekimle konuş.",
            1: "Günde 10 dakika ekransız yürüyüş ya da sessiz bir mola planla.",
        },
    },
}
_ONCELIK = ["sigara", "hareket_gun", "uyku_saat", "sebze_meyve_porsiyon", "balik_haftalik", "stres"]


def _kodlar(anahtar: str):
    return Literal[tuple(x[1] for x in _SECENEKLER[anahtar])]  # type: ignore[valid-type]


class KarneCevaplari(BaseModel):
    """Sayısal sorular sayı ya da seçenek kodu kabul eder; aralık eşlemesini sunucu yapar."""

    hareket_gun: Annotated[int, Field(ge=0, le=7)] | _kodlar("hareket_gun") | None = Field(
        default=None, description="Son bir haftada en az 30 dk tempolu hareket edilen gün sayısı ya da kod (ör. '1_2_gun')")
    uyku_saat: Annotated[float, Field(ge=0, le=24)] | _kodlar("uyku_saat") | None = Field(
        default=None, description="Gecelik ortalama uyku süresi (saat) ya da kod (ör. '6_7_saat')")
    sebze_meyve_porsiyon: Annotated[float, Field(ge=0, le=30)] | _kodlar("sebze_meyve_porsiyon") | None = Field(
        default=None, description="Günlük sebze ve meyve porsiyonu ya da kod (ör. '3_4_porsiyon')")
    balik_haftalik: Annotated[float, Field(ge=0, le=21)] | _kodlar("balik_haftalik") | None = Field(
        default=None, description="Haftada kaç kez balık ya da kod (ör. 'ayda_1_3')")
    sigara: _kodlar("sigara") | None = None
    stres: _kodlar("stres") | None = None


def _puanla(anahtar: str, deger) -> int:
    if anahtar == "hareket_gun":
        return 2 if deger >= 5 else 1 if deger >= 3 else 0
    if anahtar == "uyku_saat":
        return 2 if 7 <= deger <= 9 else 1 if 6 <= deger < 7 or deger > 9 else 0
    if anahtar == "sebze_meyve_porsiyon":
        return 2 if deger >= 5 else 1 if deger >= 3 else 0
    if anahtar == "balik_haftalik":
        # AHA haftada 1–2 kez deniz ürünü önerir (TB-10): haftada 1 kez iyi, ayda birkaç kez orta.
        return 2 if deger >= 1 else 1 if deger > 0 else 0
    if anahtar == "sigara":
        return {"hayir": 2, "ara_sira": 1, "her_gun": 0}[deger]
    if anahtar == "stres":
        return {"hic": 2, "bazen": 2, "sik": 1, "neredeyse_her_gun": 0}[deger]
    raise KeyError(anahtar)


def _aralik(anahtar: str, deger) -> tuple:
    """Cevabı (alt, üst) aralığına çevirir: sayı tek noktadır, seçenek kodu kendi aralığıdır, kategorik cevap kendisidir."""
    return _ARALIKLAR.get((anahtar, deger), (deger, deger))


def _puan(anahtar: str, deger) -> int:
    """Cevabın puanı. Seçenek aralıkları eşiklerle hizalı olduğundan aralığın alt ucu yeterlidir."""
    return _puanla(anahtar, _aralik(anahtar, deger)[0])


def _cevap_metni(anahtar: str, deger) -> str:
    return _ETIKETLER.get((anahtar, deger), _sayi(deger) if isinstance(deger, (int, float)) else str(deger))


def _kural_saglanir(kosul: dict, cevaplar: dict) -> bool:
    if not kosul:
        return True
    alt, ust = _aralik(kosul["alan"], cevaplar[kosul["alan"]])
    if "ust_sinir_kucuktur" in kosul:
        return ust < kosul["ust_sinir_kucuktur"]
    if "icinde" in kosul:
        return alt in kosul["icinde"]
    raise ValueError(f"Tanımsız karne kuralı koşulu: {kosul}")


def _kopruler(girilen: dict) -> tuple[dict, list[str]]:
    """Karne cevaplarından takviye bağlantıları ve güvenlik uyarıları üretir.

    Takviye bağlantısı yalnızca hedef maddenin sunulabilir kanıt kartı varsa kurulur (TB-12): boş karta köprü yok.
    Tahlil önerisi karneden çıkarıldı (TB-11): cevaplara bağlı değildi; tahliller şikâyet yolunda ele alınır.
    """
    baglantilar, uyarilar, kaynak_idleri = [], [], []
    for k in veri.karne_kurallari():
        if not _kural_saglanir(k["kosul"], girilen):
            continue
        if k["tur"] == "takviye_baglantisi" and veri.monografi(k["etken_madde"]) is None:
            continue
        kaynak_idleri += k["kaynaklar"]
        kayit = {"tetikleyici": k["tetikleyici"], "etken_madde": _rehber_adi(k["etken_madde"]),
                 "mesaj": k["mesaj"], "onerilen_sonraki_arac": k["onerilen_sonraki_arac"]}
        (baglantilar if k["tur"] == "takviye_baglantisi" else uyarilar).append(kayit)
    return {
        "takviye_baglantilari": baglantilar,
        "guvenlik_uyarilari": uyarilar,
        "kopru_notu": ("Bağlantılar takviye önerisi değildir; ilgili kanıtı incelemek için yönlendirmedir. "
                       "Yalnızca kanıt kartı hazır olan maddelere bağlantı verilir. Kurallar medikal kurul onayı bekler."),
    }, kaynak_idleri


def yasam_karnesi(cevaplar: KarneCevaplari | dict | None = None, yas: int | None = None) -> dict:
    if isinstance(cevaplar, dict) or cevaplar is None:
        cevaplar = KarneCevaplari.model_validate(cevaplar or {})
    girilen = cevaplar.model_dump(exclude_none=True)
    eksik = [s for s in SORULAR if s["anahtar"] not in girilen]

    if eksik:
        return veri.zarf({
            "kisa_ozet": f"Karne için 6 sorunun hepsi gerekli; {len(eksik)} soru cevaplanmadı.",
            "soru_yonergesi": SORU_YONERGESI,
            "eksik_sorular": eksik,
        }, veri.kaynaklar(KARNE_KAYNAKLARI))

    karne = []
    for s in SORULAR:
        puan = _puan(s["anahtar"], girilen[s["anahtar"]])
        karne.append({
            "alan": _HEDEFLER[s["anahtar"]]["alan"],
            "cevap": _cevap_metni(s["anahtar"], girilen[s["anahtar"]]),
            "seviye": _SEVIYE[puan],
            "puan": puan,
        })
    toplam = sum(k["puan"] for k in karne)

    gelismeli = sorted(
        (s["anahtar"] for s, k in zip(SORULAR, karne) if k["puan"] < 2),
        key=lambda a: (_puan(a, girilen[a]), _ONCELIK.index(a)),
    )
    hedefler = [{**_HEDEFLER[a], "ilk_adim": _HEDEFLER[a]["ilk_adim"][_puan(a, girilen[a])]} for a in gelismeli[:3]]

    notlar = []
    if girilen["stres"] == "neredeyse_her_gun":
        notlar.append("Neredeyse her gün gergin ya da tükenmiş hissetmek bir hekim veya ruh sağlığı uzmanıyla konuşmaya değer.")
    if isinstance(girilen["uyku_saat"], (int, float)) and girilen["uyku_saat"] > 10:
        notlar.append("Düzenli olarak gecede 10 saatten uzun uyumak, nedeni hekimle konuşulmaya değer bir durumdur.")
    if yas is not None and yas < 18:
        notlar.append("Bu karnenin eşikleri yetişkinler içindir; çocuk ve gençlerde uyku ve hareket ihtiyacı farklıdır.")

    kopru, kopru_kaynaklari = _kopruler(girilen)
    return veri.zarf({
        "kisa_ozet": f"Karne: {toplam}/12. {len(hedefler)} hedef seçildi." if hedefler else f"Karne: {toplam}/12. Altı alanın hepsi iyi düzeyde.",
        "karne": karne,
        "toplam_puan": toplam,
        "en_yuksek_puan": 12,
        "hedefler": hedefler,
        "hedef_secimi": "En düşük puanlı alanlardan en fazla 3 hedef seçilir; eşitlikte tütün, hareket, uyku, beslenme, balık, dinlenme sırası izlenir.",
        "esik_notu": ESIK_NOTU,
        "notlar": notlar,
        **kopru,
        "gizlilik": "Cevaplar yalnızca bu karneyi üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, veri.kaynaklar(KARNE_KAYNAKLARI + kopru_kaynaklari))


# --------------------------------------------------------------------------- #
# 5. etken_madde_rehberi
# --------------------------------------------------------------------------- #

Sigara = Literal["hayir", "ara_sira", "her_gun"]

# Kanıt kartı ilk seti. "multivitamin" bir etken madde değil, ürün türüdür; kataloğa ayrı ölçütle bağlanır.
REHBER_KAPSAMI = [
    "d3", "omega3", "b12", "folik_asit", "demir", "magnezyum",
    "c_vitamini", "cinko", "multivitamin", "beta_karoten", "e_vitamini", "probiyotik",
]
_MULTIVITAMIN_ADLARI = {"multivitamin", "multi vitamin", "multivitamin mineral", "vitamin mineral", "multi"}
# Bir ürünün multivitamin sayılması için içermesi gereken en az farklı vitamin/mineral sayısı.
_MULTIVITAMIN_ESIGI = 5
_VITAMIN_MINERAL = {
    "d3", "k2", "a_vitamini", "b1", "b2", "b3", "b5", "b6", "biotin", "folik_asit", "b12", "c_vitamini", "e_vitamini",
    "magnezyum", "demir", "cinko", "kalsiyum", "selenyum", "iyot", "bakir", "manganez", "krom", "molibden",
}
# Omega-3 rehberi EPA ve DHA'yı ayrı satır olarak yazan ürünleri de kapsar.
_KATALOG_KIMLIKLERI = {"omega3": {"omega3", "epa", "dha", "toplam_omega3"}}
# Kanıt kartı olan maddede modele dönen en fazla ürün sayısı (TB-14); kalanı sayıyla verilir.
KATALOG_SINIRI = 5
TASLAK_NOTU = "Taslak: bu kanıt kartı medikal kurul onayı bekliyor."
TASLAK_UYARI_NOTU = "Taslak: bu güvenlik uyarısı medikal kurul onayı bekliyor; onay beklerken de gösterilir."


# Kanıt kartı hazırlanana kadar yönlendirilen genel bilgi sayfası (kurum belgesi, doğrulanmış).
GENEL_KILAVUZ = {
    "d3": "nih_ods_d_vitamini", "omega3": "nih_ods_omega3", "b12": "nih_ods_b12", "folik_asit": "nih_ods_folat",
    "demir": "nih_ods_demir", "magnezyum": "nih_ods_magnezyum", "c_vitamini": "nih_ods_c_vitamini",
    "cinko": "nih_ods_cinko", "multivitamin": "nih_ods_multivitamin", "beta_karoten": "nih_ods_a_vitamini_karotenoidler",
    "e_vitamini": "nih_ods_e_vitamini", "probiyotik": "nih_ods_probiyotik",
}


def _katalog_sayisi_metni(sayi: int) -> str:
    return (f"Katalogda bu maddeyi içeren {sayi} ürün var. Katalog şu an yalnızca Orzax ürünlerini içerir. "
            "Belirli bir ürünün etiket bilgisi için ürün adıyla sorulabilir.")


def _genel_kilavuz(em_id: str) -> dict | None:
    kid = GENEL_KILAVUZ.get(em_id)
    if not kid or not veri.kaynaklar([kid]):
        return None
    k = veri.kaynaklar([kid])[0]
    return {"baslik": k["baslik"], "kurum": k["kurum_veya_dergi"], "url": k["url"], "dil": "İngilizce"}


def _rehber_id(ad: str) -> str | None:
    if veri.normalize(ad) in _MULTIVITAMIN_ADLARI:
        return "multivitamin"
    return veri.etken_madde_id(ad)


def _rehber_adi(em_id: str) -> str:
    return "Multivitamin" if em_id == "multivitamin" else veri.etken_madde_adi(em_id)


def _katalog_eslesmesi(em_id: str, u: dict) -> list[dict]:
    """Ürünün bu rehberle eşleşen içerik satırları; multivitaminde tüm vitamin/mineral satırları."""
    if em_id == "multivitamin":
        satirlar = [e for e in u["etken_maddeler"] if e["etken_madde"] in _VITAMIN_MINERAL]
        return satirlar if len({e["etken_madde"] for e in satirlar}) >= _MULTIVITAMIN_ESIGI else []
    kimlikler = _KATALOG_KIMLIKLERI.get(em_id, {em_id})
    return [e for e in u["etken_maddeler"] if e["etken_madde"] in kimlikler]


def _katalog_urunleri(em_id: str, yas: int | None) -> tuple[list[dict], list[dict], list[dict]]:
    """(eşleşen, yaşa uygun ve sıralı, yaş sınırı dışında) ürünler. Sıra: yalnızca bu maddeyi içerenler önce, sonra alfabetik."""
    eslesen = [u for u in veri.urunler() if _katalog_eslesmesi(em_id, u)]
    yas_disi = [u for u in eslesen if yas is not None and _yas_disinda(u["yas_siniri"], yas)]
    uygun = sorted((u for u in eslesen if u not in yas_disi),
                   key=lambda x: (not _tek_icerikli(x, em_id), veri.normalize(x["ad"])))
    return eslesen, uygun, yas_disi


def _madde_beyanlari(u: dict, em_id: str) -> list[str]:
    """Ürün sayfası beyanlarından bu maddeye eşlenenler; ürün rehberiyle aynı kaynak (TB-15)."""
    hedef = veri.KATALOG_GRUBU.get(em_id, em_id)
    return [b["metin"] for b in veri.urun_saglik_beyanlari(u) if em_id == "multivitamin" or hedef in b["etken_maddeler"]]


def _katalog_ogesi(u: dict, em_id: str, beyanlar: list[str]) -> dict:
    return {
        "ad": u["ad"],
        "marka": u["marka"],
        "tek_icerikli": _tek_icerikli(u, em_id),
        "porsiyondaki_miktar": [f"{e['etiketteki_ad']}: {_etiket_miktari(e, u)}" for e in _katalog_eslesmesi(em_id, u)],
        "yas_siniri": _yas_metni(u["yas_siniri"]),
        "urun_sayfasi_beyanlari": beyanlar,
        "parti_analizi_var": veri.gercek_parti_analizi_var(u["id"]),
    }


def _beyan_anahtari(beyan: str, anahtarlar: list[str]) -> str:
    """"D vitamini normal kemiklerin…" ile "Normal kemiklerin…" aynı beyandır: baştaki madde adı karşılaştırmaya katılmaz."""
    n = veri.normalize(beyan)
    for a in anahtarlar:
        if n.startswith(a + " "):
            return n[len(a) + 1:]
    return n


def _tek_icerikli(u: dict, em_id: str) -> bool:
    """Yalnızca bu maddeyi içeren ürün. Kural tablosunda tanımı olmayan içerikler de sayılır (v0.3 Ek 3):
    "Ocean Dim Ultra" D3 dışında altı içerik taşıdığı için tek içerikli değildir."""
    kimlikler = {e["etken_madde"] for e in u["etken_maddeler"]}
    return bool(kimlikler) and kimlikler <= _KATALOG_KIMLIKLERI.get(em_id, {em_id})


def _kosul_saglanir(kosul: dict, profil: dict) -> bool:
    yas = profil.get("yas")
    if "yas_min" in kosul and (yas is None or yas < kosul["yas_min"]):
        return False
    if "yas_max" in kosul and (yas is None or yas > kosul["yas_max"]):
        return False
    for alan in ("evre", "sigara", "cinsiyet"):
        if alan in kosul and profil.get(alan) not in kosul[alan]:
            return False
    if "ilac_grubu" in kosul and not set(kosul["ilac_grubu"]) & set(profil.get("ilac_grubu") or []):
        return False
    return True


# v0.3 Ek 7: 100 kişide mutlak fark 2'nin altındaki fayda "küçük fayda" diye etiketlenir.
KUCUK_FAYDA_ESIGI = 2
SONUC_ETIKETLERI = {"fayda": "Fayda", "kucuk_fayda": "Küçük fayda", "etkisiz": "Etkisiz bulundu",
                    "zarar": "Güvenlik sinyali", "belirsiz": "Belirsiz"}


def sonuc_etiketi(kart: dict) -> str:
    """Kartın sonuç etiketi kodu. Fayda yönündeki kartta 100 kişilik gruplar arasındaki fark eşiğin altındaysa küçük faydadır."""
    yon = kart["sonuc_yonu"]
    gruplar = (kart["mutlak_fark"].get("yuz_kiside") or {}).get("gruplar", [])
    if yon == "fayda" and len(gruplar) == 2 and abs(gruplar[0]["sayi"] - gruplar[1]["sayi"]) < KUCUK_FAYDA_ESIGI:
        return "kucuk_fayda"
    return yon


def _kunye(kid: str) -> str:
    k = veri.kaynak_kayitlari()[kid]
    return f"{k['kurum_veya_dergi']}, {k['yil']}" if k.get("yil") else k["kurum_veya_dergi"]


def etken_madde_rehberi(
    etken_madde: str,
    yas: int | None = None,
    cinsiyet: str | None = None,
    evre: str | None = None,
    sigara: str | None = None,
    ilac_grubu: list[str] | None = None,
) -> dict:
    em_id = _rehber_id(etken_madde)
    if em_id is None:
        aranan = veri.normalize(etken_madde)
        urunler = sorted(
            (u["ad"] for u in veri.urunler()
             if aranan and any(aranan in veri.normalize(e["etiketteki_ad"]) for e in u["etken_maddeler"])),
            key=veri.normalize,
        )
        # Kanıt kartı olmayan maddede ürün listesi dönmez (TB-05); yalnızca katalog kapsamı sayıyla yazılır.
        return veri.zarf({
            "kisa_ozet": (
                f"'{etken_madde}' için kanıt kartı yok; kanıt kartı olmayan maddede ürün listesi gösterilmez."
                + ("" if urunler else " Adı farklı yazmayı deneyin (ör. 'D vitamini', 'omega-3').")
            ),
            "kanit_karti_hazirlanan_maddeler": [_rehber_adi(i) for i in REHBER_KAPSAMI],
            "katalog_kapsami": _katalog_sayisi_metni(len(urunler)),
        }, veri.kaynaklar(["orzax_urunler"]))

    profil = {"yas": yas, "cinsiyet": cinsiyet, "evre": evre, "sigara": sigara,
              "ilac_grubu": [i for i in (ilac_grubu or []) if i != "yok"]}
    m = veri.monografi(em_id)
    ad = m["ad"] if m else _rehber_adi(em_id)
    kaynak_idleri: list[str] = []

    # Zorunlu güvenlik uyarıları (TB-03, TB-04): kanıt kartı olsa da olmasa da, en üstte.
    zorunlu = []
    for u in veri.zorunlu_uyarilar(em_id):
        if _kosul_saglanir(u["kosul"], profil):
            zorunlu.append({
                "mesaj": u["mesaj"],
                "dayanak": [_kunye(i) for i in u["kaynaklar"]],
                **({"durum": TASLAK_UYARI_NOTU} if u["durum"] == "taslak" else {}),
            })
            kaynak_idleri += u["kaynaklar"]
    # "Tahlilsiz kullanma" uyarısının ilk cümlesi özetin ilk cümlesi olur.
    on_ek = next((u["mesaj"].split(". ")[0] + ". " for u in veri.zorunlu_uyarilar(em_id)
                  if u["tur"] == "tahlilsiz_kullanma" and _kosul_saglanir(u["kosul"], profil)), "")

    # Kanıt düzeyi: sonuç alanı bazında.
    kanit = []
    for k in (m or {}).get("kartlar", []):
        kanit.append({
            "sonuc_alani": k["sonuc_alani"],
            "populasyon": k["populasyon"],
            "duzey": k["kanit_duzeyi"],
            "sonuc_yonu": k["sonuc_yonu"],
            "sonuc_etiketi": sonuc_etiketi(k),
            "gerekce": k["gerekce"],
            "halk_ozeti": k["halk_ozeti"],
            "mutlak_fark": k["mutlak_fark"]["metin"],
            **({"mutlak_fark_100": k["mutlak_fark"]["yuz_kiside"]} if k["mutlak_fark"].get("yuz_kiside") else {}),
            "calismalarda_kullanilan_dozlar": k["calisilan_dozlar"],
            "ne_bilmiyoruz": k["ne_bilmiyoruz"],
            "dayanak": [_kunye(i) for i in k["kaynaklar"]],
            **({"durum": TASLAK_NOTU} if k["durum"] == "taslak" else {}),
        })
        kaynak_idleri += k["kaynaklar"]

    # TB-18: profil verildiyse kullanıcının grubu ilk satıra çıkar. Gruplar listedeki sırayla denenir (ör. gebelik
    # yetişkin grubundan önce); koşulu olmayan grup (ör. prediyabet) profilden çıkarılamaz, otomatik seçilmez.
    profil_verildi = any(profil[a] for a in ("yas", "cinsiyet", "evre", "ilac_grubu"))
    senin_grubun = None
    if m and profil_verildi:
        g = next((g for g in m.get("kimde_kanit_var", []) if "kosul" in g and _kosul_saglanir(g["kosul"], profil)), None)
        senin_grubun = {"grup": g["grup"], "gerekce": g["gerekce"]} if g else {
            "grup": "Eşleşen ayrı grup yok", "gerekce": "Verdiğin bilgilerle kanıt özetindeki gruplardan biri eşleşmedi."}

    # Profile göre dikkat edilecekler ve hekime sorulacaklar.
    dikkat, sorular = [], list((m or {}).get("hekime_sorulacaklar", []))
    for kural in (m or {}).get("dikkat_kurallari", []):
        if _kosul_saglanir(kural["kosul"], profil):
            dikkat.append(kural["mesaj"])
            kaynak_idleri += kural["kaynaklar"]

    # Etkileşim kural tablosu (kurallar.json): bu maddeyi içeren kurallar.
    kurallar = veri.kurallar()
    etkilesimler = []
    for kural in kurallar["etkilesimler"]:
        kosul = kural["kosul"]
        if em_id not in _liste(kosul["etken_madde"]):
            continue
        karsi = [kurallar["ilac_gruplari"][i] for i in _liste(kosul.get("ilac_grubu", []))]
        if "diger_etken_madde" in kosul:
            karsi.append(veri.etken_madde_adi(kosul["diger_etken_madde"]))
        karsi += [_EVRE_ADLARI[e] for e in kosul.get("evre", [])]
        etkilesimler.append({"ile": karsi, "seviye": kural["seviye"], "mesaj": kural["mesaj"]})
        kaynak_idleri += kural.get("kaynaklar", [])
        if (set(_liste(kosul.get("ilac_grubu", []))) & set(profil["ilac_grubu"])) or profil["evre"] in kosul.get("evre", []):
            dikkat.append(kural["mesaj"])
            sorular.append(kural["soru"])

    # EFSA üst sınırı: güvenlik tavanı, öneri değil.
    sinir_kaydi = kurallar["ust_sinirlar"].get(em_id)
    efsa = None
    if sinir_kaydi:
        sinir = veri.ust_sinir(em_id, yas if yas is not None else 18)
        efsa = {
            "deger": _sinir_metni(em_id, sinir) if sinir else "Sayısal üst sınır belirlenmemiş",
            "yas_grubu": "yetişkin" if yas is None else f"{yas} yaş",
            "kapsam": sinir_kaydi["kapsam"],
            # Sayısal sınır yoksa (ör. C vitamini) "bu değer" diye başlayan not anlamsızdır (v0.3 Ek 8).
            "not": "Bu değer bir güvenlik tavanıdır; alınması gereken miktar değildir." if sinir else "",
        }
        kaynak_idleri += sinir_kaydi["kaynaklar"]

    # Katalog (TB-14): yaş sınırına uyanlar; tek içerikliler önce, sonra alfabetik; en fazla KATALOG_SINIRI ürün.
    anahtarlar = [veri.normalize(a) for a in (m or {}).get("beyan_anahtarlari", [])]
    eslesen, uygun, yas_disi = _katalog_urunleri(em_id, yas)
    katalog, beyan_metinleri, beyan_urunleri = [], [], []
    for u in uygun:
        beyanlar = _madde_beyanlari(u, em_id)
        if len(katalog) < KATALOG_SINIRI:
            katalog.append(_katalog_ogesi(u, em_id, beyanlar))
        # Madde düzeyindeki beyan listesi yalnızca bu maddeyi tek başına içeren ürünlerden derlenir.
        if em_id != "multivitamin" and beyanlar and _tek_icerikli(u, em_id):
            for b in beyanlar:
                anahtar = _beyan_anahtari(b, anahtarlar)
                onceki = next((i for i, x in enumerate(beyan_metinleri) if _beyan_anahtari(x, anahtarlar) == anahtar), None)
                if onceki is None:
                    beyan_metinleri.append(b)
                elif veri.normalize(b) != anahtar and veri.normalize(beyan_metinleri[onceki]) == anahtar:
                    beyan_metinleri[onceki] = b  # Etken madde adını içeren yazım tercih edilir.
            beyan_urunleri.append(u)
    katalog_ozeti = {
        "gosterilen": len(katalog),
        "kalan_urun_sayisi": len(uygun) - len(katalog),
        **({"yas_siniri_disinda_kalan": len(yas_disi)} if yas_disi else {}),
        "kapsam": "Katalog şu an yalnızca Orzax ürünlerini içerir.",
        "siralama_olcutu": ("Yalnızca bu maddeyi içeren ürünler önce, sonra alfabetik. "
                            "Sponsorlu veya öncelikli sıralama yoktur; sıra bir öneri değildir."),
    }

    # Tek gösterim kuralı (v0.3 Ek 4): sunulabilir kartı olmayan maddede ürün listesi yok, yalnızca sayı.
    if m is None or not veri.urun_listesi_gosterilir(em_id):
        return _kartsiz_yanit(em_id, ad, on_ek, zorunlu, efsa, etkilesimler, dikkat, sorular, len(eslesen), kaynak_idleri)
    kaynak_idleri += m.get("kaynaklar", []) + m.get("uretici_icerikleri", [])
    for alan in ("besinle_karsilama", "tahlil_notu", "formlar"):
        kaynak_idleri += m.get(alan, {}).get("kaynaklar", [])
    for g in m.get("kimde_kanit_var", []):
        kaynak_idleri += g["kaynaklar"]
    # Bağımsız kaynaklar önce, üretici içerikleri sonra.
    kayitlar = veri.kaynak_kayitlari()
    sirali = sorted(dict.fromkeys(kaynak_idleri), key=lambda i: kayitlar[i]["tur"] == "uretici_icerigi")
    kaynak_listesi = veri.kaynaklar(sirali)
    kaynak_listesi = (
        [k for k in kaynak_listesi if k["tur"] != "uretici_icerigi"]
        + [veri.urun_kaynagi(u) for u in beyan_urunleri[:KATALOG_SINIRI]]
        + [k for k in kaynak_listesi if k["tur"] == "uretici_icerigi"]
    )

    return veri.zarf({
        "kisa_ozet": on_ek + (f"Senin grubun: {senin_grubun['grup']}. {senin_grubun['gerekce']} " if senin_grubun else "")
                     + m["kisa_ozet"],
        "etken_madde_adi": ad,
        # Görsel kart için öneksiz özet: uyarı ve grup kartta ayrı kutularda durur.
        "genel_ozet": m["kisa_ozet"],
        **({"senin_grubun": senin_grubun} if senin_grubun else {}),
        "zorunlu_uyarilar": zorunlu,
        **({"kanit_durumu": TASLAK_NOTU} if m["durum"] == "taslak" else {}),
        "kimde_kanit_var": [{"grup": g["grup"], "gerekce": g["gerekce"]} for g in m.get("kimde_kanit_var", [])],
        **({"kimde_kanit_var_notu": m["kimde_kanit_var_notu"]} if m.get("kimde_kanit_var_notu") else {}),
        "kanit_duzeyi": kanit,
        "kanit_duzeyi_olcegi": (
            "guclu: birden fazla yüksek kaliteli çalışmada tutarlı; orta: tutarlı ama sınırlı ya da kalite sorunlu; "
            "zayif: küçük ya da çelişkili çalışmalar; yetersiz: anlamlı insan çalışması yok. "
            "sonuc_yonu ayrıca fayda, etkisiz, zarar ya da belirsiz olabilir."
        ),
        # TB-16: ürün sayfası metnidir; regülasyon onayı ayrıca doğrulanmadı.
        "urun_sayfasi_beyanlari": {
            "metinler": beyan_metinleri,
            "not": (
                "Bu maddeye eşlenen, katalog ürünlerinin sayfalarındaki beyanlardır. " + BEYAN_ACIKLAMASI
                if beyan_metinleri else
                "Katalogdaki ürün sayfalarında bu maddeye açıkça eşlenebilen beyan bulunmadı."
            ),
        },
        "besinle_karsilama": m.get("besinle_karsilama", {}).get("metin"),
        **({"tahlil_notu": m["tahlil_notu"]["metin"]} if m.get("tahlil_notu") else {}),
        # TB-21: form karşılaştırması (ör. B12'de ağızdan–iğne, metil–siyano).
        **({"formlar": {k: v for k, v in m["formlar"].items() if k != "kaynaklar"}} if m.get("formlar") else {}),
        "efsa_ust_sinir": efsa,
        "etkilesimler": etkilesimler,
        "etkilesim_notu": (
            None if etkilesimler else
            "Kural tablosunda bu madde için tanımlı etkileşim yok; bu, etkileşim olmadığı anlamına gelmez."
        ),
        "dikkat_edecekler": dikkat,
        "hekime_sorulacaklar": list(dict.fromkeys(sorular)),
        "katalogdaki_urunler": katalog,
        "katalog_ozeti": katalog_ozeti,
        "gizlilik": "Profil bilgileri yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, kaynak_listesi)


def _kartsiz_yanit(em_id, ad, on_ek, zorunlu, efsa, etkilesimler, dikkat, sorular, urun_sayisi, kaynak_idleri) -> dict:
    """Kanıt kartı yoksa ürün listesi ve ürün sayfası beyanları dönmez (TB-05); güvenlik bilgisi kalır."""
    kilavuz = _genel_kilavuz(em_id)
    kaynak_idleri = list(kaynak_idleri) + ([GENEL_KILAVUZ[em_id]] if kilavuz else []) or ["orzax_urunler"]
    return veri.zarf({
        "kisa_ozet": (
            on_ek + f"{ad} için kanıt kartı hazırlanıyor ya da medikal kurul onayı bekliyor. "
            "Kanıt kartı hazır olana kadar ürün listesi gösterilmez."
            + (" Genel bilgi için kurum sayfasına bakılabilir." if kilavuz else "")
        ),
        "etken_madde_adi": ad,
        "genel_ozet": f"{ad} için kanıt kartı hazırlanıyor ya da medikal kurul onayı bekliyor.",
        "zorunlu_uyarilar": zorunlu,
        "kanit_durumu": "Kanıt kartı hazırlanıyor.",
        "genel_kilavuz": kilavuz,
        "efsa_ust_sinir": efsa,
        "etkilesimler": etkilesimler,
        "etkilesim_notu": (
            None if etkilesimler else
            "Kural tablosunda bu madde için tanımlı etkileşim yok; bu, etkileşim olmadığı anlamına gelmez."
        ),
        "dikkat_edecekler": dikkat,
        "hekime_sorulacaklar": list(dict.fromkeys(sorular)),
        "katalog_kapsami": _katalog_sayisi_metni(urun_sayisi),
        "gizlilik": "Profil bilgileri yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, veri.kaynaklar(dict.fromkeys(kaynak_idleri)))


# --------------------------------------------------------------------------- #
# 6. sikayet_yolu (TB-19)
# --------------------------------------------------------------------------- #


def sikayet_yolu(sikayet: str, yas: int | None = None, cinsiyet: str | None = None) -> dict:
    """Şikâyetten yola çıkar: kırmızı bayrak, hekimin isteyebileceği tahliller, karne ve ilgili kanıt kartları.

    Ürün listesi ve ürün önerisi döndürmez; kanıt kartı olmayan maddede bunu söyler.
    """
    sid = veri.sikayet_id(sikayet)
    if sid is None:
        return veri.zarf({
            "kisa_ozet": (f"'{sikayet}' için şikâyet yolu henüz hazırlanmadı. Hazır yollar: "
                          + ", ".join(y["ad"] for y in veri.sikayet_yollari().values()) + ". "
                          "Süren ya da yeni başlayan bir yakınma hekimle değerlendirilmelidir."),
            "hazir_yollar": [y["ad"] for y in veri.sikayet_yollari().values()],
            "kopru": KOPRU_KARNE,
        }, veri.kaynaklar(["orzax_urunler"]))

    yol = veri.sikayet_yollari()[sid]
    profil = {"yas": yas, "cinsiyet": cinsiyet}
    kaynak_idleri: list[str] = []
    bayraklar = []
    for b in yol["kirmizi_bayraklar"]:
        if _kosul_saglanir(b["kosul"], profil):
            bayraklar.append({"mesaj": b["mesaj"], "dayanak": [_kunye(i) for i in b["kaynaklar"]]})
            kaynak_idleri += b["kaynaklar"]
    kaynak_idleri += yol["tahliller"]["kaynaklar"]

    uyarilar = {u["id"]: u for em in yol["ilgili_maddeler"] for u in veri.zorunlu_uyarilar(em)}
    tahlil_oncesi = []
    for uid in yol["tahlil_oncesi_uyarilari"]:
        tahlil_oncesi.append(uyarilar[uid]["mesaj"])
        kaynak_idleri += uyarilar[uid]["kaynaklar"]

    kartlar = []
    for em_id in yol["ilgili_maddeler"]:
        m = veri.monografi(em_id)
        if m is None:
            kartlar.append({"etken_madde": _rehber_adi(em_id), "durum": "Kanıt kartı hazırlanıyor."})
            continue
        for k in m["kartlar"]:
            kartlar.append({
                "etken_madde": m["ad"], "sonuc_alani": k["sonuc_alani"], "populasyon": k["populasyon"],
                "duzey": k["kanit_duzeyi"], "sonuc_yonu": k["sonuc_yonu"],
                **({"durum": TASLAK_NOTU} if k["durum"] == "taslak" else {}),
            })
            kaynak_idleri += k["kaynaklar"]

    return veri.zarf({
        "kisa_ozet": (bayraklar[-1]["mesaj"] + " " if len(bayraklar) > 2 else "") + yol["giris"],
        **({"durum": "Taslak: bu şikâyet yolu medikal kurul onayı bekliyor."} if yol["durum"] == "taslak" else {}),
        "kirmizi_bayraklar": bayraklar,
        "hekimin_isteyebilecegi_tahliller": {"liste": yol["tahliller"]["liste"], "not": yol["tahliller"]["not"]},
        "tahlil_oncesi": tahlil_oncesi,
        "yasam_karnesi": {"oneri": yol["karne"], "arac": "yasam_karnesi"},
        "ilgili_kanit_kartlari": kartlar,
        "kanit_karti_araci": "etken_madde_rehberi",
        "beyan_aciklamasi": BEYAN_ACIKLAMASI,
        "urun_notu": "Bu yol ürün önermez. Belirli bir ürünün etiket bilgisi için ürün adıyla sorulabilir.",
        "kopru": kopru_kartlar(yol["ilgili_maddeler"], yas=yas, cinsiyet=cinsiyet) or KOPRU_KARNE,
        "gizlilik": "Bilgiler yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, veri.kaynaklar(dict.fromkeys(kaynak_idleri)))


def katalog_sayfasi(etken_madde: str, sayfa: int = 1, yas: int | None = None) -> dict:
    """Görsel kartın sayfalama aracı (modelden gizli). Kanıt kartı sunulamayan maddede ürün döndürmez (TB-05)."""
    em_id = _rehber_id(etken_madde)
    if em_id is None or not veri.urun_listesi_gosterilir(em_id):
        return veri.zarf({
            "kisa_ozet": "Kanıt kartı olmayan maddede ürün listesi gösterilmez.",
            "urunler": [], "sayfa": sayfa, "toplam_sayfa": 0,
        }, veri.kaynaklar(["orzax_urunler"]))
    _, uygun, yas_disi = _katalog_urunleri(em_id, yas)
    toplam_sayfa = max(1, -(-len(uygun) // KATALOG_SINIRI))
    secilen = uygun[(sayfa - 1) * KATALOG_SINIRI: sayfa * KATALOG_SINIRI]
    return veri.zarf({
        "kisa_ozet": f"{_rehber_adi(em_id)}: {len(uygun)} ürünün {sayfa}. sayfası.",
        "urunler": [_katalog_ogesi(u, em_id, _madde_beyanlari(u, em_id)) for u in secilen],
        "sayfa": sayfa, "toplam_sayfa": toplam_sayfa, "toplam_urun": len(uygun),
        **({"yas_siniri_disinda_kalan": len(yas_disi)} if yas_disi else {}),
        "siralama_olcutu": ("Yalnızca bu maddeyi içeren ürünler önce, sonra alfabetik. "
                            "Sponsorlu veya öncelikli sıralama yoktur; sıra bir öneri değildir."),
    }, [veri.urun_kaynagi(u) for u in secilen] or veri.kaynaklar(["orzax_urunler"]))


# --------------------------------------------------------------------------- #
# 7. karsilastir (v0.3 Bölüm 5): bir maddeyi içeren katalog ürünlerinin etikete göre kıyası
# --------------------------------------------------------------------------- #

Form = Literal["damla", "sprey", "tablet", "kapsul", "cigneme", "toz", "efervesan", "sase"]
# Ürün adı ve porsiyon metnindeki ifade → form. Sıra önemlidir: "efervesan tablet" efervesandır, "çiğnenebilir tablet" çiğnemedir.
_FORM_IFADELERI = [
    ("efervesan", "efervesan"), ("gummies", "cigneme"), ("gummy", "cigneme"), ("cignenebilir", "cigneme"),
    ("sase", "sase"), ("damla", "damla"), ("sprey", "sprey"), ("puf", "sprey"), ("pufta", "sprey"),
    ("softjel", "kapsul"), ("softgel", "kapsul"), ("kapsul", "kapsul"), ("tablet", "tablet"), ("toz", "toz"),
    ("olcek", "toz"),
]
KIYAS_SAYFA_BOYU = 40
KATALOG_MARKALARI = {"orzax", "ocean", "day2day", "bigflor", "imunol", "supradyn"}
KIYAS_SIRALAMA = ("Önce yalnızca bu maddeyi içeren ürünler, sonra porsiyondaki miktar (artan), sonra alfabetik. "
                  "Sıra öneri değildir; fiyat ya da sponsorluk yoktur.")


def urun_formu(u: dict) -> str:
    """Önce ürün adı, sonra porsiyon, en son kullanım metni okunur ("her pufu 3 damlaya denk" spreyi damla yapmasın)."""
    for metin in (u["ad"], u.get("porsiyon"), u.get("etiketteki_kullanim")):
        n = f" {veri.normalize(metin or '')} "
        bulunan = next((f for ifade, f in _FORM_IFADELERI if f" {ifade}" in n), None)
        if bulunan:
            return bulunan
    return "diger"


def _kiyas_satiri(u: dict, em_id: str, yas: int | None, ilac_grubu: list[str] | None) -> dict:
    satirlar = _katalog_eslesmesi(em_id, u)
    birim = veri.kurallar()["etken_maddeler"].get(em_id, {}).get("birim")
    miktarlar = [veri.satir_miktari(e) for e in satirlar]
    miktar = sum(miktarlar) if satirlar and all(m is not None for m in miktarlar) else None
    sinir = veri.ust_sinir(em_id, 18 if yas is None else yas)
    oran = round(miktar / sinir["deger"] * 100) if miktar is not None and sinir else None
    ug = None if miktar is None else miktar * {"g": 1_000_000, "mg": 1_000, "µg": 1}.get(birim, 1)
    bayraklar = etkilesim_bayraklari(u, ilac_grubu)
    yas_disi = yas is not None and _yas_disinda(u["yas_siniri"], yas)
    return {
        "ad": u["ad"], "marka": u["marka"], "seri": u["seri"], "form": urun_formu(u), "porsiyon": u["porsiyon"],
        "tek_bilesen": _tek_icerikli(u, em_id),
        "porsiyondaki_miktar": None if miktar is None else round(miktar, 3),
        "birim": birim,
        "porsiyondaki_miktar_ug": None if ug is None else round(ug, 3),
        "etiketteki_miktar": "; ".join(f"{e['etiketteki_ad']}: {_etiket_miktari(e, u)}" for e in satirlar),
        "brd": "; ".join(e["brd"] for e in satirlar if e.get("brd")) or None,
        "efsa_siniri": None if not sinir else f"{_sayi(sinir['deger'])} {sinir['birim']} / gün",
        "efsa_sinir_degeri": None if not sinir else sinir["deger"],
        "efsa_orani": oran,
        "ek_etken_maddeler": [e["etiketteki_ad"] for e in u["etken_maddeler"] if e not in satirlar],
        "yas_siniri": _yas_metni(u["yas_siniri"]),
        **({"yas_siniri_disinda": yas_disi} if yas is not None else {}),
        "uyari_bayraklari": [b["metin"] for b in bayraklar] + (["Yaş sınırı dışında"] if yas_disi else [])
                            + (["Bir satır doğrulanamadı"] if any(e.get("karantina") for e in satirlar) else []),
        "kirmizi_bayrak": any(b["kirmizi"] for b in bayraklar),
        "kirmizi_bayraklar": [b["metin"] for b in bayraklar if b["kirmizi"]],
        "parti_analizi_var": veri.gercek_parti_analizi_var(u["id"]),
        "urun_sayfasi": u["kaynak"]["url"],
    }


def karsilastir(
    etken_madde: str,
    form: str | None = None,
    yas: int | None = None,
    sadece_tek_bilesen: bool = False,
    marka: str | None = None,
    ilac_grubu: list[str] | None = None,
    sayfa: int = 1,
) -> dict:
    """Maddeyi içeren tüm katalog ürünleri, etiketteki ölçütlerle tek tabloda. Sıralama öneri değildir."""
    ilaclar = [i for i in (ilac_grubu or []) if i != "yok"]
    # Katalog dışı marka: alakasız aday listelenmez (v0.3 Bölüm 5.5).
    if marka and not set(veri.normalize(marka).split()) & KATALOG_MARKALARI:
        return veri.zarf({
            "kisa_ozet": (f"Katalog şu an yalnızca Orzax ürünlerini içeriyor; {marka} için etiket verisi yok. Kutudaki etiket "
                          "içeriğini yazarsanız kisisel_rutin ile toplam miktarı kontrol edebilirim."),
            "katalog_kapsami": "Katalog şu an yalnızca Orzax ürünlerini içerir.",
            "istenen_marka": marka,
            "satirlar": [],
            "onerilen_sonraki_arac": "kisisel_rutin",
        }, veri.kaynaklar(["orzax_urunler"]))

    em_id = _rehber_id(etken_madde)
    if em_id is None:
        return veri.zarf({
            "kisa_ozet": f"'{etken_madde}' kural tablosunda tanımlı bir etken madde değil. Adı farklı yazmayı deneyin (ör. 'D vitamini').",
            "satirlar": [],
        }, veri.kaynaklar(["orzax_urunler"]))
    ad = gorunen_ad(em_id)
    eslesen = [u for u in veri.urunler() if _katalog_eslesmesi(em_id, u)]
    # Tek gösterim kuralı (v0.3 Ek 4): sunulabilir kanıt kartı yoksa ürün listelenmez, yalnızca sayı verilir.
    if not veri.urun_listesi_gosterilir(em_id):
        return veri.zarf({
            "kisa_ozet": (f"{ad} için kanıt kartı hazırlanıyor; kart hazır olana kadar ürün listesi ve kıyas gösterilmez. "
                          f"Katalogda bu maddeyi içeren {len(eslesen)} ürün var."),
            "etken_madde_adi": ad, "kart_durumu": veri.kart_durumu(em_id),
            "katalogdaki_urun_sayisi": len(eslesen), "satirlar": [],
        }, veri.kaynaklar([GENEL_KILAVUZ[em_id]] if _genel_kilavuz(em_id) else ["orzax_urunler"]))

    satirlar = [_kiyas_satiri(u, em_id, yas, ilaclar) for u in eslesen]
    if form:
        satirlar = [r for r in satirlar if r["form"] == form]
    if sadece_tek_bilesen:
        satirlar = [r for r in satirlar if r["tek_bilesen"]]
    satirlar.sort(key=lambda r: (not r["tek_bilesen"], r["porsiyondaki_miktar"] is None,
                                 r["porsiyondaki_miktar"] or 0, veri.normalize(r["ad"])))
    toplam_sayfa = max(1, -(-len(satirlar) // KIYAS_SAYFA_BOYU))
    secilen = satirlar[(sayfa - 1) * KIYAS_SAYFA_BOYU: sayfa * KIYAS_SAYFA_BOYU]
    formlar = sorted({r["form"] for r in satirlar})
    sinir_kaydi = veri.kurallar()["ust_sinirlar"].get(em_id)
    kirmizi = [r["ad"] for r in secilen if r["kirmizi_bayrak"]]
    kosullar = ([f"form: {form}"] if form else []) + (["yalnızca tek bileşenli"] if sadece_tek_bilesen else [])
    return veri.zarf({
        "kisa_ozet": (f"{ad} içeren {len(satirlar)} katalog ürünü etikete göre kıyaslandı"
                      + (f" ({', '.join(kosullar)})" if kosullar else "") + ". Sıra öneri değildir."
                      + (f" Belirttiğiniz ilaç grubu için {len(kirmizi)} üründe etkileşim bayrağı var; hekiminize danışın." if kirmizi else "")),
        "etken_madde_adi": ad,
        "kart_durumu": veri.kart_durumu(em_id),
        "efsa_sinir_grubu": "yetişkin" if yas is None else f"{yas} yaş grubu",
        **({"yas": yas} if yas is not None else {}),
        "formlar": formlar,
        "satirlar": secilen,
        "toplam_urun": len(satirlar), "sayfa": sayfa, "toplam_sayfa": toplam_sayfa,
        "siralama_olcutu": KIYAS_SIRALAMA,
        "katalog_kapsami": "Katalog şu an yalnızca Orzax ürünlerini içerir.",
        "efsa_notu": "EFSA değeri bir güvenlik tavanıdır, alınması gereken miktar değildir; oran porsiyon başınadır.",
        "kanit_karti_araci": "etken_madde_rehberi",
    }, veri.kaynaklar((sinir_kaydi or {}).get("kaynaklar", []) or ["orzax_urunler"],
                      [veri.urun_kaynagi(u) for u in eslesen if u["ad"] in {r["ad"] for r in secilen}][:5]))


# --------------------------------------------------------------------------- #
# 9. Köprü (v0.3 Bölüm 1): kapı araçları kullanıcıya sorulacak tek cümleyle biter
# --------------------------------------------------------------------------- #

KOPRU_KART_SORUSU = ("Bu maddelerin kanıt kartlarını (100 kişilik görsel, güvenlik uyarıları) Takviye Bilimi'nde "
                     "görmek ister misiniz?")


def _profil_parametreleri(**alanlar) -> dict:
    return {k: v for k, v in alanlar.items() if v not in (None, [], "")}


def kopru_kartlar(em_idler: list[str], **profil) -> dict | None:
    """Kanıt kartı sunulabilir maddeler için 'evet' denirse çağrılacak etken_madde_rehberi listesi."""
    hazir = [e for e in em_idler if veri.urun_listesi_gosterilir(e)]
    if not hazir:
        return None
    return {"soru": KOPRU_KART_SORUSU if len(hazir) > 1 else KOPRU_KART_SORUSU.replace("Bu maddelerin", f"{gorunen_ad(hazir[0])}"),
            "evet_ise": [{"arac": "etken_madde_rehberi",
                          "parametreler": {"etken_madde": gorunen_ad(e), **_profil_parametreleri(**profil)}} for e in hazir]}


KOPRU_KARNE = {"soru": "Takviyeden önce uyku, hareket ve beslenme alışkanlıklarınızı 6 soruluk yaşam karnesiyle görmek ister misiniz?",
               "evet_ise": [{"arac": "yasam_karnesi", "parametreler": {}}]}


# --------------------------------------------------------------------------- #
# 10. takviye_rehberi (v0.3 Bölüm 4): kapı aracı, kartsız
# --------------------------------------------------------------------------- #

Hedef = Literal["kis_bagisiklik", "kemik_kas", "gebelik", "cocuk_ergen", "yas_50_ustu", "vegan_vejetaryen", "spor",
                "sac_cilt_tirnak"]
GENEL_KILAVUZ_EK = {"kalsiyum": "nih_ods_kalsiyum_hp", "k2": "nih_ods_k_vitamini_hp"}
SORULACAKLAR = {
    "yas_araligi": {"alan": "yas_araligi", "soru": "Kaç yaş aralığındasınız?", "secenekler": ["1–10", "11–17", "18–64", "65 ve üzeri"]},
    "evre": {"alan": "evre", "soru": "Gebelik ya da emzirme durumunuz nedir?", "secenekler": ["Yok", "Planlıyor", "Gebe", "Emziriyor"]},
    "ilac_grubu": {"alan": "ilac_grubu", "soru": "Düzenli kullandığınız bir ilaç grubu var mı?",
                   "secenekler": ["Yok", "Kan sulandırıcı", "Tiroid hormonu", "Diğer"]},
}
SORU_YONERGESI_KAPI = ("Profil eksik: soruları seçenekleriyle, tek mesajda sorun. Cevaba göre yas, evre ve ilac_grubu "
                       "parametreleriyle aracı yeniden çağırın.")


def hedef_bul(metin: str) -> str | None:
    n = f" {veri.normalize(metin)} "
    for hid, h in veri.hedef_eslemesi()["hedefler"].items():
        if any(f" {veri.normalize(e)} " in n for e in [hid.replace('_', ' '), *h["esanlamlar"]]):
            return hid
    return None


# Kullanıcıya gösterilen ad: kural tablosundaki teknik ad yerine sohbet dilindeki ad.
_GORUNEN_AD = {"d3": "D vitamini", "omega3": "Omega-3", "k2": "K2 vitamini"}


def gorunen_ad(em_id: str) -> str:
    return _GORUNEN_AD.get(em_id) or (_rehber_adi(em_id) if em_id in veri.kurallar()["etken_maddeler"] or em_id == "multivitamin" else em_id)


def _madde_adi(kayit: dict) -> str:
    ad = kayit.get("ad") or gorunen_ad(kayit["etken_madde"])
    return f"{ad} ({kayit['not']})" if kayit.get("not") else ad


def _kart_ozeti(m: dict, kart_adlari: list[str]) -> tuple[str, list[str]]:
    """Kanıt kartlarından 1–2 cümle: sonuç alanı, sonuç etiketi ve 100 kişide mutlak fark."""
    if kart_adlari == []:
        # Eşlemede bu hedefe uyan kart yoksa ilgisiz bir kart özetlenmez.
        return "Bu konuya özgü kanıt kartı henüz yok; kimde kanıt olduğu aşağıda.", []
    kartlar = [k for k in m["kartlar"] if k["id"].split("__", 1)[1] in (kart_adlari or [])] or m["kartlar"]
    parcalar, kaynak = [], []
    for k in kartlar[:2]:
        etiket = SONUC_ETIKETLERI[sonuc_etiketi(k)].casefold()
        parcalar.append(f"{k['sonuc_alani']} ({k['populasyon']}): {etiket}. {k['mutlak_fark']['metin']}")
        kaynak += k["kaynaklar"]
    return " ".join(parcalar), kaynak


def _madde_ozeti(kayit: dict, profil: dict) -> tuple[dict, list[str]]:
    em_id = kayit["etken_madde"]
    tanimli = em_id in veri.kurallar()["etken_maddeler"]
    durum = veri.kart_durumu(em_id) if tanimli else veri.KART_HAZIRLANIYOR
    o: dict = {"etken_madde": _madde_adi(kayit), "kart_durumu": durum}
    kaynak: list[str] = []
    guvenlik = []
    for u in veri.zorunlu_uyarilar(em_id):
        if _kosul_saglanir(u["kosul"], profil):
            guvenlik.append(u["mesaj"])
            kaynak += u["kaynaklar"]
    if profil["ilac_grubu"] or profil["evre"]:
        for kural in veri.kurallar()["etkilesimler"]:
            kosul = kural["kosul"]
            if em_id not in _liste(kosul["etken_madde"]):
                continue
            if set(_liste(kosul.get("ilac_grubu", []))) & set(profil["ilac_grubu"]) or profil["evre"] in kosul.get("evre", []):
                guvenlik.append(kural["mesaj"])
                kaynak += kural.get("kaynaklar", [])
    if durum == veri.KART_HAZIRLANIYOR:
        o["not"] = "Kanıt kartı hazırlanıyor."
        kid = GENEL_KILAVUZ.get(em_id) or GENEL_KILAVUZ_EK.get(em_id)
        k = veri.kaynaklar([kid]) if kid and kid in veri.kaynak_kayitlari() else []
        if k:
            o["genel_bilgi"] = k[0]["url"]
            kaynak.append(kid)
        if guvenlik:
            o["guvenlik"] = guvenlik
        return o, kaynak
    m = veri.monografi(em_id)
    ozet, kart_kaynak = _kart_ozeti(m, kayit.get("kartlar"))
    kaynak += kart_kaynak
    o["ozet"] = ozet
    profil_verildi = any(profil[a] for a in ("yas", "evre", "ilac_grubu"))
    grup = next((g for g in m.get("kimde_kanit_var", []) if profil_verildi and "kosul" in g and _kosul_saglanir(g["kosul"], profil)), None)
    if grup:
        o["kimde_kanit"] = f"Senin grubun: {grup['grup']}. {grup['gerekce']}"
        kaynak += grup["kaynaklar"]
    elif m.get("kimde_kanit_var"):
        o["kimde_kanit"] = "Kanıt özetindeki gruplar: " + "; ".join(g["grup"] for g in m["kimde_kanit_var"]) + "."
    if guvenlik:
        o["guvenlik"] = guvenlik
    if m.get("besinle_karsilama"):
        o["besinle_karsilama"] = m["besinle_karsilama"]["metin"]
        kaynak += m["besinle_karsilama"]["kaynaklar"]
    o["katalogdaki_urun_sayisi"] = len([u for u in veri.urunler() if _katalog_eslesmesi(em_id, u)])
    return o, kaynak


def takviye_rehberi(
    konu: str,
    hedef: str | None = None,
    etken_madde: str | None = None,
    yas: int | None = None,
    cinsiyet: str | None = None,
    evre: str | None = None,
    ilac_grubu: list[str] | None = None,
) -> dict:
    """Kapı aracı: hedef, mevsim, yaşam evresi ya da tek madde sorusu. Ürün önermez, ürün listelemez."""
    em_id = _rehber_id(etken_madde) if etken_madde else None
    if etken_madde is None and hedef is None:
        hedef = hedef_bul(konu)
        if hedef is None:
            em_id = veri.sorgudaki_etken_madde(konu)
    elif hedef is None and em_id is None:
        hedef = hedef_bul(konu)
    eslem = veri.hedef_eslemesi()
    h = eslem["hedefler"].get(hedef) if hedef and not em_id else None
    profil = {"yas": yas, "cinsiyet": cinsiyet, "evre": evre, "sigara": None,
              "ilac_grubu": [i for i in (ilac_grubu or []) if i != "yok"]}

    # Eksik profil: seçenekli sorular. Gebelik hedefinde gebelik sorusu sorulmaz; erkekte gebelik sorulmaz.
    sorulacaklar = []
    if yas is None:
        sorulacaklar.append(SORULACAKLAR["yas_araligi"])
    if evre is None and cinsiyet != "erkek" and not (h and h.get("evre_belirler")) and (yas is None or 11 <= yas <= 55):
        sorulacaklar.append(SORULACAKLAR["evre"])
    if ilac_grubu is None:
        sorulacaklar.append(SORULACAKLAR["ilac_grubu"])

    if em_id is not None:
        kayitlar, baslik, eslem_durumu = [{"etken_madde": em_id}], gorunen_ad(em_id), None
    elif h is not None:
        if not veri.sunulabilir(eslem):
            return veri.zarf({
                "kisa_ozet": (f"'{h['ad']}' konusu için madde eşlemesi medikal kurul onayı bekliyor. Belirli bir maddeyi "
                              "adıyla sorabilir ya da bir yakınmanız varsa onu anlatabilirsiniz."),
                "hedef": hedef, "eslem_durumu": eslem["durum"], "maddeler": [], "sorulacaklar": sorulacaklar,
                "kopru": KOPRU_KARNE,
            }, veri.kaynaklar(["orzax_urunler"]))
        kayitlar, baslik, eslem_durumu = h["maddeler"], h["ad"], eslem["durum"]
    else:
        return veri.zarf({
            "kisa_ozet": ("Sorunuzu bir hedefe ya da maddeye eşleyemedim. Hazır konular: "
                          + ", ".join(x["ad"] for x in eslem["hedefler"].values())
                          + ". Bir maddeyi adıyla da sorabilirsiniz (ör. 'D vitamini')."),
            "hedef": None, "maddeler": [], "hazir_konular": [x["ad"] for x in eslem["hedefler"].values()],
            "sorulacaklar": sorulacaklar, "kopru": KOPRU_KARNE,
        }, veri.kaynaklar(["orzax_urunler"]))

    maddeler, kaynak_idleri = [], []
    for kayit in kayitlar:
        o, k = _madde_ozeti(kayit, profil)
        maddeler.append(o)
        kaynak_idleri += k
    besin = [f"{o['etken_madde']}: {o.pop('besinle_karsilama')}" for o in maddeler if o.get("besinle_karsilama")]
    ids = [k["etken_madde"] for k in kayitlar if k["etken_madde"] in veri.kurallar()["etken_maddeler"]]
    kopru = kopru_kartlar(ids, yas=yas, cinsiyet=cinsiyet, evre=profil["evre"], ilac_grubu=profil["ilac_grubu"] or None) or KOPRU_KARNE
    hazir = [o for o in maddeler if o["kart_durumu"] != veri.KART_HAZIRLANIYOR]
    adlar = ", ".join(o["etken_madde"] for o in maddeler)
    return veri.zarf({
        "kisa_ozet": (f"{baslik}: kısa kanıt özeti ve güvenlik notları." if em_id else f"{baslik} için sık sorulan maddeler: {adlar}.")
                     + " Bu bir öneri listesi değildir; ürün önerilmez.",
        "hedef": hedef if not em_id else None,
        **({"eslem_durumu": eslem_durumu} if eslem_durumu else {}),
        "maddeler": maddeler,
        "besinle_karsilama": (" ".join(besin) + " " if besin else "")
                             + "Beslenme ve yaşam alışkanlıklarınızı görmek için yaşam karnesi doldurulabilir (yasam_karnesi).",
        "katalog_notu": " ".join(f"{o['etken_madde']}: katalogda {o['katalogdaki_urun_sayisi']} ürün var; içeriğe göre kıyas için sorabilirsiniz."
                                 for o in hazir) or None,
        "sorulacaklar": sorulacaklar,
        **({"soru_yonergesi": SORU_YONERGESI_KAPI} if sorulacaklar else {}),
        "kopru": kopru,
        "gizlilik": "Bilgiler yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, veri.kaynaklar(dict.fromkeys(kaynak_idleri)) or veri.kaynaklar(["orzax_urunler"]))


# --------------------------------------------------------------------------- #
# 8. tahlil_goster (istemci tarafında tahlil görünümü)
# --------------------------------------------------------------------------- #

# Tahlil değeri bu araca hiç gelmez: aracın değer parametresi yoktur. Kullanıcı değerini ve kendi laboratuvarının
# referans aralığını görsel kartın içine yazar; kart değeri sunucuya göndermez, saklamaz (KVKK: sağlık verisi).
TAHLILLER = {
    "b12": {"ad": "B12 vitamini", "etken_madde": "b12", "esanlamlar": ["b12", "b12 vitamini", "kobalamin"],
            "ne_olcer": "Kandaki B12 vitamini düzeyi.", "birimler": ["pg/mL", "pmol/L"],
            "kaynaklar": ["bsh_b12_folat_2014"]},
    "ferritin": {"ad": "Ferritin", "etken_madde": "demir", "esanlamlar": ["ferritin", "demir", "demir deposu"],
                 "ne_olcer": "Vücuttaki demir depolarının göstergesi; demir eksikliğinde en yararlı tek göstergedir.",
                 "birimler": ["ng/mL", "µg/L"], "kaynaklar": ["bsg_demir_eksikligi_2021"]},
    "d_vitamini": {"ad": "D vitamini (25(OH)D)", "etken_madde": "d3",
                   "esanlamlar": ["d vitamini", "25 oh d", "25 hidroksi d vitamini", "d3"],
                   "ne_olcer": "Kandaki 25(OH)D düzeyi; D vitamini durumunun göstergesidir.", "birimler": ["ng/mL", "nmol/L"],
                   "kaynaklar": ["zittermann_d_doz_yanit_2014"]},
}
TAHLIL_GIZLILIK = ("Değerin sunucuya gönderilmez: yalnızca bu kartta, kendi cihazında işlenir ve saklanmaz. "
                   "Kart sabit bir 'normal' aralık kullanmaz; raporundaki referans aralığını yazarsın.")


def _tahlil_id(metin: str) -> str | None:
    n = f" {veri.normalize(metin)} "
    return next((tid for tid, t in TAHLILLER.items() if any(f" {veri.normalize(e)} " in n for e in [tid, *t["esanlamlar"]])), None)


def tahlil_goster(tahlil: str) -> dict:
    tid = _tahlil_id(tahlil)
    if tid is None:
        return veri.zarf({
            "kisa_ozet": f"'{tahlil}' için tahlil görünümü henüz yok. Hazır olanlar: " + ", ".join(t["ad"] for t in TAHLILLER.values()) + ".",
            "hazir_tahliller": [t["ad"] for t in TAHLILLER.values()],
            "gizlilik": TAHLIL_GIZLILIK,
        }, veri.kaynaklar(["orzax_urunler"]))
    t = TAHLILLER[tid]
    kaynak_idleri: list[str] = list(t["kaynaklar"])
    oncesi = [u for u in veri.zorunlu_uyarilar(t["etken_madde"]) if u["tur"] == "tahlil_oncesi"]
    for u in oncesi:
        kaynak_idleri += u["kaynaklar"]
    # Monografi taslak olsa da tahlil notu yalnızca sunulabilirse gösterilir.
    m = veri.monografi(t["etken_madde"])
    notu = (m or {}).get("tahlil_notu")
    if notu:
        kaynak_idleri += notu["kaynaklar"]
    return veri.zarf({
        "kisa_ozet": (f"{t['ad']} tahlili: {t['ne_olcer']} Değerini kendi laboratuvarının referans aralığıyla kartta görebilirsin; "
                      "değer sunucuya gönderilmez. Sonucu hekiminle değerlendir."),
        "tahlil": t["ad"],
        "ne_olcer": t["ne_olcer"],
        "yaygin_birimler": t["birimler"],
        "birim_notu": "Değer ile referans aralığı aynı birimde olmalıdır; raporundaki birimi kullan.",
        "tahlil_oncesi": [u["mesaj"] for u in oncesi],
        **({"tahlil_notu": notu["metin"]} if notu else {}),
        "yorum_notu": ("Kart yalnızca değerin raporundaki aralığa göre konumunu gösterir. Takviyeyle değerin nasıl değişeceğine "
                       "dair tahmin yapmaz; tanı ve tedavi kararı hekimindir."),
        "gizlilik": TAHLIL_GIZLILIK,
    }, veri.kaynaklar(dict.fromkeys(kaynak_idleri)))
