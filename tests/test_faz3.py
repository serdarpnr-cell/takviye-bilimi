"""Faz 3: ürün karşılaştırma (TB-20), demo parti kartı (TB-23), istemci tarafında tahlil görünümü."""

import json
import re

import pytest

from server import araclar, veri
from server.app import mcp
from server.arayuz import kart_html


# ---- karsilastir (v0.3 Bölüm 5) ---------------------------------------------

@pytest.fixture
def taslak(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")


def test_kiyas_tum_urunler_ve_siralama(taslak):
    y = araclar.karsilastir("D vitamini")
    eslesen = [u for u in veri.urunler() if any(e["etken_madde"] == "d3" for e in u["etken_maddeler"])]
    assert y["toplam_urun"] == len(eslesen) > 5  # 5 ürün sınırı yok
    tek = [r["tek_bilesen"] for r in y["satirlar"]]
    assert tek == sorted(tek, reverse=True)  # önce yalnızca bu maddeyi içerenler
    tekler = [r["porsiyondaki_miktar"] for r in y["satirlar"] if r["tek_bilesen"]]
    assert tekler == sorted(tekler)  # sonra miktar (artan)
    assert "Sıra öneri değildir" in y["siralama_olcutu"]
    metin = json.dumps(y, ensure_ascii=False).casefold()
    for yasak in ["en iyi", "önerilir", "tercih edin", "kazanan"]:
        assert yasak not in metin, yasak


def test_kiyas_yas_grubu_siniri_ve_varfarin(taslak):
    y = araclar.karsilastir("D vitamini", yas=8, ilac_grubu=["kan_sulandirici_varfarin"])
    sprey = next(r for r in y["satirlar"] if r["ad"] == "Ocean Vitamin D3 400 IU Sprey")
    assert sprey["efsa_sinir_degeri"] == 50 and sprey["efsa_orani"] == 20 and sprey["form"] == "sprey"
    d3k2 = next(r for r in y["satirlar"] if r["ad"] == "Ocean D3K2 Damla")
    assert "K vitamini — varfarin: hekime danışın" in d3k2["uyari_bayraklari"] and d3k2["kirmizi_bayrak"] is True
    assert d3k2["yas_siniri_disinda"] is True


def test_kiyas_form_ve_tek_bilesen_suzgeci(taslak):
    y = araclar.karsilastir("D vitamini", form="sprey", sadece_tek_bilesen=True)
    assert y["satirlar"] and all(r["form"] == "sprey" and r["tek_bilesen"] for r in y["satirlar"])


def test_kiyas_katalog_disi_marka_aday_listelemez():
    y = araclar.karsilastir("D vitamini", marka="Solgar")
    assert y["satirlar"] == [] and "yalnızca Orzax ürünlerini" in y["kisa_ozet"] and "kisisel_rutin" in y["kisa_ozet"]


def test_kiyas_karti_olmayan_maddede_urun_listelemez():
    # Tek gösterim kuralı (v0.3 Ek 4).
    y = araclar.karsilastir("C vitamini")
    assert y["satirlar"] == [] and y["katalogdaki_urun_sayisi"] > 0


def test_kiyas_karti_dis_kaynak_yuklemez():
    html = kart_html("kiyas")
    assert not re.search(r"""(src|href)\s*=\s*["']https?://""", html)
    assert "@media (max-width: 480px)" in html and "ui/open-link" in html


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
