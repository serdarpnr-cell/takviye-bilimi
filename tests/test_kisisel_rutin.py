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


def test_magnezyum_ust_siniri_asimi():
    y = kisisel_rutin(
        35, "erkek",
        mevcut_urunler=["Ocean Magnezyum"],
        diger_urun_icerikleri=[{"ad": "Uyku Destek", "icerikler": [{"etken_madde": "magnezyum", "miktar": 100, "birim": "mg"}]}],
    )
    mg = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "Magnezyum")
    assert mg["takviyelerden_toplam"] == "300 mg / gün"
    assert mg["asiyor"] is True
    assert _soru_var(y, "EFSA değerinin üzerinde")


def test_cocukta_d3_siniri_yasa_gore_degisir():
    urunler = ["Ocean Balık Yağı Şurup", "Ocean Vitamin D3 1000 IU Sprey"]
    diger = [{"ad": "Damla", "icerikler": [{"etken_madde": "D3", "miktar": 25, "birim": "µg"}]}]
    cocuk = kisisel_rutin(8, "kadin", mevcut_urunler=urunler, diger_urun_icerikleri=diger)
    yetiskin = kisisel_rutin(30, "kadin", mevcut_urunler=urunler, diger_urun_icerikleri=diger)
    c = next(k for k in cocuk["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    a = next(k for k in yetiskin["ust_sinir_kontrolu"] if k["etken_madde"] == "D3 vitamini")
    assert c["takviyelerden_toplam"] == "60 µg / gün"
    assert c["efsa_degeri"].startswith("50 µg") and c["asiyor"] is True
    assert a["efsa_degeri"].startswith("100 µg") and a["asiyor"] is False


def test_omega3_toplami_epa_ve_dha_dan_hesaplanir():
    y = kisisel_rutin(40, "erkek", mevcut_urunler=["Ocean Balık Yağı"])
    o3 = next(k for k in y["ust_sinir_kontrolu"] if k["etken_madde"] == "Omega-3 (EPA + DHA)")
    assert o3["takviyelerden_toplam"] == "580 mg / gün"
    assert "güvenli alım düzeyi" in o3["efsa_degeri"]


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
        mevcut_urunler=["Ocean Folik Asit + Demir"],
        diger_urun_icerikleri=[{"ad": "Kalsiyum Tablet", "icerikler": [{"etken_madde": "Kalsiyum", "miktar": 600, "birim": "mg"}]}],
    )
    notlar = [e for e in y["etkilesim_ve_zamanlama"] if e["konu"] == "Demir + Kalsiyum"]
    assert len(notlar) == 1 and "2 saat" in notlar[0]["mesaj"]


def test_yas_siniri_ve_gebelik_sorulari():
    y = kisisel_rutin(30, "kadin", evre="gebelik_planliyor", mevcut_urunler=["Ocean Balık Yağı Şurup"])
    assert y["etiket_uyarilari"][0]["yas_siniri_disinda"] is True
    assert _soru_var(y, "yaş aralığının")
    assert _soru_var(y, "gebelik planlarken")
    assert _soru_var(y, "folik asit")


def test_ilac_grubu_sorulari():
    y = kisisel_rutin(55, "erkek", ilac_grubu=["metformin", "mide_asidi_baskilayici"])
    assert _soru_var(y, "Metformin")
    assert _soru_var(y, "mide ilacı")


def test_taninmayan_ve_belirsiz_girdiler():
    y = kisisel_rutin(
        30, "kadin",
        mevcut_urunler=["Ocean D3", "Bilinmeyen Ürün"],
        diger_urun_icerikleri=[{"ad": "X", "icerikler": [
            {"etken_madde": "ashwagandha", "miktar": 300, "birim": "mg"},
            {"etken_madde": "magnezyum", "miktar": 5, "birim": "IU"},
        ]}],
    )
    assert y["taninmayan_urunler"] == ["Bilinmeyen Ürün"]
    assert "Ocean D3" in y["birden_fazla_eslesen_urunler"]
    assert y["taninmayan_icerikler"] == ["X: ashwagandha"]
    assert y["birimi_cevrilemeyen_icerikler"] == ["X: Magnezyum"]


def test_doz_onermez_ve_urun_tavsiye_etmez():
    y = kisisel_rutin(
        41, "kadin", evre="gebelik_planliyor", ilac_grubu=["kan_sulandirici_varfarin"],
        mevcut_urunler=["Ocean Magnezyum", "Ocean D3K2 Damla"],
        diger_urun_icerikleri=[{"ad": "Multi", "icerikler": [{"etken_madde": "magnezyum", "miktar": 150, "birim": "mg"}]}],
    )
    metin = json.dumps(y, ensure_ascii=False).casefold()
    for yasak in ["almalısınız", "alın.", "azaltın", "artırın", "bunu al", "önerilen doz", "kullanmalısınız"]:
        assert yasak not in metin, yasak


def test_kisisel_veri_loglanmaz(caplog):
    caplog.set_level(logging.DEBUG)
    kisisel_rutin(47, "kadin", evre="gebe", ilac_grubu=["metotreksat"], mevcut_urunler=["Ocean Folik Asit + Demir"])
    assert "metotreksat" not in caplog.text
    assert "gebe" not in caplog.text
