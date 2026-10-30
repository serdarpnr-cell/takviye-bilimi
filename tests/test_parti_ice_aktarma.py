"""v0.4 C7: parti analizi içe aktarma hattı."""

import sys
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))
from parti_analizi_al import denetle  # noqa: E402

from server import veri  # noqa: E402

SATIR = {"parti_no": "L1", "urun_kodu": "ocean-vitamin-d3k2-damla", "laboratuvar": "Örnek Lab", "akreditasyon_no": "AB-1",
         "analiz_tarihi": "2026-10-01", "rapor_no": "R-1", "etken_madde": "D vitamini", "etiketteki": "25", "olculen": "26",
         "birim": "µg", "yontem": "HPLC", "yayin_onaylayan": "Kalite Müdürü", "yayin_onay_tarihi": "2026-10-05"}


def test_gecerli_parti():
    partiler, hatalar = denetle([SATIR, {**SATIR, "etken_madde": "K2", "etiketteki": "11,25", "olculen": "11"}], date(2026, 10, 30))
    assert hatalar == [] and partiler[0]["demo"] is False and len(partiler[0]["sonuclar"]) == 2


def test_onaysiz_ve_uyumsuz_satir_reddedilir():
    _, hatalar = denetle([{**SATIR, "yayin_onaylayan": ""}, {**SATIR, "parti_no": "L2", "etiketteki": "40"},
                          {**SATIR, "parti_no": "L3", "birim": "mg"}, {**SATIR, "parti_no": "L4", "etken_madde": "Demir"}],
                         date(2026, 10, 30))
    metin = "\n".join(hatalar)
    for parca in ["yayın onayı", "uyuşmuyor", "birim", "tanımlı bir etken madde değil"]:
        assert parca in metin, parca


def test_demo_kaydi_korunur():
    assert veri.parti_bul("DEMO-0001")["demo"] is True
