"""Sunucu yanıt süresini ve modele dönen yanıtın boyutunu ölçer.

Kullanım:
    python scripts/olcum.py [--tekrar 20] [--etiket once]

Sunucuyu gerçek HTTP üzerinden (Streamable HTTP, /mcp) ayrı bir süreçte başlatır ve test senaryolarını
(docs/olcumler/ altındaki raporlarda listelenir) art arda çağırır. Her senaryo için p50 ve p95 süre ile
modele dönen metnin karakter sayısı ve yaklaşık token sayısı yazılır.

Token sayısı kaba tahmindir: karakter / 3 (Türkçe için temkinli). Ölçülen, modele giden metin içeriğidir;
görsel karta giden structuredContent ayrıca karakter olarak raporlanır.
Sonuç docs/olcumler/<tarih>_<etiket>.md dosyasına yazılır. Kişisel veri yoktur; senaryolar test personasıdır.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import datetime as dt
import os
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

KOK = Path(__file__).resolve().parent.parent
CIKTI = KOK / "docs" / "olcumler"

# Test bulgularındaki 11 senaryo. Doğal sorular (10, 11) modelin yaptığı çağrılarla temsil edilir.
SENARYOLAR: list[tuple[str, str, list[tuple[str, dict]]]] = [
    ("1", "Karne, cevapsız", [("yasam_karnesi", {})]),
    ("2", "Karne, seçenek koduyla, 45 yaş", [("yasam_karnesi", {"yas": 45, "cevaplar": {
        "hareket_gun": "1_2_gun", "uyku_saat": "6_7_saat", "sebze_meyve_porsiyon": "0_2_porsiyon",
        "balik_haftalik": "haftada_1", "sigara": "hayir", "stres": "sik"}})]),
    ("3", "Karne, sayılarla", [("yasam_karnesi", {"cevaplar": {
        "hareket_gun": 3, "uyku_saat": 7, "sebze_meyve_porsiyon": 4, "balik_haftalik": 1,
        "sigara": "hayir", "stres": "bazen"}})]),
    ("4", "Ürün: Ocean D3K2 Damla", [("urun_rehberi", {"urun": "Ocean D3K2 Damla"})]),
    ("5", "Rutin: 58 yaş kadın, varfarin, D3K2 + multivitamin", [("kisisel_rutin", {
        "yas": 58, "cinsiyet": "kadin", "ilac_grubu": ["kan_sulandirici_varfarin"],
        "mevcut_urunler": ["Ocean D3K2 Damla"],
        "diger_urun_icerikleri": [{"ad": "Multivitamin", "icerikler": [
            {"etken_madde": "D vitamini", "miktar": 2000, "birim": "IU"}]}]})]),
    ("6", "Parti: L2410A17", [("parti_analizi", {"karekod_veya_parti_no": "L2410A17"})]),
    ("6b", "Parti: DEMO-0001 (demo kart)", [("parti_analizi", {"karekod_veya_parti_no": "DEMO-0001"})]),
    ("7", "Etken madde: omega-3", [("etken_madde_rehberi", {"etken_madde": "omega-3"})]),
    ("8", "Etken madde: D vitamini, 42 yaş erkek", [("etken_madde_rehberi", {
        "etken_madde": "D vitamini", "yas": 42, "cinsiyet": "erkek"})]),
    ("9", "Rutin: Collagen Mag Plus", [("kisisel_rutin", {
        "yas": 40, "cinsiyet": "kadin", "mevcut_urunler": ["Day2Day The Collagen Mag Plus"]})]),
    ("10", "\"Yorgunum\": sikayet_yolu (v2 yolu)", [("sikayet_yolu", {"sikayet": "Kendimi yorgun hissediyorum"})]),
    ("10b", "\"Yorgunum\": eski yol, B12 + demir + magnezyum", [
        ("etken_madde_rehberi", {"etken_madde": "B12"}),
        ("etken_madde_rehberi", {"etken_madde": "demir"}),
        ("etken_madde_rehberi", {"etken_madde": "magnezyum"})]),
    ("11", "\"En güçlü B12\"", [("etken_madde_rehberi", {"etken_madde": "B12"})]),
    ("12", "Kıyas: magnezyum ürünleri", [("karsilastir", {"etken_madde": "magnezyum"})]),
    ("14", "Takviye rehberi: kış", [("takviye_rehberi", {"konu": "Kış geldi, hangi vitaminler?"})]),
    ("13", "Tahlil görünümü: ferritin", [("tahlil_goster", {"tahlil": "ferritin"})]),
]


def _bos_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _yuzdelik(degerler: list[float], p: float) -> float:
    s = sorted(degerler)
    return s[min(len(s) - 1, round(p / 100 * (len(s) - 1)))]


async def _olc(url: str, tekrar: int) -> list[dict]:
    sonuclar = []
    async with httpx.AsyncClient(trust_env=False, timeout=60) as istemci:
        async with streamable_http_client(url, http_client=istemci) as (oku, yaz, _):
            async with ClientSession(oku, yaz) as oturum:
                await oturum.initialize()
                for no, ad, cagrilar in SENARYOLAR:
                    sureler, karakter, kart = [], 0, 0
                    for i in range(tekrar + 1):
                        bas = time.perf_counter()
                        karakter = kart = 0
                        for arac, arg in cagrilar:
                            yanit = await oturum.call_tool(arac, arg)
                            if yanit.isError:
                                raise RuntimeError(f"{no} {arac}: {yanit.content}")
                            karakter += sum(len(c.text) for c in yanit.content if c.type == "text")
                            kart += len(json.dumps(yanit.structuredContent or {}, ensure_ascii=False))
                        if i:  # İlk çağrı ısınmadır, ölçüme katılmaz.
                            sureler.append((time.perf_counter() - bas) * 1000)
                    sonuclar.append({"no": no, "ad": ad, "cagri": len(cagrilar), "p50": statistics.median(sureler),
                                     "p95": _yuzdelik(sureler, 95), "karakter": karakter, "token": karakter // 3, "kart": kart})
    return sonuclar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tekrar", type=int, default=20)
    ap.add_argument("--etiket", default="olcum")
    a = ap.parse_args()

    port = _bos_port()
    ortam = {**os.environ, "PORT": str(port), "TB_TASLAK_GOSTER": "1"}
    ortam.pop("TB_PORT", None)
    surec = subprocess.Popen([sys.executable, "-m", "server"], cwd=KOK, env=ortam,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        sonuclar = asyncio.run(_olc(f"http://127.0.0.1:{port}/mcp", a.tekrar))
    finally:
        surec.terminate()
        surec.wait(timeout=10)

    tum_p95 = _yuzdelik([s["p95"] for s in sonuclar], 95)
    satirlar = [
        f"# Ölçüm · {a.etiket} · {dt.date.today().isoformat()}",
        "",
        f"Yerel HTTP sunucusu (`TB_TASLAK_GOSTER=1`), senaryo başına {a.tekrar} tekrar, ilk çağrı ısınma olarak atıldı. "
        "Süre, senaryodaki tüm araç çağrılarının toplamıdır (ms). Token = modele giden metin karakteri / 3 (temkinli tahmin). "
        "Kart = görsel karta giden structuredContent karakteri (modelin bağlamına girmez).",
        "",
        "| # | Senaryo | Çağrı | p50 ms | p95 ms | Modele dönen karakter | ≈ token | Kart karakteri |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        *(f"| {s['no']} | {s['ad']} | {s['cagri']} | {s['p50']:.1f} | {s['p95']:.1f} | {s['karakter']:,} | {s['token']:,} | {s['kart']:,} |"
          for s in sonuclar),
        "",
        f"Senaryoların p95 değerleri arasında en yüksek dilim: {tum_p95:.1f} ms. "
        f"Modele dönen yanıt, senaryo p95'i: ≈ {_yuzdelik([s['token'] / s['cagri'] for s in sonuclar], 95):,.0f} token / çağrı. "
        f"1.500 token'ı aşan çağrı içeren senaryo: {sum(s['token'] / s['cagri'] > 1500 for s in sonuclar)} / {len(sonuclar)}.",
        "",
    ]
    CIKTI.mkdir(parents=True, exist_ok=True)
    dosya = CIKTI / f"{dt.date.today().isoformat()}_{a.etiket}.md"
    dosya.write_text("\n".join(satirlar), encoding="utf-8")
    print("\n".join(satirlar))
    print(f"Yazıldı: {dosya.relative_to(KOK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
