import json
import re

import pytest

from server import veri
from server.araclar import REHBER_KAPSAMI, _VITAMIN_MINERAL, etken_madde_rehberi

ALANLAR = {
    "kisa_ozet", "kimde_kanit_var", "kanit_duzeyi", "onayli_saglik_beyanlari", "besinle_karsilama", "efsa_ust_sinir",
    "etkilesimler", "dikkat_edecekler", "hekime_sorulacaklar", "kaynaklar", "katalogdaki_urunler", "uyari",
}
# Kişiye doz ya da ürün öneren kalıplar.
DOZ_KALIPLARI = [
    r"\balmal[ıi]s[ıi]n[ıi]z\b", r"\bal[ıi]n[ıi]z?\b", r"\bkullan[ıi]n[ıi]z?\b", r"\bkullanmal[ıi]s[ıi]n[ıi]z\b",
    r"\bönerilen doz\b", r"\bsize uygun doz\b", r"\bbunu al\b",
]


@pytest.fixture
def taslak(monkeypatch):
    monkeypatch.setenv("TB_TASLAK_GOSTER", "1")


def _metin(y: dict) -> str:
    return json.dumps(y, ensure_ascii=False).casefold()


def test_es_anlamlilar_ayni_maddeye_gider(taslak):
    adlar = {etken_madde_rehberi(a)["kisa_ozet"] for a in ["D vitamini", "vitamin d", "Kolekalsiferol", "D3"]}
    assert len(adlar) == 1


def test_d_vitamini_tam_cikti(taslak, uyari_var):
    y = etken_madde_rehberi("D vitamini")
    uyari_var(y)
    assert ALANLAR <= y.keys()
    assert "medikal kurul onayı bekliyor" in y["kanit_durumu"]
    duzeyler = {k["sonuc_alani"]: (k["duzey"], k["sonuc_yonu"]) for k in y["kanit_duzeyi"]}
    assert duzeyler["Kırık"] == ("guclu", "etkisiz")
    assert duzeyler["Akut solunum yolu enfeksiyonları"] == ("orta", "fayda")
    assert all(k["mutlak_fark"] and k["dayanak"] for k in y["kanit_duzeyi"])
    assert "güvenlik tavanıdır" in y["efsa_ust_sinir"]["not"]
    assert y["efsa_ust_sinir"]["deger"].startswith("100 µg")
    assert y["tahlil_notu"] and y["besinle_karsilama"]


def test_kaynaklar_bagimsizlar_once_uretici_icerigi_sonra(taslak):
    turler = [k["tur"] for k in etken_madde_rehberi("D vitamini")["kaynaklar"]]
    assert {"kilavuz", "rct", "meta_analiz", "duzenleyici"} <= set(turler)
    ilk_uretici = turler.index("uretici_icerigi")
    assert all(t == "uretici_icerigi" for t in turler[ilk_uretici:])


def test_onayli_beyanlar_tekillestirilir(taslak):
    metinler = etken_madde_rehberi("D vitamini")["onayli_saglik_beyanlari"]["metinler"]
    assert metinler
    sade = [re.sub(r"^d vitamini ", "", veri.normalize(m)) for m in metinler]
    assert len(sade) == len(set(sade))


def test_katalog_alfabetik_ve_tarafsiz(taslak):
    y = etken_madde_rehberi("D vitamini")
    adlar = [u["ad"] for u in y["katalogdaki_urunler"]]
    assert adlar == sorted(adlar, key=veri.normalize)
    assert "Ocean D3K2 Damla" in adlar
    for u in y["katalogdaki_urunler"]:
        assert u["parti_analizi_var"] is False
        assert u["porsiyondaki_miktar"]
    assert "Sponsorlu veya öncelikli sıralama yoktur" in y["siralama_olcutu"]


def test_profile_gore_dikkat_edilecekler(taslak):
    yetiskin = etken_madde_rehberi("D vitamini")
    cocuk = etken_madde_rehberi("D vitamini", yas=8)
    gebe = etken_madde_rehberi("D vitamini", yas=30, evre="gebe")
    assert not any("1–10 yaş" in d for d in yetiskin["dikkat_edecekler"])
    assert any("1–10 yaş" in d for d in cocuk["dikkat_edecekler"])
    assert cocuk["efsa_ust_sinir"]["deger"].startswith("50 µg")
    assert any("gebelikte" in d for d in gebe["dikkat_edecekler"])
    assert not any("gebelikte" in d for d in yetiskin["dikkat_edecekler"])


def test_ilac_grubu_etkilesim_kuralini_tetikler():
    y = etken_madde_rehberi("omega-3", ilac_grubu=["kan_sulandirici_varfarin"])
    assert y["etkilesimler"]
    assert any("kan sulandırıcı" in d for d in y["dikkat_edecekler"])
    assert any("kan sulandırıcı" in s for s in y["hekime_sorulacaklar"])
    assert etken_madde_rehberi("omega-3")["dikkat_edecekler"] == []


def test_taslak_gosterilmezse_kanit_yerine_durum_bildirilir(monkeypatch, uyari_var):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    y = etken_madde_rehberi("D vitamini")
    uyari_var(y)
    assert "kurul onayı bekliyor" in y["kisa_ozet"]
    assert y["kanit_duzeyi"] == [] and y["kimde_kanit_var"] == []
    assert y["efsa_ust_sinir"] and y["katalogdaki_urunler"] and y["kaynaklar"]


@pytest.mark.parametrize("em_id", REHBER_KAPSAMI)
def test_ilk_setin_her_maddesi_yanit_uretir(em_id, taslak):
    ad = "multivitamin" if em_id == "multivitamin" else veri.etken_madde_adi(em_id)
    y = etken_madde_rehberi(ad)
    assert "kanit_karti_hazirlanan_maddeler" not in y, ad
    assert y["kaynaklar"]


def test_multivitamin_katalogu_esige_gore():
    y = etken_madde_rehberi("multivitamin")
    assert y["katalogdaki_urunler"]
    urunler = {u["ad"]: u for u in veri.urunler()}
    for u in y["katalogdaki_urunler"]:
        kimlikler = {e["etken_madde"] for e in urunler[u["ad"]]["etken_maddeler"]} & _VITAMIN_MINERAL
        assert len(kimlikler) >= 5, u["ad"]


def test_kart_disi_madde_katalogdan_bulunur():
    y = etken_madde_rehberi("kreatin")
    assert "Ocean Kreatin" in y["katalogda_bu_adi_iceren_urunler"]
    bos = etken_madde_rehberi("xyz")
    assert bos["katalogda_bu_adi_iceren_urunler"] == []
    assert len(bos["kanit_karti_hazirlanan_maddeler"]) == 12


@pytest.mark.parametrize("ad", ["D vitamini", "omega-3", "beta-karoten", "multivitamin", "kreatin"])
def test_doz_onermez(ad, taslak):
    metin = _metin(etken_madde_rehberi(ad, yas=40, evre="gebe", sigara="her_gun"))
    for kalip in DOZ_KALIPLARI:
        assert not re.search(kalip, metin), kalip
