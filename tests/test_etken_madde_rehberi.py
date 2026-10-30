import json
import re

import pytest

from server import veri
from server.araclar import REHBER_KAPSAMI, _VITAMIN_MINERAL, _katalog_eslesmesi, etken_madde_rehberi

ALANLAR = {
    "kisa_ozet", "kimde_kanit_var", "kanit_duzeyi", "urun_sayfasi_beyanlari", "besinle_karsilama", "efsa_ust_sinir",
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


def test_urun_sayfasi_beyanlari_tekillestirilir(taslak):
    # TB-16: alan adı "onaylı" demez; ürün sayfası metnidir.
    y = etken_madde_rehberi("D vitamini")
    assert "onayli_saglik_beyanlari" not in y
    metinler = y["urun_sayfasi_beyanlari"]["metinler"]
    assert metinler
    sade = [re.sub(r"^d vitamini ", "", veri.normalize(m)) for m in metinler]
    assert len(sade) == len(set(sade))


def test_katalog_en_fazla_bes_urun_tek_icerikliler_once(taslak):
    # TB-14: en fazla 5 ürün; yalnızca bu maddeyi içerenler önce, kendi içinde alfabetik; kalanı sayıyla.
    y = etken_madde_rehberi("D vitamini")
    k = y["katalogdaki_urunler"]
    assert 0 < len(k) <= 5
    tekler = [u["tek_icerikli"] for u in k]
    assert tekler == sorted(tekler, reverse=True)
    for grup in (True, False):
        adlar = [u["ad"] for u in k if u["tek_icerikli"] is grup]
        assert adlar == sorted(adlar, key=veri.normalize)
    assert y["katalog_ozeti"]["kalan_urun_sayisi"] > 0
    assert "Sponsorlu veya öncelikli sıralama yoktur" in y["katalog_ozeti"]["siralama_olcutu"]
    for u in k:
        assert u["parti_analizi_var"] is False and u["porsiyondaki_miktar"]


def test_katalog_yas_sinirina_gore_suzulur(taslak):
    # TB-14: 42 yaş girilince çocuk ürünleri gelmez.
    y = etken_madde_rehberi("D vitamini", yas=42)
    urunler = {u["ad"]: u for u in veri.urunler()}
    for u in y["katalogdaki_urunler"]:
        ys = urunler[u["ad"]]["yas_siniri"]
        assert ys["max"] is None or ys["max"] >= 42, u["ad"]
    assert y["katalog_ozeti"]["yas_siniri_disinda_kalan"] > 0


def test_beyan_baska_maddeye_sizmaz(taslak):
    # TB-15: bir maddenin rehberinde başka maddeyi adıyla anan beyan görünmez.
    from server.araclar import _katalog_eslesmesi
    for u in veri.urunler():
        if not _katalog_eslesmesi("d3", u):
            continue
        for b in veri.urun_saglik_beyanlari(u):
            if b["etken_maddeler"] and "d3" not in b["etken_maddeler"]:
                assert b["metin"] not in etken_madde_rehberi("D vitamini")["urun_sayfasi_beyanlari"]["metinler"]


def test_senin_grubun_ilk_satirda(taslak):
    # TB-18
    y = etken_madde_rehberi("D vitamini", yas=42, cinsiyet="erkek")
    assert y["kisa_ozet"].startswith("Senin grubun: 75 yaş altı sağlıklı yetişkinler.")
    assert etken_madde_rehberi("D vitamini", yas=80)["senin_grubun"]["grup"] == "75 yaş ve üstü"
    assert etken_madde_rehberi("D vitamini", yas=30, evre="gebe")["senin_grubun"]["grup"] == "Gebeler"
    assert "senin_grubun" not in etken_madde_rehberi("D vitamini")


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
    assert "kanit_duzeyi" not in y and "kimde_kanit_var" not in y
    # Kart yayında değilse ürün listesi de dönmez (TB-05); güvenlik bilgisi kalır.
    assert "katalogdaki_urunler" not in y
    assert y["efsa_ust_sinir"] and y["zorunlu_uyarilar"] and y["genel_kilavuz"] and y["kaynaklar"]


@pytest.mark.parametrize("em_id", REHBER_KAPSAMI)
def test_ilk_setin_her_maddesi_yanit_uretir(em_id, taslak):
    ad = "multivitamin" if em_id == "multivitamin" else veri.etken_madde_adi(em_id)
    y = etken_madde_rehberi(ad)
    assert "kanit_karti_hazirlanan_maddeler" not in y, ad
    assert y["kaynaklar"]


def test_multivitamin_katalogu_esige_gore():
    eslesen = [u for u in veri.urunler() if _katalog_eslesmesi("multivitamin", u)]
    assert eslesen
    for u in veri.urunler():
        kimlikler = {e["etken_madde"] for e in u["etken_maddeler"]} & _VITAMIN_MINERAL
        assert bool(_katalog_eslesmesi("multivitamin", u)) == (len(kimlikler) >= 5), u["ad"]


@pytest.mark.parametrize("ad", ["omega-3", "B12", "magnezyum", "demir", "multivitamin"])
def test_kanit_karti_yoksa_urun_listesi_donmez(ad, monkeypatch):
    # TB-05: genel soruya yalnızca ürün listesi dönmez; kanıt kartı hazırlanıyor notu ve kurum sayfası döner.
    # Yayın ayarı (taslak kartlar kapalı): bu maddelerin kartları taslak olduğu için sunulmaz.
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    y = etken_madde_rehberi(ad, yas=42, cinsiyet="erkek")
    assert "katalogdaki_urunler" not in y
    assert "onayli_saglik_beyanlari" not in y
    assert "ürün listesi gösterilmez" in y["kisa_ozet"]
    assert y["kanit_durumu"] == "Kanıt kartı hazırlanıyor."
    assert y["genel_kilavuz"]["url"].startswith("https://ods.od.nih.gov/factsheets/")
    assert re.search(r"Katalogda bu maddeyi içeren \d+ ürün var", y["katalog_kapsami"])
    assert all(k["tur"] != "uretici_icerigi" for k in y["kaynaklar"])
    assert not any(u["ad"] in json.dumps(y, ensure_ascii=False) for u in veri.urunler())


def test_kart_disi_madde_urun_adi_listelemez():
    y = etken_madde_rehberi("kreatin")
    assert "katalogda_bu_adi_iceren_urunler" not in y
    assert "Ocean Kreatin" not in json.dumps(y, ensure_ascii=False)
    assert re.search(r"içeren [1-9]\d* ürün var", y["katalog_kapsami"])
    bos = etken_madde_rehberi("xyz")
    assert "içeren 0 ürün var" in bos["katalog_kapsami"]
    assert len(bos["kanit_karti_hazirlanan_maddeler"]) == 12


@pytest.mark.parametrize("ad", ["D vitamini", "omega-3", "beta-karoten", "multivitamin", "kreatin"])
def test_doz_onermez(ad, taslak):
    metin = _metin(etken_madde_rehberi(ad, yas=40, evre="gebe", sigara="her_gun"))
    for kalip in DOZ_KALIPLARI:
        assert not re.search(kalip, metin), kalip


@pytest.mark.parametrize("ad, alan", [
    ("B12", "Bilişsel işlev, depresif belirtiler ve yorgunluk"),
    ("demir", "Anemi ve demir eksikliği"),
    ("magnezyum", "Kas krampları"),
    ("omega-3", "Kalp-damar olayları"),
])
def test_faz1_kartlari_taslak_olarak_sunulur(ad, alan, taslak):
    # TB-13: yorgunluk ekseninin kartları. Taslak etiketi her kartta durur.
    y = etken_madde_rehberi(ad)
    assert alan in {k["sonuc_alani"] for k in y["kanit_duzeyi"]}
    assert all(k["durum"].startswith("Taslak") for k in y["kanit_duzeyi"])
    assert y["kanit_durumu"].startswith("Taslak")


def test_faz1_kartlari_yayin_sunucusunda_gorunmez(monkeypatch):
    monkeypatch.delenv("TB_TASLAK_GOSTER", raising=False)
    for ad in ("B12", "demir", "magnezyum", "omega-3"):
        assert "kanit_duzeyi" not in etken_madde_rehberi(ad)


def test_b12_form_bolumu_dolu(taslak):
    # TB-21 ve kabul ölçütü: "Hangi B12 bilimsel olarak en güçlü?" → form bölümü dolu.
    f = etken_madde_rehberi("B12")["formlar"]
    assert "1000 µg" in f["agizdan_ve_igne"] and "hekim" in f["agizdan_ve_igne"]
    assert "randomize çalışma bulunmadı" in f["metil_ve_siyano"]


def test_b12_metformin_grubu_one_cikar(taslak):
    y = etken_madde_rehberi("B12", yas=60, ilac_grubu=["metformin"])
    assert y["senin_grubun"]["grup"] == "Uzun süre metformin kullananlar"
    assert any("metformin" in d for d in y["dikkat_edecekler"])


def test_olumsuz_ve_belirsiz_sonuclar_yumusatilmaz(taslak):
    # CLAUDE.md kural 6: "etkisiz" ve "belirsiz" sonuçlar gizlenmez.
    kartlar = {k["sonuc_alani"]: k for ad in ("omega-3", "magnezyum", "B12")
               for k in etken_madde_rehberi(ad)["kanit_duzeyi"]}
    assert kartlar["Kalp-damar olayları"]["sonuc_yonu"] == "etkisiz"
    assert kartlar["Kas krampları"]["sonuc_yonu"] == "etkisiz"
    assert kartlar["Erken doğum"]["sonuc_yonu"] == "belirsiz"
    assert "100 kişiden yaklaşık 3" in kartlar["Kalp-damar olayları"]["mutlak_fark"]
