"""v0.4 A1–A2: tetiklenme setinin yapısı ve koşucunun puanlaması (API çağrısı yapılmaz)."""

import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))
import tetiklenme_olc as t  # noqa: E402

from server.app import ACIKLAMALAR  # noqa: E402

SET = t.vakalar(KOK / "tests" / "tetiklenme" / "set_v1.jsonl")


def test_set_dagilimi():
    cekirdek = [v for v in SET if v["kategori"] == "cekirdek"]
    assert len(cekirdek) == 30 and len([v for v in SET if v["kategori"] == "zor"]) == 10
    assert len([v for v in SET if v["kategori"] == "negatif"]) == 5
    assert Counter(v["beklenen_ilk_arac"] for v in cekirdek) == {
        "takviye_rehberi": 6, "sikayet_yolu": 4, "etken_madde_rehberi": 4, "urun_rehberi": 4, "karsilastir": 4,
        "kisisel_rutin": 4, "yasam_karnesi": 2, "parti_analizi": 2}
    assert Counter(v["set"] for v in cekirdek) == {"gelistirme": 20, "tutma": 10}
    assert len({v["id"] for v in SET}) == len(SET)


def test_mesajlarda_arac_adi_gecmez():
    for v in SET:
        for ad in [*ACIKLAMALAR, "tahlil_goster", "Takviye Bilimi"]:
            assert ad.casefold() not in v["mesaj"].casefold(), (v["id"], ad)


def test_puanlama_ve_rapor(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "CIKTI", tmp_path)
    sahte = lambda m, s, a, mesaj: (next(v["beklenen_ilk_arac"] for v in SET if v["mesaj"] == mesaj), {}, "tool_use")  # noqa: E731
    kayit = t.olc(sahte, "sahte", "", [], SET, 2)
    o = t.ozetle(kayit)
    assert o["dogruluk"]["cekirdek_tutma"] == 1.0 and o["dogruluk"]["negatif"] == 1.0
    assert o["tekrarlar_arasi_tutarlilik"] == 1.0 and o["hatali_vakalar"] == []
    rapor = t.rapor_yaz({"sahte": o}, "http://yerel", 2).read_text(encoding="utf-8")
    assert "Sınırlama" in rapor and "geçti" in rapor
    # Negatif vakada Takviye Bilimi aracı hatadır; dikkat dağıtıcı araç kabul.
    neg = next(v for v in SET if v["kategori"] == "negatif")
    assert t.dogru_mu(neg, "web_search") and not t.dogru_mu(neg, "takviye_rehberi")
