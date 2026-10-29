"""Seçenekli karne (P0-4): seçenek kodları, aralık eşlemesi ve MCP Apps arayüzü."""

import re

import pytest
from pydantic import ValidationError

from server.app import KARNE_ARAYUZU, MCP_APP_MIME, TALIMATLAR, mcp
from server.araclar import _SECENEKLER, SORULAR, _aralik, _puanla, yasam_karnesi
from server.arayuz import karne_html

SAYISAL = [a for a, liste in _SECENEKLER.items() if len(liste[0]) == 4]


def test_her_soru_secenek_dondurur():
    for s in SORULAR:
        assert s["secenekler"], s["anahtar"]
        for sec in s["secenekler"]:
            assert sec.keys() == {"etiket", "deger"}


def test_cevapsiz_cagri_secenekli_sorulari_ve_yonergeyi_dondurur():
    y = yasam_karnesi()
    assert all(s["secenekler"] for s in y["eksik_sorular"])
    assert "seçenek" in y["soru_yonergesi"]


@pytest.mark.parametrize("anahtar", SAYISAL)
def test_secenek_araliklari_tek_puan_duzeyinde_kalir(anahtar):
    for etiket, kod, alt, ust in _SECENEKLER[anahtar]:
        assert _puanla(anahtar, alt) == _puanla(anahtar, ust), f"{kod} iki puan düzeyine taşıyor"


@pytest.mark.parametrize("anahtar", SAYISAL)
def test_secenekler_bitisik_ve_cakismasiz(anahtar):
    araliklar = [(s[2], s[3]) for s in _SECENEKLER[anahtar]]
    for (a1, u1), (a2, u2) in zip(araliklar, araliklar[1:]):
        assert u1 < a2, (u1, a2)


TAM_SAYI = {"hareket_gun": 1, "uyku_saat": 6.5, "sebze_meyve_porsiyon": 2, "balik_haftalik": 0.5, "sigara": "her_gun", "stres": "sik"}
TAM_KOD = {"hareket_gun": "1_2_gun", "uyku_saat": "6_7_saat", "sebze_meyve_porsiyon": "0_2_porsiyon",
           "balik_haftalik": "ayda_1_3", "sigara": "her_gun", "stres": "sik"}


def test_sayi_ve_kod_ayni_karneyi_verir():
    a, b = yasam_karnesi(TAM_SAYI), yasam_karnesi(TAM_KOD)
    assert [k["puan"] for k in a["karne"]] == [k["puan"] for k in b["karne"]]
    assert a["hedefler"] == b["hedefler"]
    assert a["takviye_baglantilari"] == b["takviye_baglantilari"]
    assert a["guvenlik_uyarilari"] == b["guvenlik_uyarilari"]


def test_kod_cevabi_etiketiyle_gosterilir():
    y = yasam_karnesi(TAM_KOD)
    hareket = next(k for k in y["karne"] if k["alan"] == "Hareket")
    assert hareket["cevap"] == "1–2 gün"


def test_kodla_kural_tetiklenir():
    assert yasam_karnesi(TAM_KOD)["takviye_baglantilari"]
    assert _aralik("balik_haftalik", "ayda_1_3") == (0.25, 0.75)


def test_tanimsiz_kod_reddedilir():
    with pytest.raises(ValidationError):
        yasam_karnesi({**TAM_KOD, "hareket_gun": "1-2 gün"})


def test_sunucu_talimati_secenekli_soruyu_soyler():
    assert "Karne sorularını tek seferde ve seçenekleriyle sor" in TALIMATLAR


async def test_arac_arayuz_kaynagina_baglidir():
    arac = next(t for t in await mcp.list_tools() if t.name == "yasam_karnesi")
    assert arac.meta["ui"]["resourceUri"] == KARNE_ARAYUZU


async def test_arayuz_kaynagi_listelenir_ve_okunur():
    kaynaklar = {str(k.uri): k for k in await mcp.list_resources()}
    assert kaynaklar[KARNE_ARAYUZU].mimeType == MCP_APP_MIME
    icerik = list(await mcp.read_resource(KARNE_ARAYUZU))[0]
    assert icerik.mime_type == MCP_APP_MIME
    assert "<!doctype html>" in icerik.content


def test_arayuz_tum_kodlari_icerir_ve_dis_kaynak_yuklemez():
    html = karne_html()
    for liste in _SECENEKLER.values():
        for s in liste:
            assert f'"{s[1]}"' in html, s[1]
    assert "__SORULAR__" not in html
    assert not re.search(r'<(script|link|img)[^>]+(src|href)="https?://', html)
    assert "ui/initialize" in html and "tools/call" in html
