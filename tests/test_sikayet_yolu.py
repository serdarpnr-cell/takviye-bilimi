"""TB-19: şikâyetten yola çıkan giriş. Ürün listesi döndürmez."""

import json

import pytest

from server import veri
from server.araclar import sikayet_yolu


@pytest.mark.parametrize("metin", ["Kendimi yorgun hissediyorum, ne kullanmalıyım?", "hep yorgunum", "halsizlik", "YORGUNLUK"])
def test_dogal_ifade_yorgunluk_yoluna_gider(metin, uyari_var):
    y = sikayet_yolu(metin)
    uyari_var(y)
    assert y["kirmizi_bayraklar"] and y["hekimin_isteyebilecegi_tahliller"]["liste"]


def test_urun_listesi_ve_urun_adi_yok():
    # Kabul ölçütü: kırmızı bayrak, tahlil ve karne önerisi; ürün listesi yok.
    y = sikayet_yolu("yorgunum", yas=40, cinsiyet="kadin")
    metin = json.dumps(y, ensure_ascii=False)
    assert y["yasam_karnesi"]["arac"] == "yasam_karnesi"
    assert not any(u["ad"] in metin for u in veri.urunler())
    assert "katalogdaki_urunler" not in y


def test_tahlil_oncesi_takviye_uyarisi():
    y = sikayet_yolu("yorgunluk")
    assert any("B12 tahlilinden önce" in m for m in y["tahlil_oncesi"])
    assert any("Demir takviyesi kandaki demir" in m for m in y["tahlil_oncesi"])


def test_yasa_ve_cinsiyete_gore_ek_bayrak():
    genc = sikayet_yolu("yorgunluk", yas=30, cinsiyet="erkek")
    ileri = sikayet_yolu("yorgunluk", yas=62, cinsiyet="erkek")
    assert len(ileri["kirmizi_bayraklar"]) == len(genc["kirmizi_bayraklar"]) + 1
    assert ileri["kisa_ozet"].startswith("Senin yaş ve cinsiyet grubunda")
    assert all(b["dayanak"] for b in ileri["kirmizi_bayraklar"])


def test_kanit_karti_yoksa_hazirlaniyor_der(monkeypatch):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    y = sikayet_yolu("yorgunluk")
    assert all(k["durum"] == "Kanıt kartı hazırlanıyor." for k in y["ilgili_kanit_kartlari"])


def test_taslak_kartlar_sunulabilirken_baglanir(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")
    y = sikayet_yolu("yorgunluk")
    alanlar = {(k["etken_madde"], k.get("sonuc_alani")) for k in y["ilgili_kanit_kartlari"]}
    assert ("Demir", "Yorgunluk") in alanlar
    assert ("B12 vitamini", "Bilişsel işlev, depresif belirtiler ve yorgunluk") in alanlar


def test_tanimsiz_sikayet_hazir_yollari_listeler():
    y = sikayet_yolu("baş ağrısı")
    assert y["hazir_yollar"] == ["Yorgunluk"]
    assert "hekimle değerlendirilmelidir" in y["kisa_ozet"]


def test_kaynaklar_dogrulanmis():
    kayitlar = veri.kaynak_kayitlari()
    for yol in veri.sikayet_yollari().values():
        for kid in [k for b in yol["kirmizi_bayraklar"] for k in b["kaynaklar"]] + yol["tahliller"]["kaynaklar"]:
            assert kayitlar[kid]["dogrulandi"], kid
