"""Veri bütünlüğü ve yasaklı ifade kontrolü."""

import json
import re

from server import veri
from server.app import TALIMATLAR, mcp

YASAKLI = [
    r"tedavi eder", r"iyileştirir", r"şifa", r"mucize", r"garanti", r"kesin sonuç", r"%100",
    r"hastalığı önler", r"kanıtlanmıştır", r"en iyi", r"\bresmi\b", r"\bresmî\b", r"bir numara",
    r"doktora gerek yok", r"ilaç yerine",
]


def test_urunlerin_etken_madde_kimlikleri_tanimli():
    em = veri.kurallar()["etken_maddeler"]
    for u in veri.urunler():
        for e in u["etken_maddeler"]:
            assert e["etken_madde"] is None or e["etken_madde"] in em, (u["ad"], e)


def test_katalog_yalnizca_orzax_ve_kaynakli():
    urunler = veri.urunler()
    assert len(urunler) >= 140
    assert {u["marka"] for u in urunler} == {"Orzax"}
    assert len({veri.normalize(u["ad"]) for u in urunler}) == len(urunler), "Ürün adları ayırt edilebilir olmalı"
    for u in urunler:
        assert u["kaynak"]["url"].startswith("https://www.orzax.com.tr/"), u["ad"]
        assert u["kaynak"]["erisim_tarihi"]
        assert u["id"] in veri.urun_beyanlari(), u["ad"]


def test_katalog_fiyat_ve_parti_verisi_icermez():
    metin = (veri.VERI_DIZINI / "urunler.json").read_text(encoding="utf-8")
    assert "₺" not in metin
    assert "parti_analizleri" not in metin


def test_bilesik_adlari_elementel_mineralle_eslesmez():
    # "Magnezyum Bisglisinat" bileşik ağırlığıdır; elementel magnezyum toplamına katılmamalı.
    for u in veri.urunler():
        for e in u["etken_maddeler"]:
            if veri.normalize(e["etiketteki_ad"]) in ("magnezyum bisglisinat", "magnezyum taurat", "balik yagi"):
                assert e["etken_madde"] not in ("magnezyum", "omega3"), (u["ad"], e)


def test_ust_sinirlar_dogrulanmis_kaynaklara_bagli():
    kayitlar = veri.kaynak_kayitlari()
    for em_id, kayit in veri.kurallar()["ust_sinirlar"].items():
        assert kayit["kaynaklar"], em_id
        for k in kayit["kaynaklar"]:
            assert kayitlar[k]["dogrulandi"] is True, (em_id, k)
            assert kayitlar[k]["tur"] == "duzenleyici", (em_id, k)


def test_etkilesim_kurallarinin_ilac_gruplari_tanimli():
    gruplar = veri.kurallar()["ilac_gruplari"]
    for k in veri.kurallar()["etkilesimler"]:
        ilac = k["kosul"].get("ilac_grubu", [])
        for i in ilac if isinstance(ilac, list) else [ilac]:
            assert i in gruplar


def _metin_alanlari(deger, haric=("brd", "miktar_metni", "okuma_notlari")):
    """Etiket değerleri (BRD yüzdesi gibi) dışındaki metinleri toplar; '%100' BRD'si yasaklı ifade sayılmaz."""
    if isinstance(deger, dict):
        return [m for k, v in deger.items() if k not in haric for m in _metin_alanlari(v, haric)]
    if isinstance(deger, list):
        return [m for v in deger for m in _metin_alanlari(v, haric)]
    return [deger] if isinstance(deger, str) else []


async def test_yasakli_ifade_yok():
    araclar = await mcp.list_tools()
    metinler = [TALIMATLAR] + [t.description for t in araclar]
    for dosya in ["urunler.json", "kurallar.json", "karne_kurallari.json", "beyanlar/beyanlar.json", "beyanlar/urun_beyanlari.json"]:
        metinler += _metin_alanlari(json.loads((veri.VERI_DIZINI / dosya).read_text(encoding="utf-8")))
    hepsi = "\n".join(metinler).casefold()
    for desen in YASAKLI:
        assert not re.search(desen, hepsi), desen


async def test_arac_aciklamalari_kisa():
    for t in await mcp.list_tools():
        assert len(t.description) <= 300, t.name
