import pytest
from pydantic import ValidationError

from server.araclar import SORULAR, yasam_karnesi

TAM = {
    "hareket_gun": 1,
    "uyku_saat": 6,
    "sebze_meyve_porsiyon": 2,
    "balik_haftalik": 0,
    "sigara": "hayir",
    "stres": "sik",
}


def test_alti_soru_var():
    assert len(SORULAR) == 6


def test_cevapsiz_cagri_sorulari_dondurur(uyari_var):
    y = yasam_karnesi()
    uyari_var(y)
    assert len(y["eksik_sorular"]) == 6
    assert "karne" not in y


def test_eksik_cevap(uyari_var):
    y = yasam_karnesi({"hareket_gun": 3})
    uyari_var(y)
    assert len(y["eksik_sorular"]) == 5


def test_karne_ve_en_fazla_uc_hedef(uyari_var):
    y = yasam_karnesi(TAM)
    uyari_var(y)
    assert len(y["karne"]) == 6
    assert y["toplam_puan"] == 4
    assert [h["alan"] for h in y["hedefler"]] == ["Hareket", "Sebze ve meyve", "Balık"]


def test_sigara_her_gun_ilk_hedeftir():
    y = yasam_karnesi({**TAM, "sigara": "her_gun"})
    assert len(y["hedefler"]) == 3
    assert y["hedefler"][0]["alan"] == "Tütün"
    assert "171" in y["hedefler"][0]["ilk_adim"]


def test_her_sey_iyiyse_hedef_yok():
    y = yasam_karnesi({"hareket_gun": 5, "uyku_saat": 8, "sebze_meyve_porsiyon": 5,
                       "balik_haftalik": 2, "sigara": "hayir", "stres": "bazen"})
    assert y["toplam_puan"] == 12
    assert y["hedefler"] == []


def test_yuksek_stres_icin_uzman_notu_ve_cocuk_notu():
    y = yasam_karnesi({**TAM, "stres": "neredeyse_her_gun"}, yas=15)
    assert any("ruh sağlığı" in n for n in y["notlar"])
    assert any("yetişkinler" in n for n in y["notlar"])


def test_gecersiz_cevap_reddedilir():
    with pytest.raises(ValidationError):
        yasam_karnesi({**TAM, "hareket_gun": 9})
    with pytest.raises(ValidationError):
        yasam_karnesi({**TAM, "sigara": "bazen"})


def test_cevapsiz_cagri_sorulari_bir_kez_tasir():
    # TB-25: tum_sorular ile eksik_sorular aynı içeriği iki kez taşımaz.
    assert "tum_sorular" not in yasam_karnesi()


def test_ilk_adim_mevcut_seviyeden_bir_basamak_yukari():
    # TB-09: 3–4 gün hareket edene "2 güne 20 dk yürüyüş" denmez.
    hic = next(h for h in yasam_karnesi({**TAM, "hareket_gun": 0})["hedefler"] if h["alan"] == "Hareket")
    orta = next(h for h in yasam_karnesi({**TAM, "hareket_gun": "3_4_gun"})["hedefler"] if h["alan"] == "Hareket")
    assert "2 güne" in hic["ilk_adim"]
    assert "bir gün daha" in orta["ilk_adim"] and "2 güne" not in orta["ilk_adim"]


def test_haftada_bir_balik_iyi_sayilir():
    # TB-10: AHA'nın haftada 1–2 kez önerisiyle hizalı.
    balik = next(k for k in yasam_karnesi({**TAM, "balik_haftalik": "haftada_1"})["karne"] if k["alan"] == "Balık")
    assert balik["seviye"] == "iyi"


def test_stres_alani_sorusuyla_ayni_adi_tasir():
    # TB-28
    alanlar = [k["alan"] for k in yasam_karnesi(TAM)["karne"]]
    assert "Stres" in alanlar and "Dinlenme" not in alanlar


def test_dokuz_saatten_uzun_uyku_orta_ve_on_saat_ustu_not():
    y = yasam_karnesi({**TAM, "uyku_saat": "9_saatten_fazla"})
    assert next(k for k in y["karne"] if k["alan"] == "Uyku")["seviye"] == "orta"
    assert any("10 saatten uzun" in n for n in yasam_karnesi({**TAM, "uyku_saat": 11})["notlar"])
