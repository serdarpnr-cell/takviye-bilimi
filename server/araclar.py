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
PARTI_ANALIZI_NOTU = "Katalogdaki ürünler için yayımlanmış parti analizi bulunmuyor."


def _etiket_miktari(em: dict, u: dict) -> str:
    if not em.get("miktar_metni"):
        return "Ürün sayfasında yazmıyor"
    porsiyon = em.get("porsiyon") or u.get("porsiyon")
    return f"{em['miktar_metni']} ({porsiyon.casefold()})" if porsiyon else em["miktar_metni"]


def _urun_karti(u: dict) -> dict:
    etkenler = []
    for em in u["etken_maddeler"]:
        em_id = em["etken_madde"]
        std = veri.satir_miktari(em)
        sinir = veri.ust_sinir(em_id, 18) if em_id else None
        etkenler.append({
            "etken_madde": em["etiketteki_ad"],
            # "Bu üründeki miktar" bloğu: yalnızca rakam, yorum yok.
            "bu_urundeki_miktar": {
                "etiketteki_miktar": _etiket_miktari(em, u),
                "beslenme_referans_degeri": em["brd"],
                "standart_birimde": None if std is None else f"{_sayi(std)} {veri.kurallar()['etken_maddeler'][em_id]['birim']}",
                "yetiskin_ust_siniri": _sinir_metni(em_id, sinir) if em_id else None,
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
        "etiketteki_kullanim": u["etiketteki_kullanim"],
        "yas_siniri": _yas_metni(u["yas_siniri"]),
        "saglik_beyanlari": beyan.get("saglik", []),
        "beslenme_beyanlari": beyan.get("beslenme", []),
        "beyan_kullanim_kosullari": beyan.get("kullanim_kosullari", []),
        "beyan_notu": "Beyanlar ürün sayfasındaki metinlerdir; ürüne ait etki ifadesi yalnızca bunlardır.",
        "etiket_uyarilari": ETIKET_UYARISI_NOTU,
        "parti_analizi": PARTI_ANALIZI_NOTU,
        "urun_sayfasi": u["kaynak"]["url"],
        "erisim_tarihi": u["kaynak"]["erisim_tarihi"],
    }


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


def urun_rehberi(urun: str) -> dict:
    adaylar = veri.urun_ara(urun)
    if len(adaylar) == 1:
        u = adaylar[0]
        return veri.zarf({
            "kisa_ozet": f"{u['ad']} ({u['marka']}) için etiket bilgileri. Ürün düzeyindeki etki ifadeleri yalnızca ürün sayfasındaki beyanlardan gelir.",
            "urun": _urun_karti(u),
        }, _urun_kaynaklari(u))
    if len(adaylar) > 1:
        return veri.zarf({
            "kisa_ozet": f"'{urun}' birden fazla ürünle eşleşti. Hangisini kastettiğinizi belirtin.",
            "adaylar": sorted((a["ad"] for a in adaylar), key=veri.normalize),
            "siralama_olcutu": "Alfabetik.",
        }, veri.kaynaklar(["orzax_urunler"]))
    # Eşleşme yoksa sorgudaki kelimelerden en az birini içeren ürünleri listeler.
    kelimeler = set(veri.normalize(urun).split())
    benzer = sorted(
        (x["ad"] for x in veri.urunler() if kelimeler & set(veri.normalize(x["ad"]).split())),
        key=veri.normalize,
    )
    return veri.zarf({
        "kisa_ozet": f"'{urun}' katalogda bulunamadı. Ürün adını kutudaki gibi yazmayı deneyin.",
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
    return veri.zarf({
        "kisa_ozet": f"'{parti_no}' parti numarası için yayımlanmış analiz bulunamadı. {PARTI_ANALIZI_NOTU}",
        "aranan_parti_no": parti_no,
        "not": "Parti numarası kutunun alt ya da yan yüzünde, son kullanma tarihinin yanında yazar. "
               "Ürünün etiket bilgileri için ürün rehberine bakılabilir.",
    }, veri.kaynaklar(["orzax_urunler"]))


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
        ust_sinir_kontrolu.append({
            "etken_madde": veri.etken_madde_adi(em_id),
            "takviyelerden_toplam": (
                f"{_sayi(toplam)} {sinir['birim']} / gün" + (" (yalnızca doğrulanan içerikler)" if eksikler else "")
                if gecerli else "Hesaplanamadı"
            ),
            "efsa_degeri": _sinir_metni(em_id, sinir),
            "asiyor": True if asiyor else (None if eksikler else False),
            "kontrol": "eksik" if eksikler else "tam",
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
        yas_disi = ys["min"] is not None and (yas < ys["min"] or (ys["max"] is not None and yas > ys["max"]))
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
        etkilesimler.append({
            "konu": " + ".join(
                [veri.etken_madde_adi(e) for e in mevcut_em]
                + ([kurallar["ilac_gruplari"][i] for i in _liste(kosul.get("ilac_grubu", [])) if i in ilaclar])
                + ([veri.etken_madde_adi(kosul["diger_etken_madde"])] if "diger_etken_madde" in kosul else [])
            ),
            "seviye": kural["seviye"],
            "mesaj": kural["mesaj"],
        })
        sorular.append(kural["soru"])

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
    "uyku_saat": [
        ("6 saatten az", "6_saatten_az", 0, 5.99), ("6 ile 7 saat arası", "6_7_saat", 6, 6.99),
        ("7–9 saat", "7_9_saat", 7, 9), ("9 saatten fazla, en çok 10", "9_10_saat", 9.01, 10),
        ("10 saatten fazla", "10_saatten_fazla", 10.01, 24),
    ],
    "sebze_meyve_porsiyon": [
        ("0–2 porsiyon", "0_2_porsiyon", 0, 2.99), ("3–4 porsiyon", "3_4_porsiyon", 3, 4.99),
        ("5 porsiyon ya da daha fazla", "5_ve_uzeri", 5, 30),
    ],
    "balik_haftalik": [
        ("Hiç", "hic", 0, 0), ("Ayda 1–3 kez", "ayda_1_3", 0.25, 0.75), ("Haftada 1 kez", "haftada_1", 1, 1.99),
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
    "Altı soruyu tek mesajda, seçenekleriyle birlikte sorun. Kullanıcı bir seçenek ya da aralık seçerse seçenek "
    "kodunu (ör. '1_2_gun'), tam sayı verirse sayıyı iletin."
)

ESIK_NOTU = (
    "Eşikler yetişkinler için genel halk sağlığı önerilerinden sadeleştirilmiştir: haftada en az 150 dakika "
    "orta yoğunlukta hareket (WHO), gecede 7–9 saat uyku (National Sleep Foundation), günde en az 400 g sebze-meyve "
    "(WHO; karnede 5 porsiyon olarak sadeleştirildi), haftada 1–2 kez deniz ürünü (American Heart Association). "
    "Prototiptir; medikal kurul onayı bekler."
)
KARNE_KAYNAKLARI = [
    "who_fiziksel_aktivite_2020", "nsf_uyku_suresi_2015", "who_saglikli_beslenme", "aha_deniz_urunleri_2018", "who_tutun",
]

# Puan: 2 = iyi, 1 = orta, 0 = gelişmeli
_SEVIYE = {2: "iyi", 1: "orta", 0: "gelişmeli"}

_HEDEFLER = {
    "sigara": {
        "alan": "Tütün",
        "hedef": "Bırakmak için bir tarih belirle.",
        "ilk_adim": "ALO 171 Sigara Bırakma Danışma Hattı'nı ara ya da aile hekiminden sigara bırakma desteği iste.",
    },
    "hareket_gun": {
        "alan": "Hareket",
        "hedef": "Haftada 5 gün 30 dakika tempolu hareket.",
        "ilk_adim": "Bu hafta 2 güne birer 20 dakikalık yürüyüş koy; günü ve saati takvime yaz.",
    },
    "uyku_saat": {
        "alan": "Uyku",
        "hedef": "Gecede 7–9 saat uyku.",
        "ilk_adim": "Bu hafta yatış saatini 30 dakika öne al ve her gün aynı saatte kalk.",
    },
    "sebze_meyve_porsiyon": {
        "alan": "Sebze ve meyve",
        "hedef": "Günde en az 5 porsiyon sebze ve meyve.",
        "ilk_adim": "Her ana öğüne bir porsiyon sebze ya da salata ekle.",
    },
    "balik_haftalik": {
        "alan": "Balık",
        "hedef": "Haftada 2 kez balık.",
        "ilk_adim": "Haftalık menüye bir balık günü koy; balık yemiyorsan bunu hekiminle ya da diyetisyenle konuş.",
    },
    "stres": {
        "alan": "Dinlenme",
        "hedef": "Her gün kendine ayrılmış kısa bir dinlenme zamanı.",
        "ilk_adim": "Günde 10 dakika ekransız yürüyüş ya da sessiz bir mola planla.",
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
        return 2 if 7 <= deger <= 9 else 1 if 6 <= deger < 7 or 9 < deger <= 10 else 0
    if anahtar == "sebze_meyve_porsiyon":
        return 2 if deger >= 5 else 1 if deger >= 3 else 0
    if anahtar == "balik_haftalik":
        return 2 if deger >= 2 else 1 if deger >= 1 else 0
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
    """Karne cevaplarından takviye bağlantıları, güvenlik uyarıları ve tahlil önerisi üretir."""
    baglantilar, uyarilar, tahliller, kaynak_idleri = [], [], [], []
    for k in veri.karne_kurallari():
        if not _kural_saglanir(k["kosul"], girilen):
            continue
        kaynak_idleri += k["kaynaklar"]
        if k["tur"] == "takviye_baglantisi":
            baglantilar.append({"tetikleyici": k["tetikleyici"], "etken_madde": _rehber_adi(k["etken_madde"]),
                                "mesaj": k["mesaj"], "onerilen_sonraki_arac": k["onerilen_sonraki_arac"]})
        elif k["tur"] == "guvenlik":
            uyarilar.append({"tetikleyici": k["tetikleyici"], "etken_madde": _rehber_adi(k["etken_madde"]),
                             "mesaj": k["mesaj"], "onerilen_sonraki_arac": k["onerilen_sonraki_arac"]})
        else:
            tahliller.append({"etken_madde": _rehber_adi(k["etken_madde"]), "mesaj": k["mesaj"]})
    return {
        "takviye_baglantilari": baglantilar,
        "guvenlik_uyarilari": uyarilar,
        "tahlil_onerisi": {
            "maddeler": tahliller,
            "not": "Bu maddelerde ihtiyaç karneyle değil, hekimin gerekli gördüğü kan tahliliyle değerlendirilir.",
        },
        "kopru_notu": ("Bağlantılar takviye önerisi değildir; ilgili kanıtı incelemek için yönlendirmedir. "
                       "Kurallar medikal kurul onayı bekler."),
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
            "tum_sorular": SORULAR,
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
    hedefler = [{**_HEDEFLER[a]} for a in gelismeli[:3]]

    notlar = []
    if girilen["stres"] == "neredeyse_her_gun":
        notlar.append("Neredeyse her gün gergin ya da tükenmiş hissetmek bir hekim veya ruh sağlığı uzmanıyla konuşmaya değer.")
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
TASLAK_NOTU = "Taslak: bu kanıt kartı medikal kurul onayı bekliyor."
TASLAK_UYARI_NOTU = "Taslak: bu güvenlik uyarısı medikal kurul onayı bekliyor; onay beklerken de gösterilir."


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


def _urun_beyanlari(u: dict, anahtarlar: list[str], tek_icerik: bool) -> list[str]:
    """Ürün sayfasındaki sağlık beyanlarından bu etken maddeyi anlatanlar (tek içerikli üründe hepsi)."""
    beyanlar = veri.urun_beyanlari().get(u["id"], {}).get("saglik", [])
    if tek_icerik or not anahtarlar:
        return beyanlar
    return [b for b in beyanlar if any(a in veri.normalize(b) for a in anahtarlar)]


def _beyan_anahtari(beyan: str, anahtarlar: list[str]) -> str:
    """"D vitamini normal kemiklerin…" ile "Normal kemiklerin…" aynı beyandır: baştaki madde adı karşılaştırmaya katılmaz."""
    n = veri.normalize(beyan)
    for a in anahtarlar:
        if n.startswith(a + " "):
            return n[len(a) + 1:]
    return n


def _tek_icerikli(u: dict, em_id: str) -> bool:
    kimlikler = {e["etken_madde"] for e in u["etken_maddeler"] if e["etken_madde"]}
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
        return veri.zarf({
            "kisa_ozet": (
                f"'{etken_madde}' için kanıt kartı yok."
                + (" Katalogda bu adı içeren ürünler aşağıda." if urunler else " Adı farklı yazmayı deneyin (ör. 'D vitamini', 'omega-3').")
            ),
            "kanit_karti_hazirlanan_maddeler": [_rehber_adi(i) for i in REHBER_KAPSAMI],
            "katalogda_bu_adi_iceren_urunler": urunler,
            "siralama_olcutu": "Alfabetik. Sponsorlu veya öncelikli sıralama yoktur.",
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
            "gerekce": k["gerekce"],
            "halk_ozeti": k["halk_ozeti"],
            "mutlak_fark": k["mutlak_fark"]["metin"],
            "calismalarda_kullanilan_dozlar": k["calisilan_dozlar"],
            "ne_bilmiyoruz": k["ne_bilmiyoruz"],
            "dayanak": [_kunye(i) for i in k["kaynaklar"]],
            **({"durum": TASLAK_NOTU} if k["durum"] == "taslak" else {}),
        })
        kaynak_idleri += k["kaynaklar"]

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
        etkilesimler.append({"ile": karsi, "seviye": kural["seviye"], "mesaj": kural["mesaj"]})
        if set(_liste(kosul.get("ilac_grubu", []))) & set(profil["ilac_grubu"]):
            dikkat.append(kural["mesaj"])
            sorular.append(kural["soru"])

    # EFSA üst sınırı: güvenlik tavanı, öneri değil.
    sinir_kaydi = kurallar["ust_sinirlar"].get(em_id)
    efsa = None
    if sinir_kaydi:
        sinir = veri.ust_sinir(em_id, yas if yas is not None else 18)
        efsa = {
            "deger": _sinir_metni(em_id, sinir),
            "yas_grubu": "yetişkin" if yas is None else f"{yas} yaş",
            "kapsam": sinir_kaydi["kapsam"],
            "not": "Bu değer bir güvenlik tavanıdır; alınması gereken miktar değildir.",
        }
        kaynak_idleri += sinir_kaydi["kaynaklar"]

    # Katalog: nötr ve belgelenmiş sıra (alfabetik).
    anahtarlar = [veri.normalize(a) for a in (m or {}).get("beyan_anahtarlari", [])]
    katalog, beyan_metinleri, beyan_urunleri = [], [], []
    for u in sorted(veri.urunler(), key=lambda x: veri.normalize(x["ad"])):
        satirlar = _katalog_eslesmesi(em_id, u)
        if not satirlar:
            continue
        tek = _tek_icerikli(u, em_id)
        beyanlar = _urun_beyanlari(u, anahtarlar, tek)
        katalog.append({
            "ad": u["ad"],
            "marka": u["marka"],
            "porsiyondaki_miktar": [f"{e['etiketteki_ad']}: {_etiket_miktari(e, u)}" for e in satirlar],
            "onayli_beyanlar": beyanlar,
            "parti_analizi_var": False,
            "urun_sayfasi": u["kaynak"]["url"],
        })
        if tek and em_id != "multivitamin":
            for b in beyanlar:
                anahtar = _beyan_anahtari(b, anahtarlar)
                onceki = next((i for i, x in enumerate(beyan_metinleri) if _beyan_anahtari(x, anahtarlar) == anahtar), None)
                if onceki is None:
                    beyan_metinleri.append(b)
                elif veri.normalize(b) != anahtar and veri.normalize(beyan_metinleri[onceki]) == anahtar:
                    beyan_metinleri[onceki] = b  # Etken madde adını içeren yazım tercih edilir.
            beyan_urunleri.append(u)

    if m is None:
        durum_metni = (f"{ad} için kanıt kartı henüz hazırlanmadı ya da medikal kurul onayı bekliyor. "
                       "Aşağıda yalnızca EFSA değeri, ürün sayfalarındaki beyanlar ve katalog bilgisi var.")
    kaynak_idleri += (m or {}).get("kaynaklar", []) + (m or {}).get("uretici_icerikleri", [])
    for alan in ("besinle_karsilama", "tahlil_notu"):
        kaynak_idleri += (m or {}).get(alan, {}).get("kaynaklar", [])
    for g in (m or {}).get("kimde_kanit_var", []):
        kaynak_idleri += g["kaynaklar"]
    if not kaynak_idleri:
        kaynak_idleri = ["orzax_urunler"]
    # Bağımsız kaynaklar önce, üretici içerikleri sonra.
    kayitlar = veri.kaynak_kayitlari()
    sirali = sorted(dict.fromkeys(kaynak_idleri), key=lambda i: kayitlar[i]["tur"] == "uretici_icerigi")
    kaynak_listesi = veri.kaynaklar(sirali)
    kaynak_listesi = (
        [k for k in kaynak_listesi if k["tur"] != "uretici_icerigi"]
        + [veri.urun_kaynagi(u) for u in beyan_urunleri]
        + [k for k in kaynak_listesi if k["tur"] == "uretici_icerigi"]
    )

    return veri.zarf({
        "kisa_ozet": on_ek + (m["kisa_ozet"] if m else durum_metni),
        "zorunlu_uyarilar": zorunlu,
        **({"kanit_durumu": TASLAK_NOTU} if m and m["durum"] == "taslak" else {}),
        "kimde_kanit_var": [{"grup": g["grup"], "gerekce": g["gerekce"]} for g in (m or {}).get("kimde_kanit_var", [])],
        **({"kimde_kanit_var_notu": m["kimde_kanit_var_notu"]} if m and m.get("kimde_kanit_var_notu") else {}),
        "kanit_duzeyi": kanit,
        "kanit_duzeyi_olcegi": (
            "guclu: birden fazla yüksek kaliteli çalışmada tutarlı; orta: tutarlı ama sınırlı ya da kalite sorunlu; "
            "zayif: küçük ya da çelişkili çalışmalar; yetersiz: anlamlı insan çalışması yok. "
            "sonuc_yonu ayrıca fayda, etkisiz, zarar ya da belirsiz olabilir."
        ),
        "onayli_saglik_beyanlari": {
            "metinler": beyan_metinleri,
            "not": (
                "Yalnızca bu maddeyi içeren katalog ürünlerinin sayfalarındaki, TGK Beslenme ve Sağlık Beyanları "
                "Yönetmeliği'ne atıf yapan beyanlardır." if beyan_metinleri else
                "Katalogda yalnızca bu maddeyi içeren ürün olmadığı için etken madde düzeyinde beyan listelenmedi."
            ),
        },
        "besinle_karsilama": (m or {}).get("besinle_karsilama", {}).get("metin"),
        **({"tahlil_notu": m["tahlil_notu"]["metin"]} if m and m.get("tahlil_notu") else {}),
        "efsa_ust_sinir": efsa,
        "etkilesimler": etkilesimler,
        "etkilesim_notu": (
            None if etkilesimler else
            "Kural tablosunda bu madde için tanımlı etkileşim yok; bu, etkileşim olmadığı anlamına gelmez."
        ),
        "dikkat_edecekler": dikkat,
        "hekime_sorulacaklar": list(dict.fromkeys(sorular)),
        "katalogdaki_urunler": katalog,
        "katalog_kapsami": "Katalog şu an yalnızca Orzax ürünlerini içerir.",
        "siralama_olcutu": "Alfabetik. Sponsorlu veya öncelikli sıralama yoktur.",
        "gizlilik": "Profil bilgileri yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    }, kaynak_listesi)
