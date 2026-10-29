"""Veri dosyalarını okunur ve satır bazında karşılaştırılabilir biçimde yazar.

Kısa nesne ve listeler tek satıra sığdırılır; uzunlar girintili açılır.
"""

from __future__ import annotations

import json
from pathlib import Path

SATIR_SINIRI = 160


def bicimle(deger, girinti: int = 0) -> str:
    tek = json.dumps(deger, ensure_ascii=False)
    if len(tek) + girinti <= SATIR_SINIRI or not isinstance(deger, (dict, list)) or not deger:
        return tek
    ic = " " * (girinti + 2)
    if isinstance(deger, dict):
        parcalar = [f"{ic}{json.dumps(k, ensure_ascii=False)}: {bicimle(v, girinti + 2)}" for k, v in deger.items()]
        return "{\n" + ",\n".join(parcalar) + "\n" + " " * girinti + "}"
    parcalar = [f"{ic}{bicimle(v, girinti + 2)}" for v in deger]
    return "[\n" + ",\n".join(parcalar) + "\n" + " " * girinti + "]"


def yaz(yol: Path | str, veri) -> None:
    Path(yol).write_text(bicimle(veri) + "\n", encoding="utf-8")
