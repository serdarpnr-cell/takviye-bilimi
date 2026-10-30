"""TB-03: demirde zorunlu güvenlik uyarıları kanıt kartından bağımsız gösterilir."""

import sys
from pathlib import Path

import pytest

from server import araclar, veri

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lint_ifadeler import bul as yasakli_ifadeler  # noqa: E402


@pytest.fixture(params=["0", "1"], ids=["yayin", "deneme"])
def taslak_ayari(request, monkeypatch):
    """Uyarılar yayın sunucusunda da (taslak kartlar kapalıyken) görünmelidir."""
    monkeypatch.setenv("TB_TASLAK_GOSTER", request.param)


def _mesajlar(y: dict) -> list[str]:
    return [u["mesaj"] for u in y["zorunlu_uyarilar"]]


def test_demir_tahlilsiz_kullanma_uyarisi_ilk_satirda(taslak_ayari):
    # Kabul ölçütü: "Erkeğim, demir alabilir miyim?" → tahlilsiz kullanma uyarısı ilk satırda.
    y = araclar.etken_madde_rehberi("demir", cinsiyet="erkek")
    assert y["kisa_ozet"].startswith("Demir takviyesine, eksiklik kan tahliliyle doğrulanmadan başlanmamalıdır.")
    assert "doğrulanmadan başlanmamalıdır" in y["zorunlu_uyarilar"][0]["mesaj"]


def test_demir_erkek_notu_yalnizca_erkekte(taslak_ayari):
    erkek = araclar.etken_madde_rehberi("demir", cinsiyet="erkek")
    kadin = araclar.etken_madde_rehberi("demir", cinsiyet="kadin")
    belirtilmemis = araclar.etken_madde_rehberi("demir")
    assert any("Erkeklerde demir eksikliği çıkarsa" in m for m in _mesajlar(erkek))
    assert not any("Erkeklerde" in m for m in _mesajlar(kadin) + _mesajlar(belirtilmemis))
    # Tahlilsiz kullanma uyarısı herkese gösterilir.
    for y in (erkek, kadin, belirtilmemis):
        assert any("doğrulanmadan" in m for m in _mesajlar(y))


def test_uyarilar_taslak_etiketli_ve_kaynakli(taslak_ayari):
    kayitlar = veri.kaynak_kayitlari()
    for ad in ("demir",):
        y = araclar.etken_madde_rehberi(ad, cinsiyet="erkek")
        assert y["zorunlu_uyarilar"]
        urls = {k["url"] for k in y["kaynaklar"]}
        for u in y["zorunlu_uyarilar"]:
            assert u["durum"].startswith("Taslak")
            assert u["dayanak"]
        for em_id in ("demir",):
            for u in veri.zorunlu_uyarilar(em_id):
                for kid in u["kaynaklar"]:
                    assert kayitlar[kid]["dogrulandi"], kid
                    assert kayitlar[kid].get("pmid") or kayitlar[kid].get("doi"), kid
        assert any("pubmed" in x for x in urls)


def test_uyari_metinleri_yasakli_ifade_icermez():
    for liste in veri._zorunlu_uyarilar().values():
        for u in liste:
            assert not yasakli_ifadeler(u["mesaj"]), u["id"]


def test_uyarisi_olmayan_maddede_alan_bos():
    assert araclar.etken_madde_rehberi("magnezyum")["zorunlu_uyarilar"] == []
