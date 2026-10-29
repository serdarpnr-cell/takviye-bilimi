import pytest

from server.araclar import parti_analizi


@pytest.mark.parametrize(
    "girdi",
    [
        "D3K2-24A117",
        "d3k2-24a117",
        "https://takviyebilimi.example/k/D3K2-24A117",
        "https://takviyebilimi.example/k/D3K2-24A117/",
        "https://takviyebilimi.example/tara?parti=D3K2-24A117",
        "(01)08680000000017(17)260912(10)D3K2-24A117",
    ],
)
def test_karekod_ve_parti_no_bicimleri(girdi, uyari_var):
    y = parti_analizi(girdi)
    uyari_var(y)
    assert y["urun"] == "Ocean D3K2 Damla"
    assert y["parti"]["parti_no"] == "D3K2-24A117"
    assert "tümü limit veya beyan içinde" in y["kisa_ozet"]
    assert y["parti"]["testler"][0]["olculen"] == "1.080 IU/2 damla"


def test_rakip_markanin_yayimladigi_analiz_de_gelir():
    y = parti_analizi("MB-D3-2407")
    assert y["urun"] == "Marka B D3 Sprey"


def test_bulunamayan_parti(uyari_var):
    y = parti_analizi("YOK-000")
    uyari_var(y)
    assert y["aranan_parti_no"] == "YOK-000"
    assert "Marka A D3 Tablet" in y["parti_analizi_yayimlamayan_urunler"]
    assert "urun" not in y
