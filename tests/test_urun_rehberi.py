from server.araclar import urun_rehberi
from server.veri import urunler


def test_tek_urun_karti(uyari_var):
    y = urun_rehberi("Ocean D3K2 Damla")
    uyari_var(y)
    u = y["urun"]
    assert u["ad"] == "Ocean D3K2 Damla"
    d3 = u["etken_maddeler"][0]["bu_urundeki_miktar"]
    assert d3["etiketteki_miktar"] == "1.000 IU / 2 damla"
    assert d3["standart_birimde"] == "25 µg"
    assert d3["yetiskin_ust_siniri"] == "100 µg / gün (EFSA üst sınır)"
    assert u["yas_siniri"] == "12 yaş ve üzeri"
    assert any("Varfarin" in x for x in u["etiket_uyarilari"])
    assert [b["metin"] for b in u["onayli_beyanlar"]] == [
        "D vitamini, normal kemiklerin korunmasına katkıda bulunur.",
        "K vitamini, normal kemiklerin korunmasına katkıda bulunur.",
    ]
    assert u["ne_beklememeli"]
    assert u["seffaflik"]["seffaflik_rozeti"] is True


def test_turkce_karaktersiz_ve_kucuk_harfle_arama():
    assert urun_rehberi("ocean balik yagi surup")["urun"]["ad"] == "Ocean Balık Yağı Şurup"
    assert urun_rehberi("d3k2")["urun"]["ad"] == "Ocean D3K2 Damla"


def test_belirsiz_sorgu_adaylari_dondurur(uyari_var):
    y = urun_rehberi("Ocean D3")
    uyari_var(y)
    assert set(y["adaylar"]) == {"Ocean D3K2 Damla", "Ocean Vitamin D3 1000 IU Sprey"}


def test_bulunamayan_urun_katalogu_olcutuyle_listeler(uyari_var):
    y = urun_rehberi("Olmayan Ürün")
    uyari_var(y)
    assert len(y["katalog"]) == len(urunler()) == 8
    assert "Ücretli sıralama yoktur" in y["siralama_olcutu"]
    rozetler = [k["seffaflik_rozeti"] for k in y["katalog"]]
    assert rozetler == sorted(rozetler, reverse=True)


def test_rakip_urun_ayni_sablonla_ve_eksik_bilgi_acikca():
    ocean = urun_rehberi("Ocean Vitamin D3 1000 IU Sprey")["urun"]
    rakip = urun_rehberi("Marka A D3 Tablet")["urun"]
    assert ocean.keys() == rakip.keys()
    assert rakip["mensei"]["uretim_ulkesi"] == "Belirtilmemiş"
    assert rakip["seffaflik"]["parti_analizi"] == "Yayımlamıyor"
    assert rakip["seffaflik"]["seffaflik_rozeti"] is False


def test_tum_urunler_kart_uretir():
    for u in urunler():
        assert urun_rehberi(u["ad"])["urun"]["ad"] == u["ad"]
