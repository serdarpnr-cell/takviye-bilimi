import json

from server.araclar import urun_rehberi
from server.veri import urunler


def test_tek_urun_karti(uyari_var):
    y = urun_rehberi("Ocean D3K2 Damla")
    uyari_var(y)
    u = y["urun"]
    assert u["ad"] == "Ocean D3K2 Damla"
    assert u["marka"] == "Orzax"
    d3 = u["etken_maddeler"][0]["bu_urundeki_miktar"]
    assert d3["etiketteki_miktar"] == "25 µg (1000 IU) (her damlada)"
    assert d3["standart_birimde"] == "25 µg"
    assert d3["yetiskin_ust_siniri"] == "100 µg / gün (EFSA üst sınır)"
    assert d3["beslenme_referans_degeri"] == "%500"
    k2 = u["etken_maddeler"][1]["bu_urundeki_miktar"]
    assert k2["standart_birimde"] == "11,25 µg"
    assert u["yas_siniri"] == "11 yaş ve üzeri"
    assert "Normal kemiklerin korunmasında katkıda bulunur." in u["saglik_beyanlari"]
    assert u["urun_sayfasi"].startswith("https://www.orzax.com.tr/")
    assert "yayımlanmış parti analizi bulunmuyor" in u["parti_analizi"]


def test_beyan_kosulu_ayri_alanda():
    u = urun_rehberi("Ocean Limon Aromalı Balık Yağı 150 mL")["urun"]
    assert u["beslenme_beyanlari"] == ["Bu gıda omega 3 yağ asidi EPA ve DHA içerir."]
    assert all("alınmalıdır" not in b for b in u["saglik_beyanlari"])
    assert any("250 mg EPA ve DHA" in k for k in u["beyan_kullanim_kosullari"])


def test_turkce_karaktersiz_ve_kucuk_harfle_arama():
    assert urun_rehberi("ocean limon aromali balik yagi 150 ml")["urun"]["ad"] == "Ocean Limon Aromalı Balık Yağı 150 mL"
    assert urun_rehberi("ocean d3k2 damla")["urun"]["ad"] == "Ocean D3K2 Damla"


def test_belirsiz_sorgu_adaylari_alfabetik_dondurur(uyari_var):
    y = urun_rehberi("Ocean D3K2")
    uyari_var(y)
    assert y["adaylar"] == ["Ocean D3K2 Damla", "Ocean D3K2 Vitamin D3 1000 IU Sprey", "Ocean Gummies D3K2"]


def test_bulunamayan_urun_benzerleri_alfabetik_listeler(uyari_var):
    y = urun_rehberi("Selenyum Forte")
    uyari_var(y)
    assert y["benzer_adli_urunler"] == ["Ocean Selenyum Tablet (100 µg)", "Ocean Selenyum Tablet (200 µg)"]
    assert y["katalogdaki_urun_sayisi"] == len(urunler())
    assert "Ücretli veya öncelikli sıralama yoktur" in y["siralama_olcutu"]
    assert "yalnızca Orzax" in y["katalog_kapsami"]


def test_sitede_okunamayan_hucre_tahmin_edilmez():
    u = urun_rehberi("Day2Day The Collagen Beauty Plus Tüp")["urun"]
    yesil_cay = next(e for e in u["etken_maddeler"] if e["etken_madde"] == "Yeşil Çay Ekstresi")
    assert yesil_cay["bu_urundeki_miktar"]["etiketteki_miktar"] == "Ürün sayfasında yazmıyor"
    assert "boş" in yesil_cay["okuma_notu"]


def test_tum_urunler_kart_uretir_ve_fiyat_icermez():
    for u in urunler():
        kart = urun_rehberi(u["ad"])["urun"]
        assert kart["ad"] == u["ad"]
        assert "₺" not in json.dumps(kart, ensure_ascii=False)
