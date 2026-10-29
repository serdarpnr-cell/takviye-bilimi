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
