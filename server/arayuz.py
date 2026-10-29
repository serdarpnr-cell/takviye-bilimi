"""MCP Apps arayüzleri (ui:// kaynakları). Sayfalar dış kaynak yüklemez; çalışma anında dışarıdan içerik çekilmez."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .araclar import SORULAR

DIZIN = Path(__file__).resolve().parent / "arayuz"


@lru_cache(maxsize=1)
def karne_html() -> str:
    """Karne formu. Sorular ve seçenek kodları sunucudaki SORULAR listesinden gömülür."""
    sorular = json.dumps(SORULAR, ensure_ascii=False).replace("</", "<\\/")
    return (DIZIN / "karne.html").read_text(encoding="utf-8").replace("__SORULAR__", sorular)
