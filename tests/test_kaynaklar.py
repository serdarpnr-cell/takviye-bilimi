"""Kaynak şeması ve 'her yanıtta kaynak' kuralı."""

import pytest

from server import araclar, veri

# "sistematik_derleme" meta-analiz yapmayan sistematik derlemedir; "derleme" anlatı derlemesidir ve yalnızca
# güvenlik uyarılarında dayanak olur, kanıt düzeyine katılmaz.
TURLER = {"kilavuz", "meta_analiz", "sistematik_derleme", "derleme", "rct", "duzenleyici", "uretici_icerigi"}
YANIT_ALANLARI = {"baslik", "kurum_veya_dergi", "yil", "tur", "url", "pmid"}

# Her aracın her dönüş yolu: soru, bulunamadı, belirsiz, tam sonuç.
CAGRILAR = [
    lambda: araclar.urun_rehberi("Ocean D3K2 Damla"),
    lambda: araclar.urun_rehberi("Ocean D3K2"),
    lambda: araclar.urun_rehberi("Olmayan Ürün"),
    lambda: araclar.urun_rehberi("Ocean Kreatin"),
    lambda: araclar.parti_analizi("D3K2-24A117"),
    lambda: araclar.kisisel_rutin(41, "kadin"),
    lambda: araclar.kisisel_rutin(41, "kadin", mevcut_urunler=["Ocean Magnezyum Complex", "Ocean D3K2 Damla"]),
    lambda: araclar.yasam_karnesi(),
    lambda: araclar.yasam_karnesi({"hareket_gun": 2, "uyku_saat": 7, "sebze_meyve_porsiyon": 3,
                                   "balik_haftalik": 0, "sigara": "her_gun", "stres": "sik"}),
]


def test_kaynak_kayitlari_semaya_uyar():
    for kid, k in veri.kaynak_kayitlari().items():
        assert k["tur"] in TURLER, kid
        assert k["baslik"] and k["kurum_veya_dergi"], kid
        assert k.get("doi") or k.get("pmid") or k.get("url"), kid
        if k["dogrulandi"]:
            assert k["dogrulama_tarihi"], kid
            if not (k.get("doi") or k.get("pmid")):
                assert k.get("erisim_tarihi"), f"{kid}: URL kaynağında erişim tarihi zorunlu"


def test_kurallardaki_kaynak_kimlikleri_tanimli():
    kayitlar = veri.kaynak_kayitlari()
    for kayit in veri.kurallar()["ust_sinirlar"].values():
        for k in kayit["kaynaklar"]:
            assert k in kayitlar, k


@pytest.mark.parametrize("cagri", CAGRILAR)
def test_her_yanit_kaynak_tasir(cagri):
    y = cagri()
    assert y["kaynaklar"], y["kisa_ozet"]
    for k in y["kaynaklar"]:
        assert YANIT_ALANLARI <= k.keys(), k
        assert k["tur"] in TURLER
        assert k["url"].startswith("https://")


def test_urun_karti_uretici_kaynagini_ve_efsa_belgesini_ayri_turle_verir():
    y = araclar.urun_rehberi("Ocean D3K2 Damla")
    turler = [k["tur"] for k in y["kaynaklar"]]
    assert turler[0] == "uretici_icerigi"
    assert "duzenleyici" in turler
    assert any("vitamin D" in k["baslik"] for k in y["kaynaklar"])


def test_dogrulanmamis_kaynak_yanita_girmez(monkeypatch):
    kayitlar = {k: dict(v) for k, v in veri.kaynak_kayitlari().items()}
    kayitlar["who_tutun"]["dogrulandi"] = False
    monkeypatch.setattr(veri, "kaynak_kayitlari", lambda: kayitlar)
    y = araclar.yasam_karnesi()
    assert all("Tobacco" not in k["baslik"] for k in y["kaynaklar"])


def test_kaynaksiz_yanit_uretilemez():
    with pytest.raises(ValueError):
        veri.zarf({"kisa_ozet": "x"}, [])
