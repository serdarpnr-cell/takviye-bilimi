"""Yasaklı ifade denetimi (CLAUDE.md, "Yasaklı ifadeler").

Bulunan ifade içeriği otomatik reddetmez; insan incelemesine düşürür.

Kullanım:
    python scripts/lint_ifadeler.py <dosya> ...   # bulguları yazar, bulgu varsa 1 ile çıkar
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# "hastalığı önler" ve "kanıtlanmıştır" bağlama bağlıdır (onaylı risk azaltma beyanı, tek çalışma);
# bu yüzden her geçişte insan bakar.
YASAKLI = [
    r"tedavi eder", r"iyileştirir", r"şifa", r"mucize", r"garanti", r"kesin sonuç", r"%\s?100\b",
    r"hastalığı önler", r"kanıtlanmıştır", r"en iyi", r"\bresm[iî]\b", r"bir numara",
    r"doktora gerek yok", r"ilaç yerine",
]


def bul(metin: str) -> list[dict]:
    """Metindeki yasaklı ifadeleri bağlamıyla döndürür."""
    kucuk = metin.casefold()
    bulgular = []
    for desen in YASAKLI:
        for m in re.finditer(desen, kucuk):
            bulgular.append({"ifade": m.group(0), "baglam": metin[max(0, m.start() - 60):m.end() + 60].strip()})
    return bulgular


if __name__ == "__main__":
    toplam = 0
    for yol in sys.argv[1:]:
        for b in bul(Path(yol).read_text(encoding="utf-8")):
            toplam += 1
            print(f"{yol}: '{b['ifade']}' … {b['baglam']}")
    raise SystemExit(1 if toplam else 0)
