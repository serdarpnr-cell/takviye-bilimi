"""Medikal kurul "ikinci göz" (v0.4 C2): tohumlu rastgele kart örneklemi, kör değerlendirme formu, Cohen's kappa.

Kullanım:
    python scripts/ikinci_goz.py orneklem [--tohum 20261030] [--oran 0.10]
        → kurul/ikinci_goz_orneklem.json ve kurul/ikinci_goz_formu.html
    python scripts/ikinci_goz.py kappa kurul/ikinci_goz_uyusma.csv
        → uyuşma tablosu ve Cohen's kappa (kanıt düzeyi için)

Form kördür: değerlendirici kartın mevcut kanıt düzeyini ve sonuç yönünü görmez; yalnızca soruyu, popülasyonu ve
kaynakları görür ve düzeyi kaynaklardan yeniden türetir. Bu adım insan gerektirir: geliştirmenin (AI) değerlendirmesi
"ikinci göz" yerine geçmez.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import random
import sys
from collections import Counter
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))

from server import veri  # noqa: E402

DUZEYLER = ["guclu", "orta", "zayif", "yetersiz"]
YONLER = ["fayda", "etkisiz", "zarar", "belirsiz"]


def tum_kartlar() -> list[dict]:
    return [k for em in veri.kanit_tabani_kimlikleri() for k in veri._monografiler()[em]["kartlar"]]


def orneklem(tohum: int, oran: float) -> list[dict]:
    kartlar = sorted(tum_kartlar(), key=lambda k: k["id"])
    n = max(1, math.ceil(len(kartlar) * oran))
    return random.Random(tohum).sample(kartlar, n)


def _kaynak_satiri(kid: str) -> str:
    k = veri.kaynak_kayitlari()[kid]
    g = veri._kaynak_gorunumu(k)
    return (f'<li><a href="{html.escape(g["url"])}">{html.escape(k["baslik"])}</a> '
            f'({html.escape(k["kurum_veya_dergi"])}, {k.get("yil") or "–"}{", PMID " + k["pmid"] if k.get("pmid") else ""})</li>')


def form_html(secilen: list[dict], tohum: int, toplam: int) -> str:
    bloklar = []
    for i, k in enumerate(secilen, 1):
        secim = lambda ad, liste: "".join(f'<label><input type="radio" name="{ad}_{i}" value="{d}"> {d}</label> ' for d in liste)  # noqa: E731
        bloklar.append(f"""<section class="kart"><h2>{i}. {html.escape(k['id'])}</h2>
<p><b>Soru:</b> {html.escape(k['soru'])}</p><p><b>Popülasyon:</b> {html.escape(k['populasyon'])}</p>
<p><b>Kaynaklar</b> (düzeyi yalnızca bunlardan türetin):</p><ul>{''.join(_kaynak_satiri(x) for x in k['kaynaklar'])}</ul>
<p><b>Kanıt düzeyi:</b> {secim('duzey', DUZEYLER)}</p><p><b>Sonuç yönü:</b> {secim('yon', YONLER)}</p>
<p><b>100 kişide mutlak fark</b> (hangi tablo/şekil):<br><textarea rows="2"></textarea></p>
<p><b>Gerekçe (tek cümle):</b><br><textarea rows="2"></textarea></p></section>""")
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>İkinci göz formu</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;max-width:860px;margin:24px auto;padding:0 16px;color:#1c1f24}}
.kart{{border:1px solid #dfe3e8;border-radius:10px;padding:12px 16px;margin:12px 0}}textarea{{width:100%;font:inherit}}
label{{margin-right:12px}}table{{border-collapse:collapse}}td,th{{border:1px solid #dfe3e8;padding:4px 8px}}</style></head><body>
<h1>Medikal kurul · ikinci göz formu</h1>
<p>Oluşturma: {date.today().isoformat()} · Tohum (seed): <b>{tohum}</b> · Örneklem: {len(secilen)} / {toplam} kart (%10, yukarı yuvarlanmış).</p>
<p><b>Kör değerlendirme.</b> Kartın mevcut kanıt düzeyi ve sonuç yönü bu formda gösterilmez. Düzeyi kaynakları okuyarak
<code>docs/KANIT_PROTOKOLU.md</code> Bölüm 4'teki ölçeğe göre yeniden türetin. Değerlendirici adı ve tarih:
<input size="30"> · <input size="12"></p>
{''.join(bloklar)}
<h2>Uyuşma tablosu ve Cohen's kappa</h2>
<p>Her kart için kartın düzeyi (A) ve sizin düzeyiniz (B) <code>kurul/ikinci_goz_uyusma.csv</code> dosyasına yazılır
(sütunlar: <code>kart_id,degerlendirici_a,degerlendirici_b</code>). Hesap: <code>python scripts/ikinci_goz.py kappa kurul/ikinci_goz_uyusma.csv</code>.</p>
<p>κ = (p<sub>o</sub> − p<sub>e</sub>) / (1 − p<sub>e</sub>); p<sub>o</sub> gözlenen uyuşma oranı, p<sub>e</sub> = Σ (A'nın k oranı × B'nin k oranı).
Küçük örneklemde κ kararsızdır; kart sayısı arttıkça yeniden hesaplanır.</p>
</body></html>
"""


