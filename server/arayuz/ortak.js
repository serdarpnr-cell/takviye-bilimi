// Tüm görsel kartların ortak MCP Apps köprüsü: üst pencereyle JSON-RPC 2.0 (postMessage).
// arayuz._sayfa her sayfaya satır içi gömer. Mesaj adları @modelcontextprotocol/ext-apps tip tanımlarına göre yazılmıştır.
const TB = (() => {
  const PROTOKOL = "2026-01-26";
  let sonId = 0;
  const bekleyenler = new Map();
  const dinleyiciler = { sonuc: () => {}, girdi: () => {} };

  function istek(method, params) {
    const id = ++sonId;
    window.parent.postMessage({ jsonrpc: "2.0", id, method, params }, "*");
    return new Promise((coz, reddet) => bekleyenler.set(id, { coz, reddet }));
  }
  function bildirim(method, params) {
    window.parent.postMessage({ jsonrpc: "2.0", method, params }, "*");
  }
  function temaUygula(baglam) {
    if (baglam?.theme) document.documentElement.dataset.theme = baglam.theme;
  }
  window.addEventListener("message", (olay) => {
    const m = olay.data;
    if (!m || m.jsonrpc !== "2.0") return;
    if (m.id !== undefined && bekleyenler.has(m.id)) {
      const { coz, reddet } = bekleyenler.get(m.id);
      bekleyenler.delete(m.id);
      m.error ? reddet(m.error) : coz(m.result);
      return;
    }
    if (m.method === "ui/notifications/tool-input") dinleyiciler.girdi(m.params?.arguments || {});
    else if (m.method === "ui/notifications/tool-result") dinleyiciler.sonuc(m.params);
    else if (m.method === "ui/notifications/host-context-changed") temaUygula(m.params);
  });
  // Yüksekliği üst pencereye bildir (iframe boyutu).
  new ResizeObserver(() => {
    bildirim("ui/notifications/size-changed", { height: Math.ceil(document.documentElement.scrollHeight) });
  }).observe(document.body);

  const el = (etiket, ozellik = {}, ...cocuklar) => {
    const e = document.createElement(etiket);
    Object.assign(e, ozellik);
    e.append(...cocuklar.filter((c) => c !== null && c !== undefined && c !== false));
    return e;
  };
  // Boş (null) bölümler atlanır; replaceChildren null'ı "null" metni olarak yazardı.
  const doldur = (kutu, ...parcalar) => kutu.replaceChildren(...parcalar.filter((p) => p !== null && p !== undefined && p !== false));
  const rozet = (metin, tur = "") => el("span", { className: `rozet ${tur}`.trim(), textContent: metin });

  function baglanti(url, metin) {
    const a = el("a", { href: url, textContent: metin, rel: "noopener" });
    a.addEventListener("click", (o) => { o.preventDefault(); istek("ui/open-link", { url }).catch(() => {}); });
    return a;
  }

  // Kaynak listesi; alt bilgideki "Kaynaklar" bağlantısı #kaynaklar'a gider.
  function kaynaklar(liste) {
    return el("section", {},
      el("h2", { id: "kaynaklar", textContent: "Kaynaklar" }),
      el("ul", {}, ...(liste || []).map((k) => el("li", {},
        baglanti(k.url, `${k.baslik} (${k.kurum_veya_dergi}${k.yil ? ", " + k.yil : ""})`)))));
  }

  // 100 kişilik ikon dizisi: "100 kişiden X" (mutlak fark).
  function noktaDizisi(sayi, sinif = "dolu", etiket = "") {
    const izgara = el("div", { className: "nokta-dizisi" });
    izgara.setAttribute("role", "img");
    izgara.setAttribute("aria-label", `100 kişiden ${sayi}${etiket ? " · " + etiket : ""}`);
    for (let i = 0; i < 100; i++) izgara.append(el("span", { className: i < sayi ? `nokta ${sinif}` : "nokta" }));
    return izgara;
  }

  function baslat(ad, { sonuc, girdi } = {}) {
    if (sonuc) dinleyiciler.sonuc = sonuc;
    if (girdi) dinleyiciler.girdi = girdi;
    istek("ui/initialize", { appInfo: { name: ad, version: "0.2.0" }, appCapabilities: {}, protocolVersion: PROTOKOL })
      .then((s) => { temaUygula(s?.hostContext); bildirim("ui/notifications/initialized", {}); })
      .catch(() => {});
  }

  return { istek, bildirim, el, doldur, rozet, baglanti, kaynaklar, noktaDizisi, baslat };
})();
