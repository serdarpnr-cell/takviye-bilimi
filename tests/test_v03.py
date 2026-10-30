"""v0.3 iş paketi: kapı + derinlik mimarisi, takviye_rehberi, köprü, ek hatalar (Ek 1–12) ve sayaçlar."""

import json
import sys
from pathlib import Path

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from server import araclar, ozet, sayac, veri
from server.app import ACIKLAMALAR, TALIMATLAR, mcp

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))
from orzax_katalog import _yas  # noqa: E402

KAPI = {"takviye_rehberi", "sikayet_yolu", "parti_analizi"}
KARTLI = {"etken_madde_rehberi", "urun_rehberi", "karsilastir", "kisisel_rutin", "yasam_karnesi"}


@pytest.fixture
def taslak(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")


# ---- Bölüm 1–3, 6 ---------------------------------------------------------------

async def test_kapi_ve_derinlik_kart_eslemesi():
    araclar_ = {t.name: t for t in await mcp.list_tools()}
    for ad in KARTLI:
        assert araclar_[ad].meta["ui"]["resourceUri"].startswith("ui://"), ad
    # takviye_rehberi ve sikayet_yolu kartsız; parti_analizi'nin kartı v0.4 B2 gereği raporlandı, değiştirilmedi.
    for ad in ("takviye_rehberi", "sikayet_yolu"):
        assert not (araclar_[ad].meta or {}).get("ui"), ad
    assert araclar_["karsilastir"].meta["ui"]["resourceUri"] == "ui://takviye-bilimi/kiyas"


async def test_aciklamalar_birebir_ve_basliklar_turkce():
    basliklar = {"takviye_rehberi": "Takviye Rehberi", "etken_madde_rehberi": "Kanıt Kartı", "urun_rehberi": "Ürün Etiketi",
                 "karsilastir": "Ürün Kıyası", "kisisel_rutin": "Rutin Kontrolü", "yasam_karnesi": "Yaşam Karnesi",
                 "sikayet_yolu": "Şikâyet Yolu", "parti_analizi": "Parti Analizi"}
    for t in await mcp.list_tools():
        if t.name in ACIKLAMALAR:
            assert t.description == ACIKLAMALAR[t.name]
            assert "Örnek kullanıcı cümleleri" in t.description
            assert t.annotations.title == basliklar[t.name]


def test_yonerge_yonlendirme_listesi():
    for arac in ["sikayet_yolu", "takviye_rehberi", "etken_madde_rehberi", "urun_rehberi", "karsilastir",
                 "kisisel_rutin", "yasam_karnesi", "parti_analizi"]:
        assert f"→ {arac}" in TALIMATLAR or f"→ önce {arac}" in TALIMATLAR or arac in TALIMATLAR, arac
    assert "Doz önerme" in TALIMATLAR and "köprü sorusunu" in TALIMATLAR


async def test_initialize_yonerge_ve_surum():
    async with create_connected_server_and_client_session(mcp) as oturum:
        sonuc = await oturum.initialize()
    assert sonuc.instructions == TALIMATLAR
    assert sonuc.serverInfo.version == "0.3.0"


# ---- Köprü ----------------------------------------------------------------------

def test_kapi_sonuclari_kopruyle_biter(taslak):
    for arac, v in [("takviye_rehberi", araclar.takviye_rehberi("Kış geldi, hangi vitaminler?")),
                    ("sikayet_yolu", araclar.sikayet_yolu("hep yorgunum")),
                    ("parti_analizi", araclar.parti_analizi("XYZ-1"))]:
        assert v["kopru"]["soru"] and v["kopru"]["evet_ise"], arac
        assert ozet.metin(arac, v).rstrip().endswith(v["kopru"]["soru"]), arac


def test_kis_sorusu_kopru_kanit_kartina(taslak):
    v = araclar.takviye_rehberi("Kış geldi, hangi vitaminleri almam gerek?")
    assert v["hedef"] == "kis_bagisiklik"
    assert [m["etken_madde"] for m in v["maddeler"]] == ["D vitamini", "C vitamini", "Çinko"]
    assert v["kopru"]["evet_ise"] == [{"arac": "etken_madde_rehberi", "parametreler": {"etken_madde": "D vitamini"}}]
    c = next(m for m in v["maddeler"] if m["etken_madde"] == "C vitamini")
    assert c["kart_durumu"] == "hazirlaniyor" and c["genel_bilgi"].startswith("https://ods.od.nih.gov/")
    assert "katalogdaki_urun_sayisi" not in c  # tek gösterim kuralı


def test_tek_madde_sorusu(taslak):
    v = araclar.takviye_rehberi("D vitamini işe yarıyor mu?")
    assert v["hedef"] is None and len(v["maddeler"]) == 1 and v["maddeler"][0]["kart_durumu"] == "taslak"
    assert "100 kişiden" in v["maddeler"][0]["ozet"]
    assert v["kopru"]["evet_ise"][0]["arac"] == "etken_madde_rehberi"


def test_gebelik_hedefinde_gebelik_sorusu_sorulmaz(taslak):
    v = araclar.takviye_rehberi("Hamilelik planlıyoruz, hangi takviyeler önemli?")
    assert v["hedef"] == "gebelik"
    assert "evre" not in {s["alan"] for s in v["sorulacaklar"]}
    assert {"yas_araligi", "ilac_grubu"} <= {s["alan"] for s in v["sorulacaklar"]}


def test_profil_verilince_soru_yok_ve_guvenlik_bayragi(taslak):
    v = araclar.takviye_rehberi("kemik sağlığı", hedef="kemik_kas", yas=70, cinsiyet="kadin", evre="yok",
                                ilac_grubu=["kan_sulandirici_varfarin"])
    assert v["sorulacaklar"] == []
    k2 = next(m for m in v["maddeler"] if m["etken_madde"].startswith("K2"))
    assert any("varfarin" in g for g in k2["guvenlik"])


def test_takviye_rehberi_urun_listelemez(taslak):
    metin = json.dumps(araclar.takviye_rehberi("Kış geldi"), ensure_ascii=False)
    assert not any(u["ad"] in metin for u in veri.urunler())


def test_eslem_taslakken_yayinda_sunulmaz(monkeypatch):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    v = araclar.takviye_rehberi("Kış geldi")
    assert v["maddeler"] == [] and "kurul onayı" in v["kisa_ozet"]


# ---- Ek hatalar -----------------------------------------------------------------

def test_ek1_yas_alani_etiket_metniyle_tutarli():
    for u in veri.urunler():
        assert u["yas_siniri"] == _yas(u["etiketteki_kullanim"] or ""), u["ad"]
    sprey = veri.urun_ara("Ocean Vitamin D3 400 IU Sprey")[0]
    assert sprey["yas_siniri"] == {"min": 2, "max": None}


def test_ek2_k_vitamini_iceren_tum_urunlerde_varfarin_bayragi():
    for u in veri.urunler():
        if any(e["etken_madde"] == "k2" for e in u["etken_maddeler"]):
            kart = araclar.urun_rehberi(u["ad"])
            if "urun" in kart:
                assert any("varfarin" in b["metin"] for b in kart["urun"]["etkilesim_bayraklari"]), u["ad"]


def test_ek3_tek_icerikliler_once_dim_ultra_degil(taslak):
    v = araclar.etken_madde_rehberi("D vitamini")
    assert v["katalogdaki_urunler"][0]["ad"] != "Ocean Dim Ultra"
    assert all(u["tek_icerikli"] for u in v["katalogdaki_urunler"])


def test_ek4_tek_gosterim_kurali(taslak):
    for em in ["c_vitamini", "cinko"]:
        assert veri.kart_durumu(em) == "hazirlaniyor"
        assert "katalogdaki_urunler" not in araclar.etken_madde_rehberi(veri.etken_madde_adi(em))
    assert veri.kart_durumu("d3") == "taslak" and araclar.etken_madde_rehberi("D vitamini")["katalogdaki_urunler"]


def test_ek5_bulunamadi_kapsam_ve_ayni_madde():
    v = araclar.urun_rehberi("Solgar Vitamin D3 1000 IU")
    assert "yalnızca Orzax ürünlerini" in v["kisa_ozet"]
    for ad in v["benzer_adli_urunler"]:
        u = veri.urun_ara(ad)[0]
        assert any(e["etken_madde"] == "d3" for e in u["etken_maddeler"]), ad


async def test_ek6_uyku_enum_kodlari():
    arac = next(t for t in await mcp.list_tools() if t.name == "yasam_karnesi")
    sema = json.dumps(arac.inputSchema)
    for kod in ["6_saatten_az", "6_7_saat", "7_9_saat", "9_saatten_fazla"]:
        assert kod in sema


def test_ek7_kucuk_fayda(taslak):
    v = araclar.etken_madde_rehberi("D vitamini")
    solunum = next(k for k in v["kanit_duzeyi"] if "solunum" in k["sonuc_alani"].casefold())
    assert solunum["sonuc_etiketi"] == "kucuk_fayda"


def test_ek8_cift_nokta_yok(taslak):
    for em in araclar.REHBER_KAPSAMI:
        ad = "multivitamin" if em == "multivitamin" else veri.etken_madde_adi(em)
        m = ozet.metin("etken_madde_rehberi", araclar.etken_madde_rehberi(ad))
        assert ".." not in m.replace("...", ""), em


def test_ek9_bos_ilgili_madde_yazilmaz():
    u = araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]
    assert "Sayfada belirtilmemiş" not in json.dumps(u, ensure_ascii=False)


