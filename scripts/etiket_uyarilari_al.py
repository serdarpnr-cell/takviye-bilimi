"""TB-24 etiket uyarılarını içe aktarır (v0.4 C5).

Kullanım:
    python scripts/etiket_uyarilari_al.py <orzax_csv> [--yaz]

CSV sütunları (data/etiket_uyarilari/sablon.csv): urun_kodu, urun_adi, uyari_metni_birebir, ambalaj_revizyon_no, tarih.
Doğrulama: ürün kodu katalogda olmalı ve adı katalogdakiyle eşleşmeli; uyarı metni boş olmamalı (birebir saklanır,
düzeltilmez); revizyon numarası dolu; tarih YYYY-AA-GG ve bugünden ileri değil; aynı ürün + revizyonda aynı uyarı iki
kez yok. Hata varsa hiçbir şey yazılmaz ve 1 ile çıkılır. --yaz verilmezse yalnızca denetler.
Çıktı: data/etiket_uyarilari/uyarilar.json (sunucu, ürün kartında "ambalajı okuyun" notu yerine bu metni gösterir).
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "scripts"))

from json_yaz import yaz  # noqa: E402
from server import veri  # noqa: E402

SUTUNLAR = ["urun_kodu", "urun_adi", "uyari_metni_birebir", "ambalaj_revizyon_no", "tarih"]
CIKTI = KOK / "data" / "etiket_uyarilari" / "uyarilar.json"


def denetle(satirlar: list[dict], bugun: date | None = None) -> tuple[dict, list[str]]:
    bugun = bugun or date.today()
    urunler = {u["id"]: u for u in veri.urunler()}
    hatalar, sonuc, gorulen = [], {}, set()
    for i, r in enumerate(satirlar, start=2):
        kod = (r.get("urun_kodu") or "").strip()
        u = urunler.get(kod)
        if u is None:
            hatalar.append(f"satır {i}: '{kod}' katalogda yok")
            continue
        if veri.normalize(r.get("urun_adi") or "") != veri.normalize(u.get("ad_sitede", u["ad"])) and \
                veri.normalize(r.get("urun_adi") or "") != veri.normalize(u["ad"]):
            hatalar.append(f"satır {i}: ad '{r.get('urun_adi')}' katalogdaki '{u['ad']}' ile eşleşmiyor")
        metin = r.get("uyari_metni_birebir") or ""
        if not metin.strip():
            hatalar.append(f"satır {i}: uyarı metni boş")
        rev = (r.get("ambalaj_revizyon_no") or "").strip()
        if not rev:
            hatalar.append(f"satır {i}: ambalaj revizyon numarası boş")
        try:
            t = date.fromisoformat((r.get("tarih") or "").strip())
            if t > bugun:
                hatalar.append(f"satır {i}: tarih ileri bir gün ({t})")
        except ValueError:
            hatalar.append(f"satır {i}: tarih YYYY-AA-GG değil ('{r.get('tarih')}')")
            t = None
        anahtar = (kod, rev, metin.strip())
        if anahtar in gorulen:
            hatalar.append(f"satır {i}: aynı uyarı tekrar ediyor")
        gorulen.add(anahtar)
        kayit = sonuc.setdefault(kod, {"urun_adi": u["ad"], "ambalaj_revizyon_no": rev, "tarih": str(t), "uyarilar": []})
        kayit["uyarilar"].append(metin)  # birebir: boşluk ve noktalama korunur
    return sonuc, hatalar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--yaz", action="store_true")
    a = ap.parse_args()
    with a.csv.open(encoding="utf-8-sig", newline="") as f:
        okuyucu = csv.DictReader(f)
        if okuyucu.fieldnames != SUTUNLAR:
            print(f"Sütunlar {okuyucu.fieldnames}; beklenen {SUTUNLAR}", file=sys.stderr)
            return 1
        satirlar = list(okuyucu)
    sonuc, hatalar = denetle(satirlar)
    for h in hatalar:
        print(h, file=sys.stderr)
    if hatalar:
        return 1
    print(f"{len(satirlar)} satır, {len(sonuc)} ürün geçerli.")
    if a.yaz:
        yaz(CIKTI, {"_not": "Orzax'tan gelen ambalaj etiket uyarıları (TB-24); metinler birebir. scripts/etiket_uyarilari_al.py ile üretilir.",
                    "urunler": dict(sorted(sonuc.items()))})
        print(CIKTI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
