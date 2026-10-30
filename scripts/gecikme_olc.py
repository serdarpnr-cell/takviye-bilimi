"""Gecikme ölçümü (v0.4 A3): soğuk başlangıç, araç başına tools/call ve kart başına resources/read p50/p95.

Kullanım:
    python scripts/gecikme_olc.py --url https://<render-adresi>/mcp [--tekrar 20] [--soguk-bekle-dk 15]

--soguk-bekle-dk verilirse betik önce o kadar boşta bekler (Render ücretsiz plan ~15 dk sonra uyur), sonra ilk
isteğin süresini soğuk başlangıç olarak yazar. Bütçe: sıcakken tools/call + resources/read p95 < 1,5 sn.
Soğuk başlangıç 3 sn'yi aşarsa rapora seçenekler yazılır; karar Serdar'da, betik keep-warm kurmaz.
Çıktı: docs/olcumler/<tarih>_gecikme.md
"""

from __future__ import annotations

import argparse
import asyncio
import time
from datetime import date
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

KOK = Path(__file__).resolve().parent.parent
BUTCE_SN = 1.5
SOGUK_SINIR_SN = 3.0
# Her araç için temsilî bir çağrı (test personası; kişisel veri yok).
CAGRILAR = {
    "takviye_rehberi": {"konu": "Kış geldi, hangi vitaminler?"},
    "sikayet_yolu": {"sikayet": "hep yorgunum", "yas": 40},
    "parti_analizi": {"karekod_veya_parti_no": "DEMO-0001"},
    "etken_madde_rehberi": {"etken_madde": "D vitamini", "yas": 40},
    "urun_rehberi": {"urun": "Ocean Vitamin D3 400 IU Sprey", "yas": 8},
    "karsilastir": {"etken_madde": "D vitamini"},
    "kisisel_rutin": {"yas": 58, "cinsiyet": "kadin", "ilac_grubu": ["kan_sulandirici_varfarin"],
                      "mevcut_urunler": ["Ocean D3K2 Damla"]},
    "yasam_karnesi": {},
    "tahlil_goster": {"tahlil": "ferritin"},
}


def yuzdelik(d: list[float], p: float) -> float:
    s = sorted(d)
    return s[min(len(s) - 1, round(p / 100 * (len(s) - 1)))]


async def olc(url: str, tekrar: int, soguk_bekle_dk: float) -> dict:
    sonuc: dict = {"soguk_sn": None, "araclar": {}, "kartlar": {}}
    if soguk_bekle_dk:
        await asyncio.sleep(soguk_bekle_dk * 60)
    async with httpx.AsyncClient(timeout=120) as istemci:
        bas = time.perf_counter()
        async with streamable_http_client(url, http_client=istemci) as (oku, yaz, _):
            async with ClientSession(oku, yaz) as oturum:
                await oturum.initialize()
                ilk = time.perf_counter() - bas
                if soguk_bekle_dk:
                    sonuc["soguk_sn"] = round(ilk, 2)
                araclar = {t.name for t in (await oturum.list_tools()).tools}
                kaynaklar = [r for r in (await oturum.list_resources()).resources if str(r.uri).startswith("ui://")]
                for _ in range(2):  # ısınma
                    await oturum.call_tool("etken_madde_rehberi", CAGRILAR["etken_madde_rehberi"])
                for ad, arg in CAGRILAR.items():
                    if ad not in araclar:
                        continue
                    sureler = []
                    for _ in range(tekrar):
                        t0 = time.perf_counter()
                        await oturum.call_tool(ad, arg)
                        sureler.append(time.perf_counter() - t0)
                    sonuc["araclar"][ad] = {"p50": yuzdelik(sureler, 50), "p95": yuzdelik(sureler, 95)}
                for r in kaynaklar:
                    sureler, boyut = [], 0
                    for _ in range(tekrar):
                        t0 = time.perf_counter()
                        icerik = await oturum.read_resource(r.uri)
                        sureler.append(time.perf_counter() - t0)
                        boyut = len(icerik.contents[0].text.encode("utf-8"))
                    sonuc["kartlar"][str(r.uri)] = {"p50": yuzdelik(sureler, 50), "p95": yuzdelik(sureler, 95),
                                                    "kb": round(boyut / 1024, 1), "mime": icerik.contents[0].mimeType}
    return sonuc


def rapor(url: str, s: dict, tekrar: int) -> str:
    ms = lambda x: f"{x * 1000:.0f} ms"  # noqa: E731
    kart_p95 = max((k["p95"] for k in s["kartlar"].values()), default=0)
    satirlar = [f"# Gecikme ölçümü · {date.today().isoformat()}", "", f"Sunucu: `{url}` · Tekrar: {tekrar}", "",
                f"Bütçe: sıcakken tools/call p95 + resources/read p95 < {BUTCE_SN} sn (\"ilk kart < 3 sn\" hedefine host çizimi için pay).", "",
                "## Araçlar (tools/call)", "", "| Araç | p50 | p95 | p95 + en yavaş kart p95 | Bütçe |", "|---|---|---|---|---|"]
    for ad, v in s["araclar"].items():
        toplam = v["p95"] + kart_p95
        satirlar.append(f"| {ad} | {ms(v['p50'])} | {ms(v['p95'])} | {ms(toplam)} | {'içinde' if toplam < BUTCE_SN else 'AŞIYOR'} |")
    satirlar += ["", "## Kartlar (resources/read)", "", "| Kart | p50 | p95 | HTML boyutu | mimeType |", "|---|---|---|---|---|"]
    satirlar += [f"| {u} | {ms(v['p50'])} | {ms(v['p95'])} | {v['kb']} KB | {v['mime']} |" for u, v in s["kartlar"].items()]
    satirlar += ["", "## Soğuk başlangıç", ""]
    if s["soguk_sn"] is None:
        satirlar.append("Ölçülmedi (`--soguk-bekle-dk 15` ile koşun).")
    else:
        satirlar.append(f"15+ dk boşta bekledikten sonraki ilk istek: **{s['soguk_sn']} sn**.")
        if s["soguk_sn"] > SOGUK_SINIR_SN:
            satirlar += ["", f"{SOGUK_SINIR_SN} sn'yi aşıyor. Seçenekler (karar Serdar'da; keep-warm kurulmadı):", "",
                         "- Render ücretli plan (uyku yok): en basit çözüm, aylık sabit ücret.",
                         "- Dışarıdan düzenli sıcak tutma isteği: ücretsiz ama Render koşullarıyla çelişebilir, yine de ilk istek garantisi yok.",
                         "- Bölge: kullanıcıya (Türkiye) yakın bölge (ör. Frankfurt) ağ gecikmesini düşürür; soğuk başlangıcı çözmez."]
    return "\n".join(satirlar) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--tekrar", type=int, default=20)
    ap.add_argument("--soguk-bekle-dk", type=float, default=0)
    ap.add_argument("--cikti", type=Path, default=KOK / "docs" / "olcumler" / f"{date.today().isoformat()}_gecikme.md")
    a = ap.parse_args()
    s = asyncio.run(olc(a.url, a.tekrar, a.soguk_bekle_dk))
    a.cikti.write_text(rapor(a.url, s, a.tekrar), encoding="utf-8")
    print(a.cikti)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
