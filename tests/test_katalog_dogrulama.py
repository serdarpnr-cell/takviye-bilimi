"""TB-02: katalogdaki birim hataları karantinaya alınır ve hesaplamalara katılmaz."""

import pytest

from server import araclar, veri


def _satir(urun_id: str, em_id: str) -> dict:
    u = next(u for u in veri.urunler() if u["id"] == urun_id)
    return next(e for e in u["etken_maddeler"] if e["etken_madde"] == em_id)


@pytest.mark.parametrize("urun_id, em_id, olasi_birim", [
    ("day2day-the-collagen-mag-plus", "d3", None),          # 25 mg, %500
    ("day2day-the-collagen-mag-plus", "selenyum", None),    # 55 mg, %100
    ("day2day-the-collagen-mag-plus", "b12", "µg"),         # 2,5 mg, %100
    ("day2day-the-collagen-mag-plus", "k2", "µg"),          # 20 mg, %27
    ("ocean-extramag-30-60-tablet", "magnezyum", None),     # birimsiz "200"
    ("ocean-extramag-fibra", "b6", None),                   # birimsiz "6,66"
    ("ocean-biotin-complex", "bakir", None),                # 5000 µg, %50
])
def test_supheli_satir_karantinada(urun_id, em_id, olasi_birim):
    satir = _satir(urun_id, em_id)
    assert satir["karantina"]["gerekce"]
    assert satir["karantina"].get("olasi_birim") == olasi_birim
    assert veri.satir_miktari(satir) is None


def test_yuksek_ama_tutarli_miktar_karantinaya_dusmez():
    # Ocean Extramag Migra: B2 130 mg, BRD %9285,7 → 1,4 mg × 92,857; değer yüksek ama tutarlı.
    satir = _satir("ocean-extramag-migra", "b2")
    assert "karantina" not in satir
    assert veri.satir_miktari(satir) == 130


def test_brd_yuzdesi_ayristirma():
    assert veri.brd_yuzdesi("%500") == 500
    assert veri.brd_yuzdesi("%9285,70") == pytest.approx(9285.7)
    assert veri.brd_yuzdesi("NE* %100") == 100
    assert veri.brd_yuzdesi("**") is None
    assert veri.brd_yuzdesi(None) is None


def test_karantinadaki_her_satir_gerekce_tasir_ve_tutarli_satirlar_gecer():
    karantina = [e for u in veri.urunler() for e in u["etken_maddeler"] if e.get("karantina")]
    assert karantina and all(e["karantina"]["gerekce"] for e in karantina)
    # Kontrolden geçen D vitamini satırlarında ima edilen BRD 5 µg civarındadır (yarısı ile iki katı arası).
    for u in veri.urunler():
        for e in u["etken_maddeler"]:
            if e.get("karantina") or e["etken_madde"] not in veri.kurallar()["etken_maddeler"]:
                continue
            if e["etken_madde"] == "d3" and veri.satir_miktari(e) and veri.brd_yuzdesi(e["brd"]):
                assert 2.5 <= veri.satir_miktari(e) * 100 / veri.brd_yuzdesi(e["brd"]) <= 10, (u["id"], e)


def test_urun_rehberi_karantinadaki_satiri_isaretler():
    kart = araclar.urun_rehberi("Day2Day The Collagen Mag Plus")["urun"]
    b12 = next(e for e in kart["etken_maddeler"] if e["etken_madde"] == "B12 Vitamini")
    assert b12["bu_urundeki_miktar"]["standart_birimde"] is None
    assert "doğrulanamadı" in b12["dogrulanamadi"]
    assert "µg" in b12["dogrulanamadi"]
    # Sitedeki metin olduğu gibi gösterilir; düzeltilmiş değer uydurulmaz.
    assert b12["bu_urundeki_miktar"]["etiketteki_miktar"].startswith("2,5 mg")
