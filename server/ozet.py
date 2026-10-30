"""Model katmanı: her araç yanıtının modele giden kısa metin özeti (mimari v2).

Tam veri `structuredContent` alanında görsel karta gider; model yalnızca bu özeti okur. Özet en fazla
OZET_SINIRI karakterdir (≈ 1.500 token), en fazla 5 ürün ve 5 kaynak taşır. Sabit metinler (veri notu, geliştirici)
sunucu talimatındadır (TB-26); özette yalnızca kullanıcıya iletilmesi gereken 'uyari' cümlesi kalır.
"""

from __future__ import annotations

from typing import Callable

from mcp.types import CallToolResult, TextContent

from .veri import yuzde

# Türkçe metinde 1 token ≈ 3 karakter varsayımıyla 1.500 token sınırının altında kalır.
OZET_SINIRI = 4500
EN_FAZLA_KAYNAK = 5
EN_FAZLA_URUN = 5
KIRPMA_ISARETI = "… (devamı görsel kartta)"


def _kaynak_satirlari(v: dict) -> list[str]:
    kaynaklar = v.get("kaynaklar", [])
    satirlar = [f"- {k['baslik']} ({k['kurum_veya_dergi']}{', ' + str(k['yil']) if k.get('yil') else ''}) {k['url']}"
                for k in kaynaklar[:EN_FAZLA_KAYNAK]]
    if len(kaynaklar) > EN_FAZLA_KAYNAK:
        satirlar.append(f"- … ve {len(kaynaklar) - EN_FAZLA_KAYNAK} kaynak daha (kartta).")
    return ["Kaynaklar:", *satirlar] if satirlar else []


def cumle(*parcalar: str) -> str:
    """Cümleleri birleştirir; sonu noktalı parçadan sonra çift nokta oluşmaz (v0.3 Ek 8)."""
    temiz = [p.strip() for p in parcalar if p and p.strip()]
    return " ".join(p if p.endswith((".", "!", "?", ":")) else p + "." for p in temiz)


def _madde(baslik: str, ogeler: list[str]) -> list[str]:
    return [f"{baslik}:", *(f"- {o}" for o in ogeler)] if ogeler else []


def _urun_rehberi(v: dict) -> list[str]:
    if "urun" not in v:
        adlar = v.get("adaylar") or v.get("benzer_adli_urunler") or []
        return [*_madde("Adaylar", adlar[:10]), *([v["siralama_olcutu"]] if v.get("siralama_olcutu") else [])]
    u = v["urun"]
    satirlar = [f"Ürün: {u['ad']} ({u['marka']}) · Yaş sınırı: {u['yas_siniri']}", f"Etiketteki kullanım: {u['etiketteki_kullanim']}"]
    icerik = []
    for e in u["etken_maddeler"]:
        m = e["bu_urundeki_miktar"]
        parca = f"{e['etken_madde']}: {m['etiketteki_miktar']}"
        if m.get("beslenme_referans_degeri"):
            parca += f", BRD {m['beslenme_referans_degeri']}"
        if e.get("olcek", {}).get("oran_metni"):
            parca += f"; {e['olcek']['oran_metni']}"
        elif m.get("yetiskin_ust_siniri"):
            parca += f"; üst sınır {m['yetiskin_ust_siniri']}"
        if e.get("dogrulanamadi"):
            parca += " [DOĞRULANAMADI: hesaplara katılmadı]"
        icerik.append(parca)
    beyanlar = [b["metin"] for b in u["urun_sayfasi_beyanlari"]]
    bayraklar = [x["metin"] for x in u.get("etkilesim_bayraklari", [])]
    return [*satirlar, *_madde("İçerik", icerik), *_madde("Etkileşim bayrakları", bayraklar),
            *_madde("Ürün sayfası beyanları", beyanlar[:6]),
            *([u["beyan_aciklamasi"]] if beyanlar else []), u["etiket_uyarilari"], u["parti_analizi"]]


