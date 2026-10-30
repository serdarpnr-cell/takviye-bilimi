"""Katalog doğrulamasında karantinaya düşen satırları Orzax web ve regülasyon ekibine bildirim için yazar.

Kullanım:
    python scripts/katalog_bulgulari.py

Çıktı: kurul/katalog_bulgulari.md. Katalog sitedeki haliyle kalır; düzeltme kaynak sayfada yapılır.
"""

from __future__ import annotations

import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
from server import veri  # noqa: E402

CIKTI = KOK / "kurul" / "katalog_bulgulari.md"

# Otomatik kontrolle yakalanmayan, testte elle görülen bulgular. Katalogda değiştirilmez, yalnızca bildirilir.
ELLE_BULGULAR = [
    ("ocean-methyl-b12", "Seri", "Ocean Methyl B12 (tablet) sitede 'Kadınlara Özel Takviyeler' serisinde; aynı ürünün "
     "sprey biçimleri 'Vitamin Serisi'nde. Seri sınıflaması gözden geçirilmeli (test bulgusu TB-17)."),
]


def main() -> int:
    satirlar = [
        "# Katalog bulguları · Orzax web ve regülasyon ekibine bildirim",
        "",
        f"Katalog erişim tarihi: {veri.katalog_tarihi()}. Bu dosya `scripts/katalog_bulgulari.py` ile üretilir.",
        "",
        "Aşağıdaki satırlar sunucuda karantinadadır: ürün kartında \"doğrulanamadı\" notuyla görünür, toplam ve "
        "üst sınır hesaplarına katılmaz. Katalog sitedeki haliyle tutulur; düzeltme ürün sayfasında yapılmalıdır.",
        "",
        "## Karantinadaki içerik satırları",
        "",
        "| Ürün | İçerik | Sitede | BRD | Gerekçe | Olası doğru birim |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    sayi = 0
    for u in veri.urunler():
        for e in u["etken_maddeler"]:
            k = e.get("karantina")
            if not k:
                continue
            sayi += 1
            satirlar.append(
                f"| [{u['ad']}]({u['kaynak']['url']}) | {e['etiketteki_ad']} | {e['miktar_metni']} | {e['brd'] or '–'} "
                f"| {k['gerekce']} | {k.get('olasi_birim', '–')} |"
            )
    satirlar += ["", f"Toplam: {sayi} satır.", "", "## Elle görülen bulgular", "",
                 "| Ürün | Alan | Gözlem |", "| --- | --- | --- |"]
    adlar = {u["id"]: u for u in veri.urunler()}
    for uid, alan, gozlem in ELLE_BULGULAR:
        u = adlar[uid]
        satirlar.append(f"| [{u['ad']}]({u['kaynak']['url']}) | {alan} | {gozlem} |")
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    print(f"{sayi} karantina satırı yazıldı: {CIKTI.relative_to(KOK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