def test_ek10_yas_grubu_ust_siniri_kabul_7():
    # Kabul testi 7: 8 yaş, 400 IU sprey → yaş uyarısı yok; 1 puf = 10 µg = 50 µg sınırının %20'si.
    v = araclar.urun_rehberi("Ocean Vitamin D3 400 IU Sprey", 8)
    assert "yas_uyarisi" not in v
    o = v["urun"]["etken_maddeler"][0]["olcek"]
    assert (o["miktar"], o["ust_sinir"]) == (10, 50)
    assert "yaş grubu üst sınırının %20'si" in o["oran_metni"]


def test_ek12_bilesim_ozeti():
    o = araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]["bilesim_ozeti"]
    assert o["k_vitamini_formu"] == "MK-7 (menakinon-7)" and o["d3_kaynagi"] == "Etikette belirtilmemiş"


def test_turkce_yuzde_eki():
    assert [veri.yuzde(n) for n in (20, 35, 50, 100, 3, 0, 40, 6)] == [
        "%20'si", "%35'i", "%50'si", "%100'ü", "%3'ü", "%0'ı", "%40'ı", "%6'sı"]


# ---- Bölüm 11: sayaçlar -----------------------------------------------------------

async def test_sayaclar_kisisel_veri_tutmaz(taslak):
    sayac.sifirla()
    async with create_connected_server_and_client_session(mcp) as oturum:
        await oturum.call_tool("takviye_rehberi", {"konu": "Kış geldi, Ayşe Yılmaz 0532", "yas": 37, "cinsiyet": "kadin",
                                                   "evre": "gebe", "ilac_grubu": ["kan_sulandirici_varfarin"]})
        await oturum.call_tool("etken_madde_rehberi", {"etken_madde": "gizli serbest metin"})
    r = sayac.rapor()
    metin = json.dumps({k: v for k, v in r.items() if k != "baslangic"}, ensure_ascii=False)
    for yasak in ["Ayşe", "0532", "gebe", "varfarin", "kadin", "37", "gizli serbest metin"]:
        assert yasak not in metin, yasak
    assert r["sayaclar"]["arac"]["takviye_rehberi"] == 1
    assert r["sayaclar"]["yas_araligi"] == {"18–64": 1}
    assert {"etken_madde": "c_vitamini", "sayi": 1} in r["karti_olmayan_en_cok_sorulan_5_madde"]
    assert r["sayaclar"]["kopru"]["soruldu"] >= 1
