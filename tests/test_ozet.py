"""Model katmanı (mimari v2): kısa metin özeti + structuredContent; modelden gizli kart araçları (TB-26 dahil)."""

import re

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from server import araclar, ozet, veri
from server.app import TALIMATLAR, mcp


@pytest.fixture(params=["0", "1"], ids=["yayin", "deneme"])
def taslak_ayari(request, monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", request.param)


def _cagrilar():
    yield "sikayet_yolu", araclar.sikayet_yolu("yorgunum", yas=62, cinsiyet="erkek")
    yield "yasam_karnesi", araclar.yasam_karnesi()
    yield "yasam_karnesi", araclar.yasam_karnesi({"hareket_gun": 0, "uyku_saat": 5, "sebze_meyve_porsiyon": 1,
                                                  "balik_haftalik": 0, "sigara": "her_gun", "stres": "neredeyse_her_gun"}, 45)
    yield "parti_analizi", araclar.parti_analizi("L2410A17")
    yield "kisisel_rutin", araclar.kisisel_rutin(58, "kadin", evre="gebe", ilac_grubu=["kan_sulandirici_varfarin"],
                                                 mevcut_urunler=["Day2Day The Collagen Mag Plus", "Ocean D3K2 Damla", "Bilinmeyen"])
    for em_id in araclar.REHBER_KAPSAMI:
        ad = "multivitamin" if em_id == "multivitamin" else veri.etken_madde_adi(em_id)
        yield "etken_madde_rehberi", araclar.etken_madde_rehberi(ad, yas=42, cinsiyet="erkek", ilac_grubu=["metformin"])
    for u in veri.urunler():
        yield "urun_rehberi", araclar.urun_rehberi(u["ad"], yas=8)


def test_her_ozet_sinir_icinde_ve_zorunlu_parcalari_tasir(taslak_ayari):
    for arac, v in _cagrilar():
        m = ozet.metin(arac, v)
        assert len(m) <= ozet.OZET_SINIRI, (arac, v["kisa_ozet"][:60], len(m))
        assert m.startswith(v["kisa_ozet"]), arac
        assert m.rstrip().endswith(v["uyari"]), arac
        kaynak_satiri = [s for s in m.splitlines() if re.match(r"- .*https?://", s)]
        assert len(kaynak_satiri) <= ozet.EN_FAZLA_KAYNAK, arac


def test_ozet_sabit_metni_tekrar_etmez():
    # TB-26: veri notu ve geliştirici notu sunucu talimatında; yanıt metninde tekrar edilmez.
    v = araclar.etken_madde_rehberi("D vitamini")
    m = ozet.metin("etken_madde_rehberi", v)
    assert veri.VERI_NOTU not in m and veri.GELISTIRICI not in m
    assert veri.VERI_NOTU in TALIMATLAR and "Orzax tarafından geliştirilmiştir" in TALIMATLAR


def test_rehber_ozetinde_en_fazla_bes_urun(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")
    v = araclar.etken_madde_rehberi("D vitamini")
    m = ozet.metin("etken_madde_rehberi", v)
    urun_adlari = [u["ad"] for u in veri.urunler() if f"- {u['ad']}\n" in m + "\n"]
    assert 0 < len(urun_adlari) <= ozet.EN_FAZLA_URUN
    assert "Kalan ürün:" in m


def test_kirpma_ozet_kaynak_ve_uyariyi_korur():
    v = {"kisa_ozet": "Özet.", "uyari": veri.UYARI, "kaynaklar": [],
         "zorunlu_uyarilar": [{"mesaj": "x" * 1000} for _ in range(10)]}
    m = ozet.metin("etken_madde_rehberi", v)
    assert len(m) <= ozet.OZET_SINIRI
    assert m.startswith("Özet.") and m.endswith(veri.UYARI) and ozet.KIRPMA_ISARETI in m


async def test_metin_ve_structured_content_ayridir(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")
    async with create_connected_server_and_client_session(mcp) as oturum:
        s = await oturum.call_tool("etken_madde_rehberi", {"etken_madde": "D vitamini"})
    assert len(s.structuredContent["kaynaklar"]) > ozet.EN_FAZLA_KAYNAK
    assert len(s.content[0].text) < len(str(s.structuredContent))


async def test_katalog_sayfasi_modelden_gizli_ve_sayfalar(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")
    async with create_connected_server_and_client_session(mcp) as oturum:
        arac = next(t for t in (await oturum.list_tools()).tools if t.name == "katalog_sayfasi")
        assert arac.meta["ui"]["visibility"] == ["app"]
        s1 = (await oturum.call_tool("katalog_sayfasi", {"etken_madde": "D vitamini", "sayfa": 1})).structuredContent
        s2 = (await oturum.call_tool("katalog_sayfasi", {"etken_madde": "D vitamini", "sayfa": 2})).structuredContent
    assert len(s1["urunler"]) == 5 and s1["toplam_sayfa"] > 1
    assert {u["ad"] for u in s1["urunler"]}.isdisjoint({u["ad"] for u in s2["urunler"]})


def test_katalog_sayfasi_kartsiz_maddede_bos(monkeypatch):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    y = araclar.katalog_sayfasi("omega-3")
    assert y["urunler"] == [] and "gösterilmez" in y["kisa_ozet"]
