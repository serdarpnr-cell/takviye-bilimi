"""Araçların iş mantığı. Saf fonksiyonlardır: hiçbir girdi saklanmaz veya loglanmaz."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

from . import veri

# --------------------------------------------------------------------------- #
# 1. urun_rehberi
# --------------------------------------------------------------------------- #


def _urun_karti(u: dict) -> dict:
    etkenler = []
    for em in u["etken_maddeler"]:
        std = veri.standart_miktar(em["etken_madde"], em["miktar"], em["birim"])
        sinir = veri.ust_sinir(em["etken_madde"], 18)
        etkenler.append({
            "etken_madde": veri.etken_madde_adi(em["etken_madde"]),
            "kaynak_form": em["kaynak_form"],
            # "Bu üründeki miktar" bloğu: yalnızca rakam, yorum yok.
            "bu_urundeki_miktar": {
                "etiketteki_miktar": f"{_sayi(em['miktar'])} {em['birim']} / {u['gunluk_porsiyon']}",
                "standart_birimde": None if std is None else f"{_sayi(std)} {veri.kurallar()['etken_maddeler'][em['etken_madde']]['birim']}",
                "calismalarda_kullanilan_dozlar": "Kanıt kartı hazırlanıyor.",
                "yetiskin_ust_siniri": _sinir_metni(em["etken_madde"], sinir),
            },
        })
    beyan_tablosu = veri.beyanlar()
    return {
        "ad": u["ad"],
        "marka": u["marka"],
        "form": u["form"],
        "gunluk_porsiyon": u["gunluk_porsiyon"],
        "etken_maddeler": etkenler,
        "etiketteki_kullanim": u["etiketteki_kullanim"],
        "yas_siniri": _yas_metni(u["yas_siniri"]),
        "etiket_uyarilari": u["etiket_uyarilari"],
        "onayli_beyanlar": [
            {"metin": beyan_tablosu[b]["metin"], "kosul": beyan_tablosu[b]["kosul"], "durum": beyan_tablosu[b]["durum"]}
            for b in u["onayli_beyanlar"]
        ],
        "ne_beklememeli": u["ne_beklememeli"],
        "mensei": {
            "uretim_ulkesi": u["mensei"].get("uretim_ulkesi") or "Belirtilmemiş",
            "hammadde_kaynagi": u["mensei"].get("hammadde_kaynagi") or "Belirtilmemiş",
        },
        "seffaflik": veri.seffaflik(u),
        "parti_analizi_sayisi": len(u["parti_analizleri"]),
    }


def urun_rehberi(urun: str) -> dict:
    adaylar = veri.urun_ara(urun)
    if len(adaylar) == 1:
        u = adaylar[0]
        return veri.zarf({
            "kisa_ozet": f"{u['ad']} ({u['marka']}) için etiket bilgileri. Ürün düzeyindeki etki ifadeleri yalnızca onaylı beyanlardan gelir.",
            "urun": _urun_karti(u),
        })
    if len(adaylar) > 1:
        return veri.zarf({
            "kisa_ozet": f"'{urun}' birden fazla ürünle eşleşti. Hangisini kastettiğinizi belirtin.",
            "adaylar": [a["ad"] for a in adaylar],
        })
    # Eşleşme yoksa kataloğu, ölçütü yazarak listeler.
    katalog = sorted(
        veri.urunler(),
        key=lambda x: (not veri.seffaflik(x)["seffaflik_rozeti"], veri.normalize(x["ad"])),
    )
    return veri.zarf({
        "kisa_ozet": f"'{urun}' katalogda bulunamadı. Katalogdaki ürünler aşağıda.",
        "siralama_olcutu": "Önce şeffaflık rozeti olanlar, sonra alfabetik. Ücretli sıralama yoktur.",
        "katalog": [
            {"ad": x["ad"], "marka": x["marka"], "form": x["form"], "seffaflik_rozeti": veri.seffaflik(x)["seffaflik_rozeti"]}
            for x in katalog
        ],
    })


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
    aranan = veri.normalize(parti_no).replace(" ", "")
    for u in veri.urunler():
        for p in u["parti_analizleri"]:
            if veri.normalize(p["parti_no"]).replace(" ", "") == aranan:
                uygun_degil = [t["parametre"] for t in p["testler"] if t["sonuc"] != "uygun"]
                return veri.zarf({
                    "kisa_ozet": (
                        f"{u['ad']}, parti {p['parti_no']}: {len(p['testler'])} test, "
                        + ("tümü limit veya beyan içinde." if not uygun_degil else f"uygun olmayan: {', '.join(uygun_degil)}.")
                    ),
                    "urun": u["ad"],
                    "marka": u["marka"],
                    "parti": {k: v for k, v in p.items() if k != "karekod"},
                    "seffaflik": veri.seffaflik(u),
                })
    yayimlamayanlar = [u["ad"] for u in veri.urunler() if not u["parti_analizi_yayimliyor"]]
    return veri.zarf({
        "kisa_ozet": f"'{parti_no}' parti numarası için yayımlanmış analiz bulunamadı.",
        "aranan_parti_no": parti_no,
        "not": "Parti numarası kutunun alt ya da yan yüzünde, son kullanma tarihinin yanında yazar. Bazı markalar parti analizi yayımlamaz.",
        "parti_analizi_yayimlamayan_urunler": yayimlamayanlar,
    })


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
    return f"{x:,.1f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".")


def _sinir_metni(em_id: str, sinir: dict | None) -> str | None:
    if sinir:
        tur = "üst sınır" if sinir["tur"] == "ust_sinir" else "güvenli alım düzeyi"
        return f"{_sayi(sinir['deger'])} {sinir['birim']} / gün (EFSA {tur})"
    kayit = veri.kurallar()["ust_sinirlar"].get(em_id)
    return kayit["kapsam"] if kayit else None


def _yas_metni(ys: dict) -> str:
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
    kaynaklar: dict[str, list[tuple[str, float | None]]] = {}
    tanimsiz_urunler: list[str] = []
    tanimsiz_icerikler: list[str] = []
    bulunan_urunler: list[dict] = []
    belirsiz_urunler: dict[str, list[str]] = {}

    for ad in mevcut_urunler or []:
        eslesen = veri.urun_ara(ad)
        if len(eslesen) == 1:
            u = eslesen[0]
            bulunan_urunler.append(u)
            for em in u["etken_maddeler"]:
                kaynaklar.setdefault(em["etken_madde"], []).append(
                    (u["ad"], veri.standart_miktar(em["etken_madde"], em["miktar"], em["birim"]))
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
            kaynaklar.setdefault(em_id, []).append(
                (diger.ad, veri.standart_miktar(em_id, ic.miktar, ic.birim))
            )

    # Toplam etken maddeler (ör. omega-3 = EPA + DHA).
    for toplam_id, parcalar in kurallar["toplamlar"].items():
        parca_kaynaklari = [k for p in parcalar for k in kaynaklar.get(p, [])]
        if parca_kaynaklari:
            kaynaklar.setdefault(toplam_id, []).extend(parca_kaynaklari)

    # Tekrar eden etken maddeler. Toplamı olan parçalar (EPA, DHA) toplam altında sayılır.
    parca_idleri = {p for parcalar in kurallar["toplamlar"].values() for p in parcalar}
    tekrar_edenler = []
    for em_id, liste in kaynaklar.items():
        if em_id in parca_idleri:
            continue
        urun_adlari = sorted({ad for ad, _ in liste})
        if len(urun_adlari) > 1:
            tekrar_edenler.append({"etken_madde": veri.etken_madde_adi(em_id), "urunler": urun_adlari})

    # Üst sınır karşılaştırması: yalnızca rakam, yorum yok.
    ust_sinir_kontrolu = []
    birim_cevrilemeyen = []
    for em_id, liste in kaynaklar.items():
        gecerli = [(ad, m) for ad, m in liste if m is not None]
        birim_cevrilemeyen += [f"{ad}: {veri.etken_madde_adi(em_id)}" for ad, m in liste if m is None]
        if not gecerli:
            continue
        sinir = veri.ust_sinir(em_id, yas)
        if sinir is None:
            continue
        toplam = sum(m for _, m in gecerli)
        ust_sinir_kontrolu.append({
            "etken_madde": veri.etken_madde_adi(em_id),
            "takviyelerden_toplam": f"{_sayi(toplam)} {sinir['birim']} / gün",
            "efsa_degeri": _sinir_metni(em_id, sinir),
            "asiyor": toplam > sinir["deger"],
            "kapsam": sinir["kapsam"],
            "kaynak_dogrulandi": sinir["kaynak"]["dogrulandi"],
        })
    asimlar = [k for k in ust_sinir_kontrolu if k["asiyor"]]

    # Etiket uyarıları ve yaş sınırı.
    etiket_uyarilari = []
    for u in bulunan_urunler:
        ys = u["yas_siniri"]
        yas_disi = yas < ys["min"] or (ys["max"] is not None and yas > ys["max"])
        etiket_uyarilari.append({
            "urun": u["ad"],
            "uyarilar": u["etiket_uyarilari"],
            "etiketteki_kullanim": u["etiketteki_kullanim"],
            "yas_siniri": _yas_metni(ys),
            "yas_siniri_disinda": yas_disi,
        })

    # Etkileşim kuralları.
    etkilesimler = []
    sorular: list[str] = []
    for kural in kurallar["etkilesimler"]:
        kosul = kural["kosul"]
        em_listesi = _liste(kosul["etken_madde"])
        mevcut_em = [e for e in em_listesi if e in kaynaklar]
        if not mevcut_em:
            continue
        if "ilac_grubu" in kosul and not ilaclar.intersection(_liste(kosul["ilac_grubu"])):
            continue
        if "diger_etken_madde" in kosul and kosul["diger_etken_madde"] not in kaynaklar:
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
    for e in etiket_uyarilari:
        if e["yas_siniri_disinda"]:
            sorular.append(f"{e['urun']} etiketteki yaş aralığının ({e['yas_siniri']}) dışında. Bu yaşta kullanımı uygun mu?")
    if evre in ("gebe", "emziriyor", "gebelik_planliyor") and (bulunan_urunler or diger_urun_icerikleri):
        etiket_metni = {"gebe": "gebelikte", "emziriyor": "emzirme döneminde", "gebelik_planliyor": "gebelik planlarken"}[evre]
        sorular.append(f"Kullandığım takviyeler {etiket_metni} uygun mu, hangilerini sürdürmeliyim?")
    if evre == "gebelik_planliyor" and "folik_asit" not in kaynaklar:
        sorular.append("Gebelik planlıyorum; folik asit kullanımı hakkında ne önerirsiniz?")
    if cinsiyet == "erkek" and "demir" in kaynaklar:
        sorular.append("Demir içeren bir ürün kullanıyorum; demir düzeyimin ölçülmesi gerekir mi?")
    if "d3" in kaynaklar:
        sorular.append("D vitamini düzeyimin ölçülmesi gerekir mi?")

    ozet_parcalari = [
        f"{len(tekrar_edenler)} tekrar eden etken madde",
        f"{len(asimlar)} EFSA değeri aşımı",
        f"{len(etkilesimler)} etkileşim veya zamanlama notu",
    ]
    return veri.zarf({
        "kisa_ozet": "Rutin kontrolü: " + ", ".join(ozet_parcalari) + ". Bu bir değerlendirme değildir; sonuçları hekiminiz veya eczacınızla konuşun.",
        "tekrar_eden_etken_maddeler": tekrar_edenler,
        "ust_sinir_kontrolu": ust_sinir_kontrolu,
        "ust_sinir_notu": "Toplamlar yalnızca girilen takviyelerden hesaplanmıştır; besinlerden gelen miktar dahil değildir. EFSA değerleri prototipte henüz kaynaktan doğrulanmamıştır.",
        "etiket_uyarilari": etiket_uyarilari,
        "etkilesim_ve_zamanlama": etkilesimler,
        "hekime_sorulacak_sorular": list(dict.fromkeys(sorular)),
        "taninmayan_urunler": tanimsiz_urunler,
        "birden_fazla_eslesen_urunler": belirsiz_urunler,
        "taninmayan_icerikler": tanimsiz_icerikler,
        "birimi_cevrilemeyen_icerikler": sorted(set(birim_cevrilemeyen)),
        "gizlilik": "Girilen bilgiler yalnızca bu yanıtı üretmek için işlendi; saklanmadı ve loglanmadı.",
    })


def _liste(x) -> list:
    return x if isinstance(x, list) else [x]


# --------------------------------------------------------------------------- #
# 4. yasam_karnesi
# --------------------------------------------------------------------------- #

SORULAR = [
    {"anahtar": "hareket_gun", "soru": "Son bir haftada kaç gün en az 30 dakika tempolu hareket ettin? (0–7)"},
    {"anahtar": "uyku_saat", "soru": "Gece ortalama kaç saat uyuyorsun?"},
    {"anahtar": "sebze_meyve_porsiyon", "soru": "Günde kaç porsiyon sebze ve meyve yiyorsun? (1 porsiyon ≈ 1 avuç ya da 1 orta boy meyve)"},
    {"anahtar": "balik_haftalik", "soru": "Haftada kaç kez balık yiyorsun?"},
    {"anahtar": "sigara", "soru": "Sigara ya da tütün kullanıyor musun? (hayir / ara_sira / her_gun)"},
    {"anahtar": "stres", "soru": "Son iki haftada kendini ne sıklıkla gergin ya da tükenmiş hissettin? (hic / bazen / sik / neredeyse_her_gun)"},
]

ESIK_NOTU = (
    "Eşikler yetişkinler için genel halk sağlığı önerilerinden sadeleştirilmiştir "
    "(haftada en az 150 dakika hareket, 7–9 saat uyku, günde en az 5 porsiyon sebze-meyve, "
    "haftada 2 kez balık). Prototiptir; medikal kurul onayı bekler."
)

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


class KarneCevaplari(BaseModel):
    hareket_gun: int | None = Field(default=None, ge=0, le=7, description="Son bir haftada en az 30 dk tempolu hareket edilen gün sayısı")
    uyku_saat: float | None = Field(default=None, ge=0, le=24, description="Gecelik ortalama uyku süresi (saat)")
    sebze_meyve_porsiyon: float | None = Field(default=None, ge=0, le=30, description="Günlük sebze ve meyve porsiyonu")
    balik_haftalik: float | None = Field(default=None, ge=0, le=21, description="Haftada kaç kez balık")
    sigara: Literal["hayir", "ara_sira", "her_gun"] | None = None
    stres: Literal["hic", "bazen", "sik", "neredeyse_her_gun"] | None = None


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


def yasam_karnesi(cevaplar: KarneCevaplari | dict | None = None, yas: int | None = None) -> dict:
    if isinstance(cevaplar, dict) or cevaplar is None:
        cevaplar = KarneCevaplari.model_validate(cevaplar or {})
    girilen = cevaplar.model_dump(exclude_none=True)
    eksik = [s for s in SORULAR if s["anahtar"] not in girilen]

    if eksik:
        return veri.zarf({
            "kisa_ozet": f"Karne için 6 sorunun hepsi gerekli; {len(eksik)} soru cevaplanmadı. Soruları kullanıcıya sorun.",
            "eksik_sorular": eksik,
            "tum_sorular": SORULAR,
        })

    karne = []
    for s in SORULAR:
        puan = _puanla(s["anahtar"], girilen[s["anahtar"]])
        karne.append({
            "alan": _HEDEFLER[s["anahtar"]]["alan"],
            "cevap": girilen[s["anahtar"]],
            "seviye": _SEVIYE[puan],
            "puan": puan,
        })
    toplam = sum(k["puan"] for k in karne)

    gelismeli = sorted(
        (s["anahtar"] for s, k in zip(SORULAR, karne) if k["puan"] < 2),
        key=lambda a: (_puanla(a, girilen[a]), _ONCELIK.index(a)),
    )
    hedefler = [{**_HEDEFLER[a]} for a in gelismeli[:3]]

    notlar = []
    if girilen["stres"] == "neredeyse_her_gun":
        notlar.append("Neredeyse her gün gergin ya da tükenmiş hissetmek bir hekim veya ruh sağlığı uzmanıyla konuşmaya değer.")
    if yas is not None and yas < 18:
        notlar.append("Bu karnenin eşikleri yetişkinler içindir; çocuk ve gençlerde uyku ve hareket ihtiyacı farklıdır.")

    return veri.zarf({
        "kisa_ozet": f"Karne: {toplam}/12. {len(hedefler)} hedef seçildi." if hedefler else f"Karne: {toplam}/12. Altı alanın hepsi iyi düzeyde.",
        "karne": karne,
        "toplam_puan": toplam,
        "en_yuksek_puan": 12,
        "hedefler": hedefler,
        "hedef_secimi": "En düşük puanlı alanlardan en fazla 3 hedef seçilir; eşitlikte tütün, hareket, uyku, beslenme, balık, dinlenme sırası izlenir.",
        "esik_notu": ESIK_NOTU,
        "notlar": notlar,
        "gizlilik": "Cevaplar yalnızca bu karneyi üretmek için işlendi; saklanmadı ve loglanmadı.",
    })
