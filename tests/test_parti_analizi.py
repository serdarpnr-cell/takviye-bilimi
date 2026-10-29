import pytest

from server.araclar import parti_analizi


@pytest.mark.parametrize(
    "girdi",
    [
        "D3K2-24A117",
        "https://ornek.example/k/D3K2-24A117",
        "https://ornek.example/k/D3K2-24A117/",
        "https://ornek.example/tara?parti=D3K2-24A117",
        "(01)08680000000017(17)260912(10)D3K2-24A117",
    ],
)
def test_karekod_ve_parti_no_bicimleri_cozulur(girdi, uyari_var):
    y = parti_analizi(girdi)
    uyari_var(y)
    assert y["aranan_parti_no"] == "D3K2-24A117"


def test_yayimlanmis_analiz_yoksa_uydurma_sonuc_donmez():
    y = parti_analizi("D3K2-24A117")
    assert "yayımlanmış analiz bulunamadı" in y["kisa_ozet"]
    assert "parti" not in y and "urun" not in y
