"""Parti analizlerini içe aktarır (v0.4 C7).

Kullanım:
    python scripts/parti_analizi_al.py <kalite_csv> [--yaz]

CSV (data/parti_analizleri/sablon.csv): her satır bir partinin bir etken madde sonucudur.
Sütunlar: parti_no, urun_kodu, laboratuvar, akreditasyon_no, analiz_tarihi, rapor_no, etken_madde, etiketteki,
olculen, birim, yontem, yayin_onaylayan, yayin_onay_tarihi.

Doğrulama: ürün kodu katalogda; etken madde kural tablosunda ve o üründe var; etiketteki miktar katalogdaki porsiyon
miktarıyla (standart birimde) %1 içinde; ölçülen sayı ve ≥ 0; birim maddenin standart birimi; tarihler YYYY-AA-GG,
ileri değil, onay tarihi analizden önce değil; yayın onayı (ad ve tarih) dolu. Onaysız satır yayımlanmaz.
Hata varsa hiçbir şey yazılmaz. Geçerli kayıtlar data/parti_analizleri.json'a 'demo: false' olarak eklenir;
DEMO-0001 gösterim kaydı korunur.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "scripts"))

from json_yaz import yaz  # noqa: E402
from server import veri  # noqa: E402

SUTUNLAR = ["parti_no", "urun_kodu", "laboratuvar", "akreditasyon_no", "analiz_tarihi", "rapor_no", "etken_madde",
            "etiketteki", "olculen", "birim", "yontem", "yayin_onaylayan", "yayin_onay_tarihi"]
HEDEF = KOK / "data" / "parti_analizleri.json"
SEMA = KOK / "data" / "parti_analizleri" / "parti_analizi.schema.json"


def _tarih(metin: str, alan: str, i: int, bugun: date, hatalar: list[str]) -> date | None:
    try:
        t = date.fromisoformat(metin.strip())
    except ValueError:
        hatalar.append(f"satır {i}: {alan} YYYY-AA-GG değil ('{metin}')")
        return None
    if t > bugun:
        hatalar.append(f"satır {i}: {alan} ileri bir gün")
    return t


def denetle(satirlar: list[dict], bugun: date | None = None) -> tuple[list[dict], list[str]]:
    bugun = bugun or date.today()
    urunler = {u["id"]: u for u in veri.urunler()}
    birimler = {k: v["birim"] for k, v in veri.kurallar()["etken_maddeler"].items()}
    partiler: dict[str, dict] = {}
    hatalar: list[str] = []
    for i, r in enumerate(satirlar, start=2):
        r = {k: (v or "").strip() for k, v in r.items()}
        u = urunler.get(r["urun_kodu"])
        if u is None:
            hatalar.append(f"satır {i}: ürün kodu '{r['urun_kodu']}' katalogda yok")
            continue
        em = veri.etken_madde_id(r["etken_madde"]) or r["etken_madde"]
        satir = next((e for e in u["etken_maddeler"] if e["etken_madde"] == em), None)
        if em not in birimler or satir is None:
            hatalar.append(f"satır {i}: '{r['etken_madde']}' bu üründe tanımlı bir etken madde değil")
            continue
        if r["birim"] != birimler[em]:
            hatalar.append(f"satır {i}: birim '{r['birim']}', beklenen {birimler[em]}")
        try:
            etiketteki, olculen = float(r["etiketteki"].replace(",", ".")), float(r["olculen"].replace(",", "."))
        except ValueError:
            hatalar.append(f"satır {i}: etiketteki/ölçülen sayı değil")
            continue
        if olculen < 0:
            hatalar.append(f"satır {i}: ölçülen negatif")
        katalog = veri.satir_miktari(satir)
        if katalog is not None and abs(etiketteki - katalog) > 0.01 * katalog:
            hatalar.append(f"satır {i}: etiketteki {etiketteki} katalogdaki {katalog} {birimler[em]} ile uyuşmuyor")
        analiz = _tarih(r["analiz_tarihi"], "analiz_tarihi", i, bugun, hatalar)
        if not r["yayin_onaylayan"] or not r["yayin_onay_tarihi"]:
            hatalar.append(f"satır {i}: yayın onayı (ad ve tarih) eksik; onaysız analiz yayımlanmaz")
        else:
            onay = _tarih(r["yayin_onay_tarihi"], "yayin_onay_tarihi", i, bugun, hatalar)
            if onay and analiz and onay < analiz:
                hatalar.append(f"satır {i}: yayın onayı analizden önce")
        for alan in ("parti_no", "laboratuvar", "rapor_no"):
            if not r[alan]:
                hatalar.append(f"satır {i}: {alan} boş")
        p = partiler.setdefault(r["parti_no"], {
            "parti_no": r["parti_no"], "demo": False, "urun_id": u["id"], "laboratuvar": r["laboratuvar"],
            "akreditasyon_no": r["akreditasyon_no"] or None, "analiz_tarihi": r["analiz_tarihi"], "rapor_no": r["rapor_no"],
            "yayin_onayi": {"onaylayan": r["yayin_onaylayan"], "tarih": r["yayin_onay_tarihi"]}, "sonuclar": []})
        if p["urun_id"] != u["id"]:
            hatalar.append(f"satır {i}: parti {r['parti_no']} iki farklı ürüne bağlı")
        if any(s["etken_madde"] == em for s in p["sonuclar"]):
            hatalar.append(f"satır {i}: parti {r['parti_no']} için {em} iki kez")
        p["sonuclar"].append({"etken_madde": em, "etiketteki": etiketteki, "olculen": olculen, "birim": r["birim"],
                              "yontem": r["yontem"] or None})
    return list(partiler.values()), hatalar


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
    partiler, hatalar = denetle(satirlar)
    mevcut = json.loads(HEDEF.read_text(encoding="utf-8"))
    eski = {p["parti_no"].casefold() for p in mevcut["partiler"]}
    hatalar += [f"parti {p['parti_no']} zaten yayımlanmış" for p in partiler if p["parti_no"].casefold() in eski]
    for h in hatalar:
        print(h, file=sys.stderr)
    if hatalar:
        return 1
    print(f"{len(partiler)} parti geçerli.")
    if a.yaz:
        mevcut["partiler"] += partiler
        yaz(HEDEF, mevcut)
        print(HEDEF)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