def kappa(yol: Path) -> str:
    satirlar = list(csv.DictReader(yol.open(encoding="utf-8")))
    ciftler = [(r["degerlendirici_a"].strip(), r["degerlendirici_b"].strip()) for r in satirlar if r["degerlendirici_b"].strip()]
    if not ciftler:
        return "Değerlendirme girilmemiş."
    n = len(ciftler)
    kat = sorted({x for c in ciftler for x in c}, key=lambda d: DUZEYLER.index(d) if d in DUZEYLER else 99)
    tablo = Counter(ciftler)
    po = sum(a == b for a, b in ciftler) / n
    pa, pb = Counter(a for a, _ in ciftler), Counter(b for _, b in ciftler)
    pe = sum(pa[k] / n * pb[k] / n for k in kat)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    cikti = ["Uyuşma tablosu (satır: A = kart, sütun: B = ikinci göz)", "| A \\ B | " + " | ".join(kat) + " |",
             "|---" * (len(kat) + 1) + "|"]
    cikti += [f"| {a} | " + " | ".join(str(tablo[(a, b)]) for b in kat) + " |" for a in kat]
    cikti += ["", f"n = {n}, p_o = {po:.3f}, p_e = {pe:.3f}, Cohen's κ = {k:.3f}"]
    return "\n".join(cikti)


def main() -> int:
    ap = argparse.ArgumentParser()
    alt = ap.add_subparsers(dest="komut", required=True)
    o = alt.add_parser("orneklem")
    o.add_argument("--tohum", type=int, default=20261030)
    o.add_argument("--oran", type=float, default=0.10)
    kp = alt.add_parser("kappa")
    kp.add_argument("csv", type=Path)
    a = ap.parse_args()
    if a.komut == "kappa":
        print(kappa(a.csv))
        return 0
    secilen = orneklem(a.tohum, a.oran)
    toplam = len(tum_kartlar())
    (KOK / "kurul" / "ikinci_goz_orneklem.json").write_text(json.dumps({
        "tohum": a.tohum, "oran": a.oran, "toplam_kart": toplam, "tarih": date.today().isoformat(),
        "secilen_kartlar": [k["id"] for k in secilen]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "kurul" / "ikinci_goz_formu.html").write_text(form_html(secilen, a.tohum, toplam), encoding="utf-8")
    with (KOK / "kurul" / "ikinci_goz_uyusma.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kart_id", "degerlendirici_a", "degerlendirici_b"])
        for k in secilen:
            w.writerow([k["id"], k["kanit_duzeyi"], ""])
    print(f"{len(secilen)}/{toplam} kart, tohum {a.tohum}: {[k['id'] for k in secilen]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
