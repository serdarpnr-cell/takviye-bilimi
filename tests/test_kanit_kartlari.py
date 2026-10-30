"""Kanıt tabanı (data/etken_maddeler/) için veri kuralları."""

import json
import re
import sys
from pathlib import Path

import pytest

from server import veri

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lint_ifadeler import bul as yasakli_ifadeler  # noqa: E402

DIZIN = veri.VERI_DIZINI / "etken_maddeler"
MONOGRAFILER = sorted(DIZIN.glob("*/monografi.json"))
KARTLAR = sorted(DIZIN.glob("*/kartlar/*.json"))
DURUMLAR = {"taslak", "kurul_incelemesinde", "onaylandi", "reddedildi"}
KOSUL_ALANLARI = {"yas_min", "yas_max", "evre", "sigara", "cinsiyet", "ilac_grubu"}
# Kart metninde serbestçe geçebilecek sayılar: "100 kişiden", "%95 güven aralığı".
SERBEST_SAYILAR = {"100", "95"}


def _yukle(yol: Path) -> dict:
    return json.loads(yol.read_text(encoding="utf-8"))


def _rakamlar(metin: str) -> set[str]:
    """'12.927', '12,927' ve '12 927' (ince boşluk) aynı sayıdır: ayırıcılar atılıp rakam dizisi karşılaştırılır.

    Ayırıcı yalnızca iki rakam arasındaysa sayıya dahildir; "1.52, 95" iki ayrı sayıdır.
    """
    return {re.sub(r"\D", "", m) for m in re.findall(r"\d+(?:[.,·  ]\d+)*", metin)}


def _kelime_sayisi(metin: str) -> int:
    return len(metin.split())


def test_kanit_tabani_bos_degil():
    assert MONOGRAFILER and KARTLAR


@pytest.mark.parametrize("yol", KARTLAR, ids=lambda p: p.stem)
def test_kart_semasi(yol):
    k = _yukle(yol)
    assert k["etken_madde"] == yol.parent.parent.name
    assert k["kanit_duzeyi"] in {"guclu", "orta", "zayif", "yetersiz"}
    assert k["sonuc_yonu"] in {"fayda", "etkisiz", "zarar", "belirsiz"}
    assert k["durum"] in DURUMLAR
    if k["durum"] == "onaylandi":
        assert k["onaylayan"] and k["onay_tarihi"]
    for alan in ("soru", "populasyon", "gerekce", "halk_ozeti", "ne_bilmiyoruz", "calisilan_dozlar", "son_arama_tarihi"):
        assert k[alan], alan
    assert k["mutlak_fark"]["metin"] and k["mutlak_fark"]["hesap"]
    assert _kelime_sayisi(k["halk_ozeti"]) <= 60


def _katman_1(kayit: dict) -> bool:
    """Kanıt protokolü Katman 1: otoriter kurum kılavuzu, düzenleyici belge ya da Cochrane sistematik derlemesi."""
    return kayit["tur"] in ("kilavuz", "duzenleyici") or kayit["kurum_veya_dergi"] == "Cochrane Database Syst Rev"


@pytest.mark.parametrize("yol", KARTLAR, ids=lambda p: p.stem)
def test_kartta_en_az_iki_kaynak_biri_katman_1(yol):
    k = _yukle(yol)
    kayitlar = veri.kaynak_kayitlari()
    assert len(set(k["kaynaklar"])) >= 2
    for kid in k["kaynaklar"]:
        assert kayitlar[kid]["dogrulandi"] is True, kid
    assert any(_katman_1(kayitlar[kid]) for kid in k["kaynaklar"])


@pytest.mark.parametrize("yol", KARTLAR, ids=lambda p: p.stem)
def test_karttaki_sayilar_kaynak_alintisinda_gecer(yol):
    k = _yukle(yol)
    kayitlar = veri.kaynak_kayitlari()
    izinli = set(SERBEST_SAYILAR) | _rakamlar(k["mutlak_fark"]["hesap"])
    for kid in k["kaynaklar"]:
        izinli.add(str(kayitlar[kid]["yil"]))
        for alinti in kayitlar[kid].get("alintilar", []):
            izinli |= _rakamlar(alinti)
    for alan in ("populasyon", "gerekce", "halk_ozeti", "ne_bilmiyoruz", "calisilan_dozlar"):
        eksik = _rakamlar(k[alan]) - izinli
        assert not eksik, f"{alan}: {eksik} kaynak alıntısında yok"
    eksik = _rakamlar(k["mutlak_fark"]["metin"]) - izinli
    assert not eksik, f"mutlak_fark: {eksik}"


@pytest.mark.parametrize("yol", MONOGRAFILER, ids=lambda p: p.parent.name)
def test_monografi_semasi_ve_kaynaklari(yol):
    m = _yukle(yol)
    kayitlar = veri.kaynak_kayitlari()
    assert m["id"] == yol.parent.name
    assert m["id"] in veri.kurallar()["etken_maddeler"]
    assert m["durum"] in DURUMLAR
    assert _kelime_sayisi(m["kisa_ozet"]) <= 60
    kimlikler = list(m["kaynaklar"]) + list(m["uretici_icerikleri"])
    kimlikler += [i for g in m["kimde_kanit_var"] for i in g["kaynaklar"]]
    kimlikler += [i for r in m["dikkat_kurallari"] for i in r["kaynaklar"]]
    for alan in ("besinle_karsilama", "tahlil_notu", "formlar"):
        kimlikler += m.get(alan, {}).get("kaynaklar", [])
    for kid in kimlikler:
        assert kayitlar[kid]["dogrulandi"] is True, kid
    for kid in m["uretici_icerikleri"]:
        assert kayitlar[kid]["tur"] == "uretici_icerigi"
    for r in m["dikkat_kurallari"] + [g for g in m["kimde_kanit_var"] if "kosul" in g]:
        assert set(r["kosul"]) <= KOSUL_ALANLARI, r["kosul"]


@pytest.mark.parametrize("yol", MONOGRAFILER + KARTLAR, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_yasakli_ifade_yok(yol):
    assert yasakli_ifadeler(yol.read_text(encoding="utf-8")) == []


def test_arama_kaydi_her_etken_madde_icin_var():
    for yol in MONOGRAFILER:
        assert (yol.parent / "arama_kaydi.md").exists(), yol.parent.name


def test_sunucu_yalnizca_onayli_kayitlari_sunar(monkeypatch):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    for yol in MONOGRAFILER:
        m = _yukle(yol)
        sunulan = veri.monografi(m["id"])
        if m["durum"] != "onaylandi":
            assert sunulan is None
        else:
            assert all(k["durum"] == "onaylandi" for k in sunulan["kartlar"])


def test_taslak_bayragi_acikken_taslaklar_sunulur(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")
    assert veri.monografi("d3")["kartlar"]