def _etken_madde_rehberi(v: dict) -> list[str]:
    satirlar = _madde("Zorunlu uyarılar", [u["mesaj"] for u in v.get("zorunlu_uyarilar", [])])
    if v.get("kanit_durumu"):
        satirlar.append(f"Durum: {v['kanit_durumu']}")
    kartlar = [
        f"{k['sonuc_alani']} ({k['populasyon']}): düzey {k['duzey']}, sonuç {k.get('sonuc_etiketi', k['sonuc_yonu'])}. {k['mutlak_fark']}"
        for k in v.get("kanit_duzeyi", [])
    ]
    satirlar += _madde("Kanıt kartları", kartlar)
    if v.get("formlar"):
        satirlar += _madde("Formlar", list(v["formlar"].values()))
    if v.get("tahlil_notu"):
        satirlar.append(f"Tahlil: {v['tahlil_notu']}")
    if v.get("genel_kilavuz"):
        g = v["genel_kilavuz"]
        satirlar.append(f"Genel bilgi: {g['baslik']} ({g['kurum']}, {g['dil']}) {g['url']}")
    if v.get("efsa_ust_sinir"):
        e = v["efsa_ust_sinir"]
        satirlar.append("EFSA: " + cumle(e["deger"], "" if e["not"] else e["kapsam"], e["not"]))
    satirlar += _madde("Dikkat", v.get("dikkat_edecekler", []))
    satirlar += _madde("Etkileşimler", [e["mesaj"] for e in v.get("etkilesimler", [])])
    satirlar += _madde("Hekime sorulacaklar", v.get("hekime_sorulacaklar", []))
    if v.get("katalogdaki_urunler"):
        o = v["katalog_ozeti"]
        satirlar += _madde("Katalogdaki ürünler (ilk " + str(o["gosterilen"]) + ")",
                           [u["ad"] for u in v["katalogdaki_urunler"][:EN_FAZLA_URUN]])
        satirlar.append(f"Kalan ürün: {o['kalan_urun_sayisi']}. {o['kapsam']} {o['siralama_olcutu']}")
    elif v.get("katalog_kapsami"):
        satirlar.append(v["katalog_kapsami"])
    return satirlar


def _kisisel_rutin(v: dict) -> list[str]:
    sinirlar = []
    for k in v["ust_sinir_kontrolu"]:
        durum = {True: "AŞIYOR", False: "aşmıyor", None: "bilinmiyor (eksik veri)"}[k["asiyor"]]
        sinirlar.append(f"{k['etken_madde']}: {k['takviyelerden_toplam']} / {k['efsa_degeri']} → {durum}"
                        + (f". {k['sinira_yakinlik']}" if k.get("sinira_yakinlik") else ""))
    return [
        *_madde("Tekrar eden etken maddeler", [f"{t['etken_madde']}: {', '.join(t['urunler'])}" for t in v["tekrar_eden_etken_maddeler"]]),
        *_madde("Üst sınır kontrolü", sinirlar),
        *_madde("Doğrulanamayan içerikler", v["dogrulanamayan_icerikler"]),
        *_madde("Etkileşim ve zamanlama", [f"{e['konu']}: {e['mesaj']}" for e in v["etkilesim_ve_zamanlama"]]),
        *_madde("Etiket yaş sınırı dışında", [e["urun"] for e in v["etiket_bilgileri"] if e["yas_siniri_disinda"]]),
        *_madde("Hekime sorulacaklar", v["hekime_sorulacak_sorular"]),
        *_madde("Tanınmayan ürünler", v["taninmayan_urunler"]),
        *_madde("Birden fazla eşleşen", [f"{k}: {', '.join(a)}" for k, a in v["birden_fazla_eslesen_urunler"].items()]),
    ]


def _yasam_karnesi(v: dict) -> list[str]:
    if "eksik_sorular" in v:
        sorular = [f"{s['anahtar']} — {s['soru']} Seçenekler: " + "; ".join(f"{x['etiket']} = {x['deger']}" for x in s["secenekler"])
                   for s in v["eksik_sorular"]]
        return [v["soru_yonergesi"], *_madde("Sorular", sorular)]
    return [
        *_madde("Karne", [f"{k['alan']}: {k['cevap']} → {k['seviye']}" for k in v["karne"]]),
        *_madde("Hedefler", [f"{h['alan']}: {h['hedef']} İlk adım: {h['ilk_adim']}" for h in v["hedefler"]]),
        *_madde("Güvenlik uyarıları", [u["mesaj"] for u in v["guvenlik_uyarilari"]]),
        *_madde("Kanıt bağlantıları", [f"{b['etken_madde']}: {b['mesaj']}" for b in v["takviye_baglantilari"]]),
        *([v["kopru_notu"]] if v["takviye_baglantilari"] else []),
        *_madde("Notlar", v["notlar"]),
    ]


def _parti_analizi(v: dict) -> list[str]:
    if "sonuclar" not in v:
        return [v["not"]]
    return [
        *([v["demo_notu"]] if v.get("demo") else []),
        f"Laboratuvar: {v['laboratuvar']} · Tarih: {v['analiz_tarihi']}",
        *_madde("Etiketteki ve ölçülen", [f"{r['etken_madde']}: {r['etiketteki']} → {r['olculen']} {r['birim']} (etiketin {yuzde(r['etikete_orani'])})"
                                         for r in v["sonuclar"]]),
        v["okuma_notu"],
    ]


def _karsilastir(v: dict) -> list[str]:
    if not v.get("satirlar"):
        return []
    satirlar = []
    for r in v["satirlar"][:12]:
        miktar = f"{r['porsiyondaki_miktar']} {r['birim']}" if r["porsiyondaki_miktar"] is not None else "hesaplanamadı"
        oran = f", EFSA {yuzde(r['efsa_orani'])}" if r["efsa_orani"] is not None else ""
        bayrak = f" [{'; '.join(r['uyari_bayraklari'])}]" if r["uyari_bayraklari"] else ""
        satirlar.append(f"{r['ad']}: {r['form']}, {miktar}{oran}, {'tek bileşen' if r['tek_bilesen'] else 'kombine'}, "
                        f"yaş {r['yas_siniri']}{bayrak}")
    if len(v["satirlar"]) > 12:
        satirlar.append(f"… ve {v['toplam_urun'] - 12} ürün daha (kıyas kartında).")
    return [*_madde("Ürünler (porsiyon başına)", satirlar), f"EFSA sınırı: {v['efsa_sinir_grubu']}. {v['efsa_notu']}",
            v["siralama_olcutu"]]


