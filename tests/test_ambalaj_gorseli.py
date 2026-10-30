"""v0.4 C6: ambalaj görseli prototipi bayrak arkasında ve varsayılan kapalı."""

from server import araclar


def test_varsayilan_kapali(monkeypatch):
    monkeypatch.delenv("TB_AMBALAJ_GORSELI", raising=False)
    assert "ambalaj_gorseli" not in araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]


def test_base64_ve_cdn(monkeypatch):
    monkeypatch.setenv("TB_AMBALAJ_GORSELI", "base64")
    g = araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]["ambalaj_gorseli"]
    assert g["src"].startswith("data:image/jpeg;base64,") and "yer tutucu" in g["not"]
    monkeypatch.setenv("TB_AMBALAJ_GORSELI", "cdn")
    g = araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]["ambalaj_gorseli"]
    assert g["src"] == "https://cdn.orzax.com.tr/ambalaj/ocean-vitamin-d3k2-damla.jpg"
    # Prototip yalnızca 3 ürün için.
    assert "ambalaj_gorseli" not in araclar.urun_rehberi("Ocean Gummies D3K2")["urun"]
