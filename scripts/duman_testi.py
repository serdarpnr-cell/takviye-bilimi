"""Yayın sonrası duman testi (v0.4 B2).

Kullanım:
    python scripts/duman_testi.py --url https://<render-adresi>/mcp [--cikti docs/olcumler/<tarih>_duman.md]

Denetimler: initialize yönergesi dolu; tools/list 8 v0.3 aracını ve ek açıklamalarını içeriyor; araç → kart eşlemesi
(kapı araçlarında _meta.ui varsa değiştirmeden raporlanır); her ui:// kaynağı okunuyor ve mimeType doğru; her araç
örnek çağrıda structuredContent ve kisa_ozet döndürüyor; kart HTML'lerinde src/href ile dış kaynak yüklemesi yok.
Hata varsa 1 ile çıkar.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from datetime import date
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gecikme_olc import CAGRILAR  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
V03_ARACLARI = ["takviye_rehberi", "sikayet_yolu", "parti_analizi", "etken_madde_rehberi", "urun_rehberi",
                "karsilastir", "kisisel_rutin", "yasam_karnesi"]
KAPI = {"takviye_rehberi", "sikayet_yolu", "parti_analizi"}
MIME = "text/html;profile=mcp-app"
DIS_KAYNAK = re.compile(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.I)


async def denetle(url: str) -> tuple[list[str], list[str], list[str]]:
    tamam, hata, notlar = [], [], []
    async with httpx.AsyncClient(timeout=120) as istemci:
        async with streamable_http_client(url, http_client=istemci) as (oku, yaz, _):
            async with ClientSession(oku, yaz) as oturum:
                ilk = await oturum.initialize()
                (tamam if (ilk.instructions or "").strip() else hata).append(
                    f"initialize instructions {'dolu' if ilk.instructions else 'BOŞ'} ({len(ilk.instructions or '')} karakter); "
                    f"serverInfo {ilk.serverInfo.name} {ilk.serverInfo.version}")
                araclar = {t.name: t for t in (await oturum.list_tools()).tools}
                eksik = [a for a in V03_ARACLARI if a not in araclar]
                (hata if eksik else tamam).append(f"tools/list: v0.3'ün 8 aracı {'eksik: ' + ', '.join(eksik) if eksik else 'var'}"
                                                  f" (toplam {len(araclar)} araç: {', '.join(sorted(araclar))})")
                for ad, t in araclar.items():
                    a = t.annotations
                    if not a or (a.readOnlyHint, a.destructiveHint, a.idempotentHint, a.openWorldHint) != (True, False, True, False) or not a.title:
                        hata.append(f"{ad}: annotations eksik ya da yanlış")
                tamam.append("annotations: tüm araçlarda title, readOnly, destructive=false, idempotent, openWorld=false"
                             if not any("annotations" in h for h in hata) else "annotations: sorunlu (yukarıda)")
                notlar += ["| Araç | Rol | Kart (_meta.ui) |", "|---|---|---|"]
                for ad, t in sorted(araclar.items()):
                    ui = ((t.meta or {}).get("ui") or {})
                    kart = ui.get("resourceUri") or ("yalnızca kart (modelden gizli)" if ui.get("visibility") == ["app"] else "yok")
                    rol = "kapı" if ad in KAPI else "derinlik" if ad in V03_ARACLARI else "ek"
                    notlar.append(f"| {ad} | {rol} | {kart} |")
                    if ad in KAPI and ui.get("resourceUri"):
                        notlar.append(f"| ⚠ | {ad} kapı aracı ama _meta.ui bağlı: v0.3 Bölüm 1 ile çelişki; değiştirilmedi, rapor edildi | |")
                kaynaklar = [r for r in (await oturum.list_resources()).resources if str(r.uri).startswith("ui://")]
                for r in kaynaklar:
                    try:
                        icerik = (await oturum.read_resource(r.uri)).contents[0]
                    except Exception as e:  # noqa: BLE001
                        hata.append(f"{r.uri}: okunamadı ({e})")
                        continue
                    if icerik.mimeType != MIME:
                        hata.append(f"{r.uri}: mimeType {icerik.mimeType}")
                    dis = DIS_KAYNAK.findall(icerik.text)
                    if dis:
                        hata.append(f"{r.uri}: dış kaynak yüklemesi {dis[:3]}")
                tamam.append(f"{len(kaynaklar)} ui:// kaynağı okundu; mimeType ve dış kaynak denetimi yapıldı")
                for ad, arg in CAGRILAR.items():
                    if ad not in araclar:
                        continue
                    s = await oturum.call_tool(ad, arg)
                    if s.isError or not (s.structuredContent or {}).get("kisa_ozet"):
                        hata.append(f"{ad}: örnek çağrıda structuredContent/kisa_ozet yok")
                tamam.append("örnek çağrılar: structuredContent ve kisa_ozet denetlendi")
    return tamam, hata, notlar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--cikti", type=Path, default=KOK / "docs" / "olcumler" / f"{date.today().isoformat()}_duman.md")
    a = ap.parse_args()
    tamam, hata, notlar = asyncio.run(denetle(a.url))
    metin = "\n".join([f"# Duman testi · {date.today().isoformat()}", "", f"Sunucu: `{a.url}`", "",
                       f"Sonuç: **{'GEÇTİ' if not hata else 'HATA VAR'}**", "", "## Geçenler", "", *[f"- {t}" for t in tamam],
                       "", "## Hatalar", "", *([f"- {h}" for h in hata] or ["- Yok."]), "", "## Kart eşlemesi", "", *notlar, ""])
    a.cikti.write_text(metin, encoding="utf-8")
    print(metin)
    return 1 if hata else 0


if __name__ == "__main__":
    raise SystemExit(main())
