"""MCP Apps arayüzleri (ui:// kaynakları). Sayfalar dış kaynak yüklemez; çalışma anında dışarıdan içerik çekilmez."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .araclar import SORULAR

DIZIN = Path(__file__).resolve().parent / "arayuz"

# Her görsel kartın sabit alt bilgisi (TB-06). Marka notu modele bırakılmaz; kartın kendi HTML'inde durur.
ALT_BILGI_METNI = "Takviye Bilimi · Orzax tarafından geliştirildi · Kaynaklar · Prototip"
_ALT_BILGI_STILI = (
    "<style>.alt-bilgi { margin-top: 20px; padding-top: 10px; border-top: 1px solid var(--cizgi); "
    "color: var(--ikincil); font-size: 12px; }</style>"
)
_ALT_BILGI = (
    '<footer class="alt-bilgi" id="alt-bilgi">Takviye Bilimi · Orzax tarafından geliştirildi · '
    '<a href="#kaynaklar">Kaynaklar</a> · Prototip</footer>'
)


def _sayfa(ad: str, **yer_tutucular: str) -> str:
    """ui:// sayfasını okur, yer tutucuları doldurur ve sabit alt bilgiyi <main> sonrasına ekler."""
    html = (DIZIN / ad).read_text(encoding="utf-8")
    for anahtar, deger in yer_tutucular.items():
        html = html.replace(f"__{anahtar}__", deger)
    return html.replace("</head>", _ALT_BILGI_STILI + "\n</head>", 1).replace("</main>", "</main>\n" + _ALT_BILGI, 1)


@lru_cache(maxsize=1)
def karne_html() -> str:
    """Karne formu. Sorular ve seçenek kodları sunucudaki SORULAR listesinden gömülür."""
    sorular = json.dumps(SORULAR, ensure_ascii=False).replace("</", "<\\/")
    return _sayfa("karne.html", SORULAR=sorular)
