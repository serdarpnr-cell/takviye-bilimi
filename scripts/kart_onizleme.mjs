// MCP Apps host benzetimi: kartı iframe'de çizer, JSON-RPC mesajlarını host gibi yanıtlar. kart_onizleme.py çağırır.
// Kullanım: node kart_onizleme.mjs <senaryolar.json> <çıktı dizini> <görüntü 0|1>
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const [, , girdiYolu, cikti, goruntu] = process.argv;
const senaryolar = JSON.parse(readFileSync(girdiYolu, "utf8"));

// Host sayfası: iframe srcdoc ile kartı yükler; gömülü senaryodan (window.__senaryo) yanıt üretir.
const HOST = (veri) => `<!doctype html><html><body style="margin:0;background:#888">
<script>window.__senaryo = ${veri};</script>
<iframe id="kart" sandbox="allow-scripts" style="width:420px;height:400px;border:0;background:transparent"></iframe>
<script>
const s = window.__senaryo; const f = document.getElementById("kart");
const sayac = {}; window.__yukseklik = 0; window.__cagrilar = []; window.__mesajlar = [];
const gonder = (m) => f.contentWindow.postMessage({ jsonrpc: "2.0", ...m }, "*");
window.addEventListener("message", (o) => {
  const m = o.data; if (!m || m.jsonrpc !== "2.0") return;
  if (m.method) window.__mesajlar.push({ method: m.method, params: m.params });
  if (m.method === "ui/initialize") gonder({ id: m.id, result: { protocolVersion: "2026-01-26", hostContext: { theme: s.tema } } });
  else if (m.method === "ui/notifications/initialized") {
    gonder({ method: "ui/notifications/tool-input", params: { arguments: s.girdi } });
    gonder({ method: "ui/notifications/tool-result", params: s.sonuc });
  } else if (m.method === "ui/notifications/size-changed") {
    window.__yukseklik = m.params.height; f.style.height = m.params.height + "px";
  } else if (m.method === "tools/call") {
    window.__cagrilar.push(m.params);
    const liste = (s.cagrilar || {})[m.params.name] || [];
    const i = sayac[m.params.name] = (sayac[m.params.name] || 0);
    sayac[m.params.name] += 1;
    gonder(i < liste.length ? { id: m.id, result: liste[i] } : { id: m.id, error: { code: -32601, message: "yok" } });
  } else if (m.id !== undefined) gonder({ id: m.id, result: {} });
});
f.srcdoc = s.html;
</script></body></html>`;

const tarayici = await chromium.launch();
const rapor = [];
for (const s of senaryolar) {
  for (const tema of goruntu === "1" ? ["light", "dark"] : ["light"]) {
    const sayfa = await tarayici.newPage({ viewport: { width: 420, height: 900 }, colorScheme: tema });
    const hatalar = [];
    sayfa.on("console", (m) => { if (m.type() === "error") hatalar.push(m.text()); });
    sayfa.on("pageerror", (e) => hatalar.push(String(e)));
    // "<" kaçırılır: gömülü HTML içindeki </script> host betiğini kapatmasın.
    await sayfa.setContent(HOST(JSON.stringify({ ...s, tema }).replace(/</g, "\\u003c")));
    const kart = sayfa.frameLocator("#kart");
    await sayfa.waitForFunction(() => window.__yukseklik > 0, null, { timeout: 10000 }).catch(() => {});
    await sayfa.waitForTimeout(300);
    for (const [secici, deger] of Object.entries(s.doldur || {})) await kart.locator(secici).fill(String(deger));
    if (s.tikla) {
      const dugme = kart.locator(s.tikla).first();
      if (await dugme.count()) { await dugme.click(); await sayfa.waitForTimeout(300); }
    }
    const eksik = [];
    // Boş bölüm "null"/"undefined" metni olarak sızmamalı.
    const metin = await kart.locator("body").innerText();
    for (const kacak of ["null", "undefined", "[object Object]"]) if (new RegExp(`(^|\\n)${kacak.replace(/[[\]]/g, "\\$&")}(\\n|$)`).test(metin)) hatalar.push(`sayfada '${kacak}' metni`);
    for (const secici of s.beklenen || []) if (!(await kart.locator(secici).count())) eksik.push(secici);
    const altBilgi = kart.locator("#alt-bilgi");
    const gorunur = (await altBilgi.count()) ? await altBilgi.isVisible() : false;
    const cagrilar = await sayfa.evaluate(() => window.__cagrilar);
    const mesajlar = await sayfa.evaluate(() => window.__mesajlar);
    const yukseklik = await sayfa.evaluate(() => window.__yukseklik);
    if (goruntu === "1") await sayfa.locator("#kart").screenshot({ path: join(cikti, `${s.ad}_${tema}.png`) });
    rapor.push({ ad: s.ad, tema, konsol_hatalari: hatalar, eksik_ogeler: eksik, alt_bilgi_gorunur: gorunur,
                 yukseklik, tools_call: cagrilar.map((c) => c.name),
                 mesajlar: [...new Set(mesajlar.map((x) => x.method))], mesaj_icerigi: JSON.stringify(mesajlar) });
    await sayfa.close();
  }
}
await tarayici.close();
process.stdout.write(JSON.stringify(rapor));
