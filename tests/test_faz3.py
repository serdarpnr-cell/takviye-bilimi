"""Faz 3: ürün karşılaştırma (TB-20), demo parti kartı (TB-23), istemci tarafında tahlil görünümü."""

import json
import re

import pytest

from server import araclar, veri
from server.app import mcp
from server.arayuz import kart_html


# ---- urun_karsilastir --------------------------------------------------------

def test_karsilastirma_kullanici_sirasini_korur_ve_siralamaz():
    adlar = ["Ocean Magnezyum Complex", "Ocean ExtraMag Magnezyum Sitrat Saşe", "Ocean ExtraMag Magnezyum Bisglisinat + P5P"]
    y = araclar.urun_karsilastir(adlar)
    assert [u["ad"] for u in y["urunler"]] == adlar
    assert "Sıralama, puan ya da öneri yoktur" in y["siralama_olcutu"]
    metin = json.dumps(y, ensure_ascii=False).casefold()
    for yasak in ["en iyi", "önerilir", "tercih edin", "puan:", "kazanan"]:
        assert yasak not in metin, yasak


def test_karsilastirma_olcutleri_ve_madde_matrisi():
    y = araclar.urun_karsilastir(["Ocean D3K2 Damla", "Ocean Magnezyum Complex"], yas=8)
    d3k2 = y["urunler"][0]
    assert d3k2["sunum_bicimi"] == "damla"
    assert d3k2["tek_ya_da_kombine"].startswith("kombine")
    assert d3k2["yas_siniri_disinda"] is True
    assert d3k2["parti_analizi"] == "yayımlanmış analiz yok"
    satir = next(r for r in y["etken_madde_karsilastirmasi"] if r["etken_madde"] == "Magnezyum")
    assert satir["urunler"][0] is None and satir["urunler"][1]["etiketteki"].startswith("Magnezyum")


def test_karsilastirma_karantinadaki_satiri_isaretler():
    y = araclar.urun_karsilastir(["Day2Day The Collagen Mag Plus", "Ocean D3K2 Damla"])
    assert y["urunler"][0]["dogrulanamayan_satir"] == 4
    d3 = next(r for r in y["etken_madde_karsilastirmasi"] if r["etken_madde"] == "D3 vitamini")
    assert d3["urunler"][0]["dogrulanamadi"] is True and d3["urunler"][1]["dogrulanamadi"] is False


def test_karsilastirma_en_az_iki_urun_ister():
    y = araclar.urun_karsilastir(["Ocean D3K2 Damla", "Bilinmeyen Ürün"])
    assert "urunler" not in y and y["taninmayan_urunler"] == ["Bilinmeyen Ürün"]


# ---- parti_analizi (demo) ----------------------------------------------------

def test_demo_parti_her_yerde_demo_olarak_etiketlidir():
    # Kabul ölçütü: "Kutudaki parti no: …" → demo analiz kartı açılır.
    y = araclar.parti_analizi("DEMO-0001")
    assert y["demo"] is True and y["kisa_ozet"].startswith("DEMO:")
    assert "gerçek" in y["laboratuvar"] and "DEMO" in y["demo_notu"]
    assert [r["etikete_orani"] for r in y["sonuclar"]] == [104, 98]
    assert araclar.parti_analizi("https://ornek.example/k?parti=demo-0001")["demo"] is True


def test_demo_kayit_urunun_parti_analizi_bilgisini_degistirmez():
    assert veri.gercek_parti_analizi_var("ocean-vitamin-d3k2-damla") is False
    assert "bulunmuyor" in araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]["parti_analizi"]
    assert all(not p["demo"] or p["parti_no"].startswith("DEMO-") for p in veri.parti_analizleri())


def test_bilinmeyen_parti_bulunamadi():
    assert "bulunamadı" in araclar.parti_analizi("L2410A17")["kisa_ozet"]


# ---- tahlil_goster -----------------------------------------------------------

async def test_tahlil_aracinin_deger_parametresi_yoktur():
    # KVKK: tahlil sonucu özel nitelikli kişisel veridir; araç değer almaz.
    arac = next(t for t in await mcp.list_tools() if t.name == "tahlil_goster")
    assert set(arac.inputSchema["properties"]) == {"tahlil"}
    assert arac.inputSchema["properties"]["tahlil"]["type"] == "string"


@pytest.mark.parametrize("ad, beklenen", [("B12", "B12 vitamini"), ("ferritin", "Ferritin"), ("25 OH D", "D vitamini (25(OH)D)")])
def test_tahlil_genel_bilgi_ve_tahlil_oncesi_uyari(ad, beklenen):
    y = araclar.tahlil_goster(ad)
    assert y["tahlil"] == beklenen
    assert y["tahlil_oncesi"] and y["kaynaklar"]
    assert "sunucuya gönderilmez" in y["gizlilik"]
    # Sabit "normal" aralık ve tahmin yok.
    metin = json.dumps(y, ensure_ascii=False)
    assert not re.search(r"\d+\s*(?:–|-)\s*\d+\s*(?:pg|ng|nmol|pmol|µg)", metin)
    assert "tahmin yapmaz" in y["yorum_notu"]


def test_tahlil_karti_degeri_gondermez_ve_saklamaz():
    # Karta özgü betik (ortak köprü hariç), yorum satırları çıkarılarak taranır.
    kaynak = (veri.VERI_DIZINI.parent / "server" / "arayuz" / "tahlil.html").read_text(encoding="utf-8")
    betik = "\n".join(s for s in kaynak[kaynak.index("<script>"):].splitlines() if not s.strip().startswith("//"))
    for yasak in ["localStorage", "sessionStorage", "indexedDB", "fetch(", "XMLHttpRequest", "tools/call", "ui/message",
                  "document.cookie", "TB.istek"]:
        assert yasak not in betik, yasak


# ---- kurul paketi ------------------------------------------------------------

def test_kurul_paketi_her_taslak_icerigi_karar_alaniyla_listeler():
    import subprocess
    import sys
    kok = veri.VERI_DIZINI.parent
    subprocess.run([sys.executable, str(kok / "scripts" / "kurul_paketi.py")], check=True, capture_output=True)
    paket = (kok / "kurul" / "kurul_paketi.html").read_text(encoding="utf-8")
    kartlar = [json.loads(p.read_text(encoding="utf-8")) for p in (veri.VERI_DIZINI / "etken_maddeler").glob("*/kartlar/*.json")]
    for k in kartlar:
        assert f"Karar ({k['id']})" in paket, k["id"]
    for liste in veri._zorunlu_uyarilar().values():
        for u in liste:
            assert f"Karar ({u['id']})" in paket
    assert "Karar (DEMO-0001)" in paket and "İkinci göz" in paket
