"""Karneden takviye kanıtına ve güvenlik uyarısına köprü kuralları (data/karne_kurallari.json)."""

import json
import re

import pytest

from server import veri
from server.app import mcp
from server.araclar import REHBER_KAPSAMI, SORULAR, yasam_karnesi

IYI = {"hareket_gun": 5, "uyku_saat": 8, "sebze_meyve_porsiyon": 5, "balik_haftalik": 2, "sigara": "hayir", "stres": "bazen"}


@pytest.fixture
def kartlar_var(monkeypatch):
    """Köprü yalnızca kanıt kartı sunulabilir maddeye kurulur; bu fikstür her maddenin kartı varmış gibi davranır."""
    monkeypatch.setattr(veri, "monografi", lambda em_id: {"id": em_id})


def _idler(y: dict, alan: str) -> set[str]:
    return {b["etken_madde"] for b in y[alan]}


async def test_kural_semasi():
    araclar = {t.name for t in await mcp.list_tools()}
    anahtarlar = {s["anahtar"] for s in SORULAR}
    kayitlar = veri.kaynak_kayitlari()
    for k in veri.karne_kurallari():
        assert k["tur"] in {"takviye_baglantisi", "guvenlik"}, k["id"]
        assert k["etken_madde"] in REHBER_KAPSAMI, k["id"]
        if k["kosul"]:
            assert k["kosul"]["alan"] in anahtarlar, k["id"]
            assert {"ust_sinir_kucuktur", "icinde"} & k["kosul"].keys(), k["id"]
        assert k["onerilen_sonraki_arac"] in araclar, k["id"]
        assert k["kaynaklar"], f"{k['id']}: bağlantı ve güvenlik kuralı kaynaksız olamaz"
        for kid in k["kaynaklar"]:
            assert kayitlar[kid]["dogrulandi"] is True, kid


def test_her_sey_iyiyken_baglanti_ve_uyari_yok(kartlar_var):
    y = yasam_karnesi(IYI)
    assert y["takviye_baglantilari"] == [] and y["guvenlik_uyarilari"] == []


# TB-10: AHA haftada 1–2 kez deniz ürünü önerir; haftada 1 kez yiyen köprüyü tetiklemez.
@pytest.mark.parametrize("balik,beklenen", [(0, True), (0.5, True), ("ayda_1_3", True), (1, False), ("haftada_1", False), (4, False)])
def test_balik_omega3_baglantisi(balik, beklenen, kartlar_var):
    y = yasam_karnesi({**IYI, "balik_haftalik": balik})
    assert ("Omega-3 (EPA + DHA)" in _idler(y, "takviye_baglantilari")) is beklenen
    if beklenen:
        b = next(b for b in y["takviye_baglantilari"] if b["etken_madde"] == "Omega-3 (EPA + DHA)")
        assert b["onerilen_sonraki_arac"] == "etken_madde_rehberi"


@pytest.mark.parametrize("porsiyon,beklenen", [(0, True), (2, True), (2.9, True), (3, False), (6, False)])
def test_sebze_meyve_baglantisi(porsiyon, beklenen, kartlar_var):
    y = yasam_karnesi({**IYI, "sebze_meyve_porsiyon": porsiyon})
    assert ({"Folik asit", "C vitamini"} <= _idler(y, "takviye_baglantilari")) is beklenen


@pytest.mark.parametrize("sigara,beklenen", [("hayir", False), ("ara_sira", True), ("her_gun", True)])
def test_sigara_beta_karoten_uyarisi(sigara, beklenen):
    y = yasam_karnesi({**IYI, "sigara": sigara})
    assert ("Beta-karoten" in _idler(y, "guvenlik_uyarilari")) is beklenen
    if beklenen:
        assert any("EFSA" in u["mesaj"] for u in y["guvenlik_uyarilari"])
        assert any("Tolerable Upper Intake" in k["baslik"] for k in y["kaynaklar"])


def test_kanit_karti_olmayan_maddeye_kopru_kurulmaz(monkeypatch):
    # TB-12: boş kanıt kartına köprü yok. Güvenlik uyarısı (beta-karoten) kartsız da gösterilir.
    monkeypatch.setattr(veri, "monografi", lambda em_id: None)
    y = yasam_karnesi({**IYI, "balik_haftalik": 0, "sebze_meyve_porsiyon": 1, "sigara": "her_gun"})
    assert y["takviye_baglantilari"] == []
    assert "Beta-karoten" in _idler(y, "guvenlik_uyarilari")


def test_tahlil_onerisi_karneden_cikarildi():
    # TB-11: her profilde aynı olan tahlil önerisi karneden çıkarıldı.
    assert "tahlil_onerisi" not in yasam_karnesi(IYI)


def test_baglanti_etken_madde_adi_rehberde_cozulur(kartlar_var):
    from server.araclar import _rehber_id
    y = yasam_karnesi({**IYI, "balik_haftalik": 0, "sebze_meyve_porsiyon": 1, "sigara": "her_gun"})
    for b in y["takviye_baglantilari"] + y["guvenlik_uyarilari"]:
        assert _rehber_id(b["etken_madde"]) is not None, b["etken_madde"]


def test_dil_takviye_almaya_yonlendirmez(kartlar_var):
    y = yasam_karnesi({**IYI, "balik_haftalik": 0, "sebze_meyve_porsiyon": 1, "sigara": "her_gun"})
    metin = json.dumps({k: y[k] for k in ("takviye_baglantilari", "guvenlik_uyarilari")},
                       ensure_ascii=False).casefold()
    for kalip in [r"takviye al", r"\balmal[ıi]s[ıi]n[ıi]z\b", r"\bal[ıi]n[ıi]z?\b", r"\bkullan[ıi]n[ıi]z?\b", r"başlay[ıi]n"]:
        assert not re.search(kalip, metin), kalip
    assert all("inceleyebilirsiniz" in b["mesaj"] for b in y["takviye_baglantilari"])
