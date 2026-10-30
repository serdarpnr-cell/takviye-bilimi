"""v0.4 C5: TB-24 etiket uyarısı içe aktarma doğrulaması."""

import sys
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))
from etiket_uyarilari_al import denetle  # noqa: E402

from server import araclar  # noqa: E402

GECERLI = {"urun_kodu": "ocean-vitamin-d3k2-damla", "urun_adi": "Ocean D3K2 Damla",
           "uyari_metni_birebir": "Örnek uyarı metni.", "ambalaj_revizyon_no": "R1", "tarih": "2026-10-01"}


def test_gecerli_satir():
    sonuc, hatalar = denetle([GECERLI], date(2026, 10, 30))
    assert hatalar == [] and sonuc["ocean-vitamin-d3k2-damla"]["uyarilar"] == ["Örnek uyarı metni."]


def test_hatali_satirlar_reddedilir():
    kotu = [{**GECERLI, "urun_kodu": "yok-boyle"}, {**GECERLI, "urun_adi": "Başka Ürün"},
            {**GECERLI, "uyari_metni_birebir": " "}, {**GECERLI, "ambalaj_revizyon_no": ""},
            {**GECERLI, "tarih": "30.10.2026"}, {**GECERLI, "tarih": "2027-01-01"}, GECERLI, GECERLI]
    _, hatalar = denetle(kotu, date(2026, 10, 30))
    metin = "\n".join(hatalar)
    for parca in ["katalogda yok", "eşleşmiyor", "metni boş", "revizyon numarası boş", "YYYY-AA-GG", "ileri bir gün", "tekrar ediyor"]:
        assert parca in metin, parca


def test_veri_gelene_kadar_ambalaj_notu():
    assert araclar.urun_rehberi("Ocean D3K2 Damla")["urun"]["etiket_uyarilari"] == araclar.ETIKET_UYARISI_NOTU
