"""Görsel kartları gerçek tarayıcıda, MCP Apps host'unu taklit ederek çizer ve denetler.

Kullanım:
    python scripts/kart_onizleme.py [--cikti <dizin>] [--goruntu]

Her senaryo için kartın HTML'i bir iframe'e yüklenir; host benzetimi ui/initialize'a tema bağlamıyla yanıt verir,
araç girdisini ve sonucunu (structuredContent) gönderir, kartın tools/call isteklerini (ör. katalog_sayfasi)
sunucudaki gerçek fonksiyonların önceden hesaplanmış yanıtlarıyla karşılar. Rapor: konsol hataları, alt bilgi,
beklenen öğeler, iframe yüksekliği. --goruntu açık ve koyu temada ekran görüntüsü kaydeder.

Gerekenler: Node.js ve Playwright (Chromium). Kişisel veri yoktur; senaryolar test personasıdır.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
os.environ.setdefault("TB_TASLAK_GOSTER", "1")

from server import araclar, arayuz  # noqa: E402

NODE_BETIGI = Path(__file__).resolve().parent / "kart_onizleme.mjs"


def _sonuc(v: dict) -> dict:
    return {"content": [{"type": "text", "text": v["kisa_ozet"]}], "structuredContent": v, "isError": False}


def senaryolar() -> list[dict]:
    karne_cevap = {"hareket_gun": "1_2_gun", "uyku_saat": "6_7_saat", "sebze_meyve_porsiyon": "0_2_porsiyon",
                   "balik_haftalik": "hic", "sigara": "her_gun", "stres": "sik"}
    d_vitamini = {"etken_madde": "D vitamini", "yas": 42}
    return [
        {"ad": "karne_form", "html": arayuz.karne_html(), "girdi": {}, "sonuc": _sonuc(araclar.yasam_karnesi()),
         "beklenen": ["form fieldset", "#gonder"]},
        {"ad": "karne_sonuc", "html": arayuz.karne_html(), "girdi": {"cevaplar": karne_cevap},
         "sonuc": _sonuc(araclar.yasam_karnesi(karne_cevap, 45)), "beklenen": [".puan", "#kaynaklar"]},
        {"ad": "kanit_d_vitamini", "html": arayuz.kart_html("kanit"), "girdi": d_vitamini,
         "sonuc": _sonuc(araclar.etken_madde_rehberi(**d_vitamini)),
         "cagrilar": {"katalog_sayfasi": [_sonuc(araclar.katalog_sayfasi("D vitamini", n, 42)) for n in range(2, 8)]},
         "tikla": "section button.ikinci", "beklenen": [".nokta-dizisi", ".sonuc-karti", "#kaynaklar"]},
        {"ad": "kanit_demir_erkek", "html": arayuz.kart_html("kanit"), "girdi": {"etken_madde": "demir", "cinsiyet": "erkek"},
         "sonuc": _sonuc(araclar.etken_madde_rehberi("demir", cinsiyet="erkek")), "beklenen": [".guvenlik", ".sonuc-karti"]},
        {"ad": "urun_d3k2_8_yas", "html": arayuz.kart_html("urun"), "girdi": {"urun": "Ocean D3K2 Damla", "yas": 8},
         "sonuc": _sonuc(araclar.urun_rehberi("Ocean D3K2 Damla", 8)), "beklenen": [".cubuk-sinir", ".guvenlik"]},
        {"ad": "urun_collagen", "html": arayuz.kart_html("urun"), "girdi": {"urun": "Day2Day The Collagen Mag Plus"},
         "sonuc": _sonuc(araclar.urun_rehberi("Day2Day The Collagen Mag Plus")), "beklenen": [".rozet.uyari", ".cubuk"]},
        {"ad": "rutin_varfarin", "html": arayuz.kart_html("rutin"), "girdi": {},
         "sonuc": _sonuc(araclar.kisisel_rutin(58, "kadin", ilac_grubu=["kan_sulandirici_varfarin"],
                                               mevcut_urunler=["Ocean D3K2 Damla", "Day2Day The Collagen Mag Plus"],
                                               diger_urun_icerikleri=[{"ad": "Multivitamin", "icerikler": [
                                                   {"etken_madde": "D vitamini", "miktar": 2000, "birim": "IU"}]}])),
         "beklenen": [".cubuk-dolgu span", ".cubuk-sinir", ".rozet"]},
    ]


def calistir(cikti: Path | None, goruntu: bool) -> list[dict]:
    with tempfile.TemporaryDirectory() as gecici:
        girdi = Path(gecici) / "senaryolar.json"
        girdi.write_text(json.dumps(senaryolar(), ensure_ascii=False), encoding="utf-8")
        komut = ["node", str(NODE_BETIGI), str(girdi), str(cikti or gecici), "1" if goruntu else "0"]
        sonuc = subprocess.run(komut, capture_output=True, text=True, timeout=180)
        if sonuc.returncode:
            raise RuntimeError(sonuc.stderr or sonuc.stdout)
        return json.loads(sonuc.stdout)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cikti", type=Path)
    ap.add_argument("--goruntu", action="store_true")
    a = ap.parse_args()
    if a.cikti:
        a.cikti.mkdir(parents=True, exist_ok=True)
    rapor = calistir(a.cikti, a.goruntu)
    hata = 0
    for r in rapor:
        sorun = r["konsol_hatalari"] + [f"eksik öğe: {s}" for s in r["eksik_ogeler"]]
        if not r["alt_bilgi_gorunur"]:
            sorun.append("alt bilgi görünmüyor")
        print(f"{'tamam' if not sorun else 'SORUN':6} {r['ad']:20} {r['tema']:5} yükseklik={r['yukseklik']}")
        for s in sorun:
            print(f"         - {s}")
        hata += bool(sorun)
    return 1 if hata else 0


if __name__ == "__main__":
    raise SystemExit(main())
