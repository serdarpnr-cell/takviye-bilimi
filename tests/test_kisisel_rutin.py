import json
import logging

from server.araclar import kisisel_rutin


def _soru_var(y, parca):
    return any(parca in s for s in y["hekime_sorulacak_sorular"])


def test_bos_rutin(uyari_var):
    y = kisisel_rutin(41, "kadin")
    uyari_var(y)
    assert y["tekrar_eden_etken_maddeler"] == []
    assert y["ust_sinir_kontrolu"] == []
    assert y["etkilesim_ve_zamanlama"] == []


def test_tekrar_eden_d3_ve_sinirda_toplam():
    y = kisisel_rutin(
        41, "kadin",
        mevcut_urunler=["Ocean D3K2 Damla", "Ocean Vitamin D3 1000 IU Sprey"],
        diger_urun_icerikleri=[{"ad": "Multivitamin", "icerikler": [{"etken_madde": "D vitamini", "miktar": 2000, "birim": "IU"}]}],
    )
    d3 = next(t for t in y["tekrar_eden_etken_maddeler"] if t["etken_madde"] == "D3 vitamini")
    assert d3["urunler"] == ["Multivitamin", "Ocean D3K2 Damla", "Ocean Vitamin D3 1000 IU Sprey"]
    kontrol = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert kontrol["takviyelerden_toplam"] == "100 µg / gün"
    assert kontrol["asiyor"] is False  # sınıra eşit, aşmıyor


def test_etiketteki_en_yuksek_gunluk_kullanim_esas_alinir():
    # Ocean Magnezyum Complex: tablet başına 125 mg, etikette "1 veya 2 tablet".
    y = kisisel_rutin(35, "erkek", mevcut_urunler=["Ocean Magnezyum Complex"])
    mg = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "Magnezyum")
    assert mg["takviyelerden_toplam"] == "250 mg / gün"
    assert mg["asiyor"] is False
    assert y["gunluk_miktari_hesaplanamayan_urunler"] == []


def test_magnezyum_ust_siniri_asimi():
    y = kisisel_rutin(
        35, "erkek",
        mevcut_urunler=["Ocean Magnezyum Complex"],
        diger_urun_icerikleri=[{"ad": "Uyku Destek", "icerikler": [{"etken_madde": "magnezyum", "miktar": 100, "birim": "mg"}]}],
    )
    mg = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "Magnezyum")
    assert mg["takviyelerden_toplam"] == "350 mg / gün"
    assert mg["asiyor"] is True
    assert _soru_var(y, "EFSA değerinin üzerinde")


def test_gunluk_miktari_hesaplanamayan_urun_belirtilir():
    # Ürün sayfasında porsiyon "Her Kapsülde", kullanım "1 veya 2 tablet" yazıyor; çarpan hesaplanmaz.
    y = kisisel_rutin(35, "kadin", mevcut_urunler=["Ocean DHA"])
    assert y["gunluk_miktari_hesaplanamayan_urunler"] == ["Ocean DHA"]


