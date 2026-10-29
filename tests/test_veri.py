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


def test_urunlerin_etken_maddeleri_ve_beyanlari_tanimli():
    em = veri.kurallar()["etken_maddeler"]
    for u in veri.urunler():
        for e in u["etken_maddeler"]:
            assert e["etken_madde"] in em, (u["ad"], e)
            assert veri.standart_miktar(e["etken_madde"], e["miktar"], e["birim"]) is not None
        for b in u["onayli_beyanlar"]:
            assert b in veri.beyanlar(), (u["ad"], b)


def test_istenen_urunler_katalogda():
    adlar = {u["ad"] for u in veri.urunler()}
    assert adlar == {
        "Ocean Balık Yağı", "Ocean D3K2 Damla", "Ocean Vitamin D3 1000 IU Sprey", "Ocean Magnezyum",
        "Ocean Balık Yağı Şurup", "Ocean Folik Asit + Demir", "Marka A D3 Tablet", "Marka B D3 Sprey",
    }


def test_ust_sinir_kaynaklari_dogrulanmadi_olarak_isaretli():
    # Kaynaklar API/kurum belgesinden doğrulanana kadar 'dogrulandi' true olamaz.
    for kayit in veri.kurallar()["ust_sinirlar"].values():
        assert kayit["kaynak"]["dogrulandi"] is False


def test_etkilesim_kurallarinin_ilac_gruplari_tanimli():
    gruplar = veri.kurallar()["ilac_gruplari"]
    for k in veri.kurallar()["etkilesimler"]:
        ilac = k["kosul"].get("ilac_grubu", [])
        for i in ilac if isinstance(ilac, list) else [ilac]:
            assert i in gruplar


async def test_yasakli_ifade_yok():
    araclar = await mcp.list_tools()
    metinler = [TALIMATLAR] + [t.description for t in araclar]
    for dosya in ["urunler.json", "kurallar.json", "beyanlar/beyanlar.json"]:
        metinler.append((veri.VERI_DIZINI / dosya).read_text(encoding="utf-8"))
    hepsi = "\n".join(metinler).casefold()
    for desen in YASAKLI:
        assert not re.search(desen, hepsi), desen


async def test_arac_aciklamalari_kisa():
    for t in await mcp.list_tools():
        assert len(t.description) <= 300, t.name
