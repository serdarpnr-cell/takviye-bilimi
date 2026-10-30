"""Tetiklenme ölçümü (v0.4 A2): doğal Türkçe mesaj ilk turda doğru Takviye Bilimi aracına düşüyor mu?

Kullanım:
    python scripts/tetiklenme_olc.py --url http://127.0.0.1:8000/mcp [--model claude-sonnet-5-5 --model claude-haiku-5-5]
                                     [--tekrar 3] [--set tests/tetiklenme/set_v1.jsonl] [--openai-model <ad>]

1. Sunucuya MCP istemcisiyle bağlanır; initialize yanıtından yönergeyi (instructions), tools/list'ten araçları alır.
2. Her mesajı Anthropic Messages API'ye tek tur olarak gönderir: system = sunucu yönergesi, tools = sunucu araçları +
   iki dikkat dağıtıcı genel araç (web araması, belge araması). İlk tool_use adını ve parametrelerini kaydeder.
3. Çıktı: tests/tetiklenme/sonuc_<tarih>_<model>.json ve tests/tetiklenme/rapor.md.

Sınırlama: Bu ölçüm açıklama düzeyindeki yönlendirmeyi ölçer. claude.ai'daki kartlı araç kısıtı (adı anılmadan ya da
seçilmeden doğrudan çağrılmama) burada yoktur; o kısıt docs/claude_canli_test.md ile elle ölçülür.

Anahtarlar yalnızca ortam değişkeninden okunur (ANTHROPIC_API_KEY, isteğe bağlı OPENAI_API_KEY); repoya yazılmaz.
Mesajlar test personasıdır; kişisel veri yoktur.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

KOK = Path(__file__).resolve().parent.parent
CIKTI = KOK / "tests" / "tetiklenme"
VARSAYILAN_MODELLER = ["claude-sonnet-5-5", "claude-haiku-5-5"]
YOK = "yok"
ESIK = 0.90

# claude.ai'da modelin elinde genel araçlar da olur; yönlendirmeyi gerçekçi kılmak için eklenir, hiç çalıştırılmaz.
DIKKAT_DAGITICILAR = [
    {"name": "web_search", "description": "Search the web for current information and return relevant results.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "drive_search", "description": "Search the user's connected documents and files.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
]

ANAHTAR_YOK = """ANTHROPIC_API_KEY tanımlı değil; ölçüm yapılamadı.
Tanımlamak için (anahtar repoya yazılmaz):
    export ANTHROPIC_API_KEY=sk-ant-...