def test_cocukta_d3_siniri_yasa_gore_degisir():
    urunler = ["Ocean Vitamin D3 1000 IU Damla"]
    diger = [{"ad": "Damla", "icerikler": [{"etken_madde": "D3", "miktar": 30, "birim": "µg"}]}]
    cocuk = kisisel_rutin(8, "kadin", mevcut_urunler=urunler, diger_urun_icerikleri=diger)
    yetiskin = kisisel_rutin(30, "kadin", mevcut_urunler=urunler, diger_urun_icerikleri=diger)
    c = next(k for k in cocuk["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    a = next(k for k in yetiskin["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert c["takviyelerden_toplam"] == "55 µg / gün"
    assert c["efsa_degeri"].startswith("50 µg") and c["asiyor"] is True
    assert a["efsa_degeri"].startswith("100 µg") and a["asiyor"] is False


def test_omega3_toplami_yalnizca_epa_ve_dha_dan_hesaplanir():
    # Balık yağı (4506 mg) ve toplam omega-3 (1480 mg) satırları EPA + DHA toplamına katılmaz.
    y = kisisel_rutin(40, "erkek", mevcut_urunler=["Ocean Limon Aromalı Balık Yağı 150 mL"])
    o3 = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "Omega-3 (EPA + DHA)")
    assert o3["takviyelerden_toplam"] == "1.210 mg / gün"
    assert "güvenli alım düzeyi" in o3["efsa_degeri"]


def test_kurali_olmayan_icerikler_listelenir():
    y = kisisel_rutin(40, "erkek", mevcut_urunler=["Ocean Kreatin"])
    assert y["kural_tanimli_olmayan_icerikler"] == ["Ocean Kreatin: Kreatin Monohidrat (CreHytine™)"]


def test_k_vitamini_ve_kan_sulandirici():
    y = kisisel_rutin(60, "erkek", ilac_grubu=["kan_sulandirici_varfarin"], mevcut_urunler=["Ocean D3K2 Damla"])
    e = y["etkilesim_ve_zamanlama"]
    assert len(e) == 1 and e[0]["seviye"] == "hekime_danis"
    assert "hekiminize danışın" in e[0]["mesaj"]
    assert _soru_var(y, "INR")


def test_kan_sulandirici_yoksa_etkilesim_notu_yok():
    y = kisisel_rutin(60, "erkek", ilac_grubu=["yok"], mevcut_urunler=["Ocean D3K2 Damla"])
    assert y["etkilesim_ve_zamanlama"] == []


def test_demir_ve_kalsiyum_arasinda_2_saat():
    y = kisisel_rutin(
        30, "kadin",
        mevcut_urunler=["Ocean Microfer Kapsül"],
        diger_urun_icerikleri=[{"ad": "Kalsiyum Tablet", "icerikler": [{"etken_madde": "Kalsiyum", "miktar": 600, "birim": "mg"}]}],
    )
    notlar = [e for e in y["etkilesim_ve_zamanlama"] if e["konu"] == "Demir + Kalsiyum"]
    assert len(notlar) == 1 and "2 saat" in notlar[0]["mesaj"]


def test_yas_siniri_ve_gebelik_sorulari():
    y = kisisel_rutin(30, "kadin", evre="gebelik_planliyor", mevcut_urunler=["Ocean Limon Aromalı Balık Yağı 150 mL"])
    assert y["etiket_bilgileri"][0]["yas_siniri_disinda"] is False
    assert _soru_var(y, "gebelik planlarken")
    assert _soru_var(y, "folik asit")
    cocuk = kisisel_rutin(8, "kadin", mevcut_urunler=["Ocean D3K2 Damla"])
    assert cocuk["etiket_bilgileri"][0]["yas_siniri_disinda"] is True
    assert _soru_var(cocuk, "yaş aralığının")


def test_ilac_grubu_sorulari():
    y = kisisel_rutin(55, "erkek", ilac_grubu=["metformin", "mide_asidi_baskilayici"])
    assert _soru_var(y, "Metformin")
    assert _soru_var(y, "mide ilacı")


def test_taninmayan_ve_belirsiz_girdiler():
    y = kisisel_rutin(
        30, "kadin",
        mevcut_urunler=["Ocean D3K2", "Bilinmeyen Ürün"],
        diger_urun_icerikleri=[{"ad": "X", "icerikler": [
            {"etken_madde": "ashwagandha", "miktar": 300, "birim": "mg"},
            {"etken_madde": "magnezyum", "miktar": 5, "birim": "IU"},
        ]}],
    )
    assert y["taninmayan_urunler"] == ["Bilinmeyen Ürün"]
    assert "Ocean D3K2" in y["birden_fazla_eslesen_urunler"]
    assert y["taninmayan_icerikler"] == ["X: ashwagandha"]
    assert y["dogrulanamayan_icerikler"] == ["X: Magnezyum"]


def test_doz_onermez_ve_urun_tavsiye_etmez():
    y = kisisel_rutin(
        41, "kadin", evre="gebelik_planliyor", ilac_grubu=["kan_sulandirici_varfarin"],
        mevcut_urunler=["Ocean Magnezyum Complex", "Ocean D3K2 Damla"],
        diger_urun_icerikleri=[{"ad": "Multi", "icerikler": [{"etken_madde": "magnezyum", "miktar": 150, "birim": "mg"}]}],
    )
    metin = json.dumps(y, ensure_ascii=False).casefold()
    for yasak in ["almalısınız", "alın.", "azaltın", "artırın", "bunu al", "önerilen doz", "kullanmalısınız"]:
        assert yasak not in metin, yasak


def test_kisisel_veri_loglanmaz(caplog):
    caplog.set_level(logging.DEBUG)
    kisisel_rutin(47, "kadin", evre="gebe", ilac_grubu=["metotreksat"], mevcut_urunler=["Ocean Methyl Folat Tablet"])
    assert "metotreksat" not in caplog.text
    assert "gebe" not in caplog.text


def test_sitedeki_hatali_birim_toplamlara_katilmaz_ama_ozette_gorunur():
    # TB-01: Ürün sayfası D3 vitaminini "25 mg", selenyumu "55 mg" yazıyor. Değer tahmin edilmez, toplamlara
    # katılmaz; ama madde üst sınır tablosundan sessizce düşmez ve özet "0 aşım" deyip geçmez.
    y = kisisel_rutin(40, "kadin", mevcut_urunler=["Day2Day The Collagen Mag Plus"])
    d3 = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert d3["kontrol"] == "eksik"
    assert d3["asiyor"] is None
    assert d3["takviyelerden_toplam"] == "Hesaplanamadı"
    assert d3["dogrulanamayan_urunler"] == ["Day2Day The Collagen Mag Plus"]
    assert "Day2Day The Collagen Mag Plus: D3 vitamini" in y["dogrulanamayan_icerikler"]
    assert "Day2Day The Collagen Mag Plus: Selenyum" in y["dogrulanamayan_icerikler"]
    assert "4 içerik doğrulanamadı" in y["kisa_ozet"]
    assert "üst sınır kontrolü eksik" in y["kisa_ozet"] and "D3 vitamini" in y["kisa_ozet"]


def test_dogrulanan_kisim_siniri_asiyorsa_asim_kesindir():
    # Doğrulanamayan içerik varken bile doğrulanan toplam sınırı geçiyorsa aşım "bilinmiyor" değil, kesindir.
    y = kisisel_rutin(40, "kadin", mevcut_urunler=["Day2Day The Collagen Mag Plus"], diger_urun_icerikleri=[
        {"ad": "Yüksek D", "icerikler": [{"etken_madde": "D vitamini", "miktar": 150, "birim": "µg"}]}])
    d3 = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert d3["asiyor"] is True and d3["kontrol"] == "eksik"
    assert "yalnızca doğrulanan" in d3["takviyelerden_toplam"]


def test_collagen_mag_plus_ve_d3k2_birlikte():
    # Kabul ölçütü: "Collagen Mag Plus ile D3K2 damlayı birlikte kullanır mıyım?" → doğrulanamayan içerik özette.
    y = kisisel_rutin(40, "kadin", mevcut_urunler=["Day2Day The Collagen Mag Plus", "Ocean D3K2 Damla"])
    assert "doğrulanamadı" in y["kisa_ozet"]
    d3 = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert d3["kontrol"] == "eksik" and d3["asiyor"] is None
    assert "yalnızca doğrulanan" in d3["takviyelerden_toplam"]


def test_tum_icerikler_dogrulandiysa_ozet_temizdir():
    y = kisisel_rutin(40, "kadin", mevcut_urunler=["Ocean D3K2 Damla"])
    assert "doğrulanamadı" not in y["kisa_ozet"]
    assert y["dogrulanamayan_icerikler"] == []
    assert all(k["kontrol"] == "tam" for k in y["ust_sinir_kontrolu"])