def _takviye_rehberi(v: dict) -> list[str]:
    maddeler = []
    for m in v["maddeler"]:
        parca = f"{m['etken_madde']} [kart: {m['kart_durumu']}]: " + (m.get("ozet") or m.get("not", ""))
        if m.get("kimde_kanit"):
            parca += f" {m['kimde_kanit']}"
        if m.get("guvenlik"):
            parca += " Güvenlik: " + " ".join(m["guvenlik"])
        if m.get("genel_bilgi"):
            parca += " Genel bilgi: NIH ODS sayfası (İngilizce, kaynaklarda)."
        maddeler.append(parca)
    sorular = [f"{s['soru']} Seçenekler: {' / '.join(s['secenekler'])}" for s in v.get("sorulacaklar", [])]
    return [*_madde("Maddeler", maddeler), *([v["besinle_karsilama"]] if v.get("besinle_karsilama") else []),
            *([v["katalog_notu"]] if v.get("katalog_notu") else []),
            *([v["soru_yonergesi"]] if v.get("soru_yonergesi") else []), *_madde("Sorulacaklar", sorular)]


def _tahlil_goster(v: dict) -> list[str]:
    if "tahlil" not in v:
        return [v["gizlilik"]]
    return [f"Yaygın birimler: {', '.join(v['yaygin_birimler'])}. {v['birim_notu']}",
            *_madde("Tahlil öncesi", v["tahlil_oncesi"]), *([v["tahlil_notu"]] if v.get("tahlil_notu") else []),
            v["yorum_notu"], v["gizlilik"]]


def _sikayet_yolu(v: dict) -> list[str]:
    if "hazir_yollar" in v:
        return []
    t = v["hekimin_isteyebilecegi_tahliller"]
    kartlar = [
        f"{k['etken_madde']}: {k['sonuc_alani']} ({k['populasyon']}) → düzey {k['duzey']}, sonuç {k['sonuc_yonu']}"
        if "sonuc_alani" in k else f"{k['etken_madde']}: {k['durum']}"
        for k in v["ilgili_kanit_kartlari"]
    ]
    return [
        *_madde("Kırmızı bayraklar", [b["mesaj"] for b in v["kirmizi_bayraklar"]]),
        *_madde("Hekimin isteyebileceği tahliller", t["liste"]), t["not"],
        *_madde("Tahlil öncesi", v["tahlil_oncesi"]),
        f"Yaşam karnesi: {v['yasam_karnesi']['oneri']}",
        *_madde("İlgili kanıt kartları (ayrıntı: etken_madde_rehberi)", kartlar),
        v["urun_notu"],
    ]


_OZETLEYICILER: dict[str, Callable[[dict], list[str]]] = {
    "urun_rehberi": _urun_rehberi,
    "etken_madde_rehberi": _etken_madde_rehberi,
    "kisisel_rutin": _kisisel_rutin,
    "yasam_karnesi": _yasam_karnesi,
    "parti_analizi": _parti_analizi,
    "sikayet_yolu": _sikayet_yolu,
    "karsilastir": _karsilastir,
    "takviye_rehberi": _takviye_rehberi,
    "tahlil_goster": _tahlil_goster,
}


def metin(arac: str, v: dict) -> str:
    """Modele giden özet. Sınırı aşarsa gövde kırpılır; özet, kaynaklar, uyarı ve köprü sorusu her zaman kalır.

    Kapı araçlarının köprü sorusu metnin son satırıdır (v0.3 Bölüm 1): structuredContent okumayan istemciler için.
    """
    bas = [v["kisa_ozet"]]
    kopru = [f"Köprü sorusu (kullanıcıya iletin): {v['kopru']['soru']}"] if v.get("kopru") else []
    son = [*_kaynak_satirlari(v), v["uyari"], *kopru]
    govde = [s for s in _OZETLEYICILER[arac](v) if s]
    sigar = lambda g: len("\n".join(bas + g + son)) <= OZET_SINIRI  # noqa: E731
    if not sigar(govde):
        n = len(govde)
        while n and not sigar(govde[:n] + [KIRPMA_ISARETI]):
            n -= 1
        govde = govde[:n] + [KIRPMA_ISARETI]
    return "\n".join(bas + govde + son)


def sonuc(arac: str, v: dict) -> CallToolResult:
    """Modele kısa metin, karta tam veri (structuredContent)."""
    return CallToolResult(content=[TextContent(type="text", text=metin(arac, v))], structuredContent=v)