ya da Anthropic CLI ile oturum açın: ant auth login
Python paketi gerekir: .venv/bin/pip install anthropic"""


async def sunucu_bilgisi(url: str) -> tuple[str, list[dict]]:
    async with httpx.AsyncClient(trust_env=False, timeout=60) as istemci:
        async with streamable_http_client(url, http_client=istemci) as (oku, yaz, _):
            async with ClientSession(oku, yaz) as oturum:
                ilk = await oturum.initialize()
                araclar = (await oturum.list_tools()).tools
    # Modelden gizli kart araçları (visibility: app) modele verilmez.
    gorunen = [t for t in araclar if ((t.meta or {}).get("ui") or {}).get("visibility") != ["app"]]
    return ilk.instructions or "", [{"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                                    for t in gorunen]


def vakalar(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def anthropic_cagir(istemci, model: str, sistem: str, araclar: list[dict], mesaj: str) -> tuple[str, dict, str]:
    """(ilk araç adı ya da 'yok', parametreler, durma nedeni). Zorunlu araç seçimi yok: tool_choice auto."""
    yanit = istemci.messages.create(
        model=model, max_tokens=4096, system=sistem, tools=araclar + DIKKAT_DAGITICILAR,
        tool_choice={"type": "auto"}, messages=[{"role": "user", "content": mesaj}],
    )
    ilk = next((b for b in yanit.content if b.type == "tool_use"), None)
    return (ilk.name, dict(ilk.input), yanit.stop_reason) if ilk else (YOK, {}, yanit.stop_reason)


def openai_cagir(model: str, sistem: str, araclar: list[dict], mesaj: str) -> tuple[str, dict, str]:
    """İsteğe bağlı ChatGPT ölçümü: aynı set, function calling. Model adı parametredir."""
    fonksiyonlar = [{"type": "function", "function": {"name": a["name"], "description": a["description"],
                                                      "parameters": a["input_schema"]}} for a in araclar + DIKKAT_DAGITICILAR]
    r = httpx.post("https://api.openai.com/v1/chat/completions", timeout=120,
                   headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                   json={"model": model, "tools": fonksiyonlar, "tool_choice": "auto",
                         "messages": [{"role": "system", "content": sistem}, {"role": "user", "content": mesaj}]})
    r.raise_for_status()
    secim = r.json()["choices"][0]
    cagrilar = secim["message"].get("tool_calls") or []
    if not cagrilar:
        return YOK, {}, secim.get("finish_reason", "")
    f = cagrilar[0]["function"]
    return f["name"], json.loads(f["arguments"] or "{}"), secim.get("finish_reason", "")


def dogru_mu(vaka: dict, arac: str) -> bool:
    if vaka["beklenen_ilk_arac"] == YOK:
        # Negatif vakada dikkat dağıtıcı ya da hiç araç kabul; Takviye Bilimi aracı hata.
        return arac == YOK or arac in {d["name"] for d in DIKKAT_DAGITICILAR}
    return arac == vaka["beklenen_ilk_arac"] or arac in vaka["kabul_edilen_alternatifler"]


def olc(cagir, model: str, sistem: str, araclar: list[dict], set_: list[dict], tekrar: int) -> list[dict]:
    kayitlar = []
    for v in set_:
        denemeler = []
        for _ in range(tekrar):
            bas = time.perf_counter()
            try:
                arac, param, neden = cagir(model, sistem, araclar, v["mesaj"])
                hata = None
            except Exception as e:  # noqa: BLE001 — ölçüm sürer, hata kayda geçer
                arac, param, neden, hata = "HATA", {}, "", f"{type(e).__name__}: {e}"
            denemeler.append({"arac": arac, "parametreler": param, "durma": neden, "hata": hata,
                              "sure_sn": round(time.perf_counter() - bas, 2), "dogru": dogru_mu(v, arac)})
        kayitlar.append({**v, "denemeler": denemeler})
        print(f"{model} {v['id']}: {[d['arac'] for d in denemeler]}", file=sys.stderr)
    return kayitlar


def ozetle(kayitlar: list[dict]) -> dict:
    def dogruluk(suz):
        d = [x["dogru"] for k in kayitlar if suz(k) for x in k["denemeler"]]
        return round(sum(d) / len(d), 3) if d else None

    araclar = sorted({k["beklenen_ilk_arac"] for k in kayitlar} | {x["arac"] for k in kayitlar for x in k["denemeler"]})
    matris = defaultdict(Counter)
    for k in kayitlar:
        for x in k["denemeler"]:
            matris[k["beklenen_ilk_arac"]][x["arac"]] += 1
    pr = {}
    for a in araclar:
        if a in (YOK, "HATA"):
            continue
        tp = sum(x["arac"] == a and k["beklenen_ilk_arac"] == a for k in kayitlar for x in k["denemeler"])
        tahmin = sum(x["arac"] == a for k in kayitlar for x in k["denemeler"])
        gercek = sum(k["beklenen_ilk_arac"] == a for k in kayitlar for _ in k["denemeler"])
        pr[a] = {"precision": round(tp / tahmin, 3) if tahmin else None, "recall": round(tp / gercek, 3) if gercek else None}
    tutarli = [len({x["arac"] for x in k["denemeler"]}) == 1 for k in kayitlar]
    return {
        "dogruluk": {
            "cekirdek_gelistirme": dogruluk(lambda k: k["kategori"] == "cekirdek" and k["set"] == "gelistirme"),
            "cekirdek_tutma": dogruluk(lambda k: k["kategori"] == "cekirdek" and k["set"] == "tutma"),
            "zor": dogruluk(lambda k: k["kategori"] == "zor"),
            "negatif": dogruluk(lambda k: k["kategori"] == "negatif"),
        },
        "arac_bazinda": pr,
        "karisiklik_matrisi": {b: dict(c) for b, c in matris.items()},
        "tekrarlar_arasi_tutarlilik": round(sum(tutarli) / len(tutarli), 3),
        "hatali_vakalar": [{"id": k["id"], "mesaj": k["mesaj"], "beklenen": k["beklenen_ilk_arac"],
                            "gelen": [x["arac"] for x in k["denemeler"]]}
                           for k in kayitlar if not all(x["dogru"] for x in k["denemeler"])],
    }


def rapor_yaz(sonuclar: dict[str, dict], url: str, tekrar: int) -> Path:
    satirlar = [f"# Tetiklenme ölçümü · {date.today().isoformat()}", "",
                f"Sunucu: `{url}` · Set: `tests/tetiklenme/set_v1.jsonl` · Tekrar: {tekrar} · Eşik: tutma setinde ≥ %{int(ESIK * 100)}", "",
                "> **Sınırlama:** Bu ölçüm açıklama düzeyindeki yönlendirmeyi ölçer. claude.ai'daki kartlı araç kısıtı (adı "
                "anılmadan ya da seçilmeden doğrudan çağrılmama) burada yoktur; o kısıt A4'te (`docs/claude_canli_test.md`) "
                "manuel ölçülür.", "", "## Genel doğruluk", "",
                "| Model | Çekirdek geliştirme | Çekirdek tutma | Zor | Negatif | Tutarlılık | Eşik |", "|---|---|---|---|---|---|---|"]
    yuzde = lambda x: "—" if x is None else f"%{round(x * 100)}"  # noqa: E731
    for model, o in sonuclar.items():
        d = o["dogruluk"]
        gecti = d["cekirdek_tutma"] is not None and d["cekirdek_tutma"] >= ESIK
        satirlar.append(f"| {model} | {yuzde(d['cekirdek_gelistirme'])} | {yuzde(d['cekirdek_tutma'])} | {yuzde(d['zor'])} | "
                        f"{yuzde(d['negatif'])} | {yuzde(o['tekrarlar_arasi_tutarlilik'])} | {'geçti' if gecti else 'GEÇMEDİ'} |")
    for model, o in sonuclar.items():
        satirlar += ["", f"## {model}", "", "### Araç bazında precision / recall", "", "| Araç | Precision | Recall |", "|---|---|---|"]
        satirlar += [f"| {a} | {yuzde(v['precision'])} | {yuzde(v['recall'])} |" for a, v in o["arac_bazinda"].items()]
        sutunlar = sorted({g for c in o["karisiklik_matrisi"].values() for g in c})
        satirlar += ["", "### Karışıklık matrisi (satır: beklenen, sütun: gelen)", "",
                     "| Beklenen | " + " | ".join(sutunlar) + " |", "|---" * (len(sutunlar) + 1) + "|"]
        satirlar += [f"| {b} | " + " | ".join(str(c.get(s, 0)) for s in sutunlar) + " |" for b, c in o["karisiklik_matrisi"].items()]
        satirlar += ["", "### Hatalı vakalar", ""]
        satirlar += [f"- `{h['id']}` «{h['mesaj']}» beklenen {h['beklenen']}, gelen {h['gelen']}" for h in o["hatali_vakalar"]] or ["- Yok."]
    satirlar += ["", "## İyileştirme turları", "",
                 "Eşik altındaysa açıklama ve yönerge değişikliği önerisi buraya yazılır; değişiklik yalnızca geliştirme setine "
                 "bakılarak yapılır, başarı tutma setinde raporlanır. En fazla 3 tur.", ""]
    yol = CIKTI / "rapor.md"
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return yol


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    ap.add_argument("--model", action="append", help="Anthropic model adı; birden çok verilebilir")
    ap.add_argument("--openai-model", help="İsteğe bağlı: OPENAI_API_KEY varsa bu modelle de ölç")
    ap.add_argument("--tekrar", type=int, default=3)
    ap.add_argument("--set", type=Path, default=CIKTI / "set_v1.jsonl")
    a = ap.parse_args()

    try:
        import anthropic
    except ImportError:
        print(ANAHTAR_YOK, file=sys.stderr)
        return 2
    try:
        istemci = anthropic.Anthropic()
    except Exception:  # noqa: BLE001 — kimlik bilgisi yoksa SDK hata verir
        print(ANAHTAR_YOK, file=sys.stderr)
        return 2
    profil = Path.home() / ".config" / "anthropic"
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or profil.exists()):
        print(ANAHTAR_YOK, file=sys.stderr)
        return 2

    sistem, araclar = asyncio.run(sunucu_bilgisi(a.url))
    set_ = vakalar(a.set)
    sonuclar = {}
    for model in a.model or VARSAYILAN_MODELLER:
        kayitlar = olc(lambda m, s, t, x: anthropic_cagir(istemci, m, s, t, x), model, sistem, araclar, set_, a.tekrar)
        sonuclar[model] = ozetle(kayitlar)
        (CIKTI / f"sonuc_{date.today().isoformat()}_{model}.json").write_text(
            json.dumps({"model": model, "ozet": sonuclar[model], "kayitlar": kayitlar}, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.openai_model:
        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY tanımlı değil; ChatGPT ölçümü atlandı. Tanımlamak için: export OPENAI_API_KEY=...", file=sys.stderr)
        else:
            kayitlar = olc(openai_cagir, a.openai_model, sistem, araclar, set_, a.tekrar)
            sonuclar[a.openai_model] = ozetle(kayitlar)
            (CIKTI / f"sonuc_{date.today().isoformat()}_{a.openai_model}.json").write_text(
                json.dumps({"model": a.openai_model, "ozet": sonuclar[a.openai_model], "kayitlar": kayitlar},
                           ensure_ascii=False, indent=1), encoding="utf-8")
    print(rapor_yaz(sonuclar, a.url, a.tekrar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
