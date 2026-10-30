"""Medikal kurul inceleme paketi (kanıt protokolü, bölüm 9).

Kullanım:
    python scripts/kurul_paketi.py

Çıktı: kurul/kurul_paketi.html. Kurul onayı bekleyen tüm içerik tek dosyada: kanıt kartları ve monografiler,
zorunlu güvenlik uyarıları, şikâyet yolları, etkileşim ve karne kuralları, demo parti kaydı. Her kayıtta
kaynaklar (PubMed/DOI bağlantısı ve doğrulanmış birebir alıntılar) ve "onayla / düzelt / reddet" alanı vardır.
Kurul kararları kayıtlara elle işlenir (durum, onaylayan, onay_tarihi).
"""

from __future__ import annotations

import datetime as dt
import html
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
from server import veri  # noqa: E402

CIKTI = KOK / "kurul" / "kurul_paketi.html"
DIZIN = veri.VERI_DIZINI / "etken_maddeler"


def h(x) -> str:
    return html.escape(str(x))


def _kaynak(kid: str) -> str:
    k = veri.kaynak_kayitlari()[kid]
    url = k.get("url") or (f"https://doi.org/{k['doi']}" if k.get("doi") else f"https://pubmed.ncbi.nlm.nih.gov/{k['pmid']}/")
    kimlik = f"PMID {k['pmid']}" if k.get("pmid") else (f"DOI {k['doi']}" if k.get("doi") else "URL")
    alintilar = "".join(f"<li><q>{h(a)}</q></li>" for a in k.get("alintilar", []))
    durum = "doğrulandı" if k.get("dogrulandi") else "DOĞRULANMADI"
    return (f"<li><a href='{h(url)}'>{h(k['baslik'])}</a> · {h(k['kurum_veya_dergi'])}{', ' + h(k['yil']) if k.get('yil') else ''}"
            f" · {h(k['tur'])} · {kimlik} · {durum}{f'<ul class=alinti>{alintilar}</ul>' if alintilar else ''}</li>")


def _kaynaklar(kimlikler) -> str:
    return "<ul>" + "".join(_kaynak(k) for k in dict.fromkeys(kimlikler)) + "</ul>"


def _karar(kimlik: str) -> str:
    return (f"<div class=karar><b>Karar ({h(kimlik)}):</b> ☐ Onayla ☐ Düzelt ☐ Reddet"
            "<br>Not: ______________________________________________ · İmza / tarih: ____________</div>")


def _alan(ad: str, deger) -> str:
    return f"<tr><th>{h(ad)}</th><td>{h(deger)}</td></tr>" if deger not in (None, "", []) else ""


def kartlar() -> str:
    parcalar, sayac = [], 0
    for yol in sorted(DIZIN.glob("*/monografi.json")):
        m = json.loads(yol.read_text(encoding="utf-8"))
        parcalar.append(f"<h2 id='{h(m['id'])}'>{h(m['ad'])} · monografi ({h(m['durum'])})</h2>")
        gruplar = "".join(f"<li><b>{h(g['grup'])}</b>: {h(g['gerekce'])}</li>" for g in m["kimde_kanit_var"])
        parcalar.append(f"<table>{_alan('Kısa özet', m['kisa_ozet'])}<tr><th>Kimde kanıt var</th><td><ul>{gruplar}</ul></td></tr>"
                        + "".join(_alan(a, m.get(a, {}).get("metin")) for a in ("besinle_karsilama", "tahlil_notu"))
                        + (_alan("Formlar", " · ".join(v for k, v in m["formlar"].items() if k != "kaynaklar")) if m.get("formlar") else "")
                        + _alan("Dikkat kuralları", " · ".join(r["mesaj"] for r in m["dikkat_kurallari"]))
                        + _alan("Hekime sorulacaklar", " · ".join(m["hekime_sorulacaklar"])) + "</table>")
        kimlikler = list(m["kaynaklar"]) + [i for g in m["kimde_kanit_var"] for i in g["kaynaklar"]]
        kimlikler += [i for r in m["dikkat_kurallari"] for i in r["kaynaklar"]]
        for a in ("besinle_karsilama", "tahlil_notu", "formlar"):
            kimlikler += m.get(a, {}).get("kaynaklar", [])
        parcalar.append("<details><summary>Monografi kaynakları</summary>" + _kaynaklar(kimlikler) + "</details>")
        parcalar.append(_karar(f"{m['id']} monografi"))
        for ky in sorted((yol.parent / "kartlar").glob("*.json")):
            k = json.loads(ky.read_text(encoding="utf-8"))
            sayac += 1
            parcalar.append(f"<div class=kart><h3>{h(k['sonuc_alani'])} · {h(k['populasyon'])}</h3><table>"
                            + _alan("Soru", k["soru"]) + _alan("Kanıt düzeyi / yön", f"{k['kanit_duzeyi']} / {k['sonuc_yonu']}")
                            + _alan("Gerekçe", k["gerekce"]) + _alan("Halk özeti", k["halk_ozeti"])
                            + _alan("Mutlak fark", k["mutlak_fark"]["metin"]) + _alan("Hesap", k["mutlak_fark"]["hesap"])
                            + _alan("Çalışmalarda kullanılan miktar", k["calisilan_dozlar"]) + _alan("Ne bilmiyoruz", k["ne_bilmiyoruz"])
                            + _alan("Durum", k["durum"]) + _alan("Son arama", k["son_arama_tarihi"]) + "</table>"
                            + "<details open><summary>Kaynaklar ve alıntılar</summary>" + _kaynaklar(k["kaynaklar"]) + "</details>"
                            + _karar(k["id"]) + "</div>")
    return "".join(parcalar), sayac


def uyarilar() -> str:
    satirlar = []
    for em_id, liste in veri._zorunlu_uyarilar().items():
        for u in liste:
            satirlar.append(f"<div class=kart><h3>{h(veri.etken_madde_adi(em_id))} · {h(u['id'])}</h3>"
                            f"<p>{h(u['mesaj'])}</p><p class=k>Koşul: {h(u['kosul'] or 'herkes')} · durum: {h(u['durum'])}</p>"
                            + _kaynaklar(u["kaynaklar"]) + _karar(u["id"]) + "</div>")
    return "".join(satirlar)


def sikayet_yollari() -> str:
    parcalar = []
    for sid, y in veri.sikayet_yollari().items():
        bayraklar = "".join(f"<li>{h(b['mesaj'])} <span class=k>(koşul: {h(b['kosul'] or 'herkes')})</span></li>" for b in y["kirmizi_bayraklar"])
        kimlikler = [k for b in y["kirmizi_bayraklar"] for k in b["kaynaklar"]] + y["tahliller"]["kaynaklar"]
        parcalar.append(f"<div class=kart><h3>{h(y['ad'])}</h3><p>{h(y['giris'])}</p><b>Kırmızı bayraklar</b><ul>{bayraklar}</ul>"
                        f"<b>Tahliller</b><p>{h(', '.join(y['tahliller']['liste']))}</p><p class=k>{h(y['tahliller']['not'])}</p>"
                        + _kaynaklar(kimlikler) + _karar(f"sikayet_yolu:{sid}") + "</div>")
    return "".join(parcalar)


def kurallar() -> str:
    parcalar = []
    for k in veri.kurallar()["etkilesimler"]:
        parcalar.append(f"<div class=kart><h3>Etkileşim · {h(k['id'])}</h3><p>{h(k['mesaj'])}</p>"
                        f"<p class=k>Koşul: {h(k['kosul'])} · seviye: {h(k['seviye'])}</p>"
                        + (_kaynaklar(k["kaynaklar"]) if k.get("kaynaklar") else "<p class=k>Kaynak bağlanmamış.</p>")
                        + _karar(k["id"]) + "</div>")
    for k in veri.karne_kurallari():
        parcalar.append(f"<div class=kart><h3>Karne · {h(k['id'])}</h3><p>{h(k['mesaj'])}</p><p class=k>Koşul: {h(k['kosul'])}</p>"
                        + _kaynaklar(k["kaynaklar"]) + _karar(k["id"]) + "</div>")
    return "".join(parcalar)


def demo() -> str:
    return "".join(f"<div class=kart><h3>Parti {h(p['parti_no'])} · demo: {h(p['demo'])}</h3><p>{h(p['not'])}</p>"
                   f"<p class=k>Ürün: {h(p['urun_id'])} · {h(p['laboratuvar'])}</p>" + _karar(p["parti_no"]) + "</div>"
                   for p in veri.parti_analizleri())


def main() -> int:
    kart_html, kart_sayisi = kartlar()
    govde = f"""<!doctype html><html lang=tr><head><meta charset=utf-8><title>Kurul inceleme paketi</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#1c1f24}}
h2{{border-bottom:2px solid #1f6f5c;padding-bottom:4px;margin-top:32px}}table{{border-collapse:collapse;width:100%;margin:8px 0}}
th,td{{border:1px solid #dfe3e8;padding:6px;text-align:left;vertical-align:top}}th{{width:22%;background:#f6f7f9}}
.kart{{border:1px solid #dfe3e8;border-radius:8px;padding:10px 14px;margin:12px 0;break-inside:avoid}}
.karar{{background:#fff4e5;border:1px dashed #8a4b00;padding:8px;margin-top:8px}}.k{{color:#5b6470;font-size:12px}}
.alinti q{{font-style:italic;color:#3b4350}}@media print{{details{{display:block}}summary{{display:none}}}}</style></head><body>
<h1>Takviye Bilimi · medikal kurul inceleme paketi</h1>
<p>Üretim: {dt.date.today().isoformat()} · <code>scripts/kurul_paketi.py</code>. Kanıt kartı: {kart_sayisi}.
Tüm kaynaklar PubMed, Crossref ya da kurum sayfasından doğrulandı; alıntılar kaynağın özetinde, açık erişimli tam metninde
ya da sayfasında birebir geçer. <b>İkinci göz</b> (kartların %10'unun bağımsız yeniden değerlendirilmesi) henüz yapılmadı.</p>
<p>Durum akışı: taslak → kurul_incelemesinde → onaylandı / reddedildi. Onaylanan kayıtta onaylayan ve tarih tutulur;
sunucu yalnızca onaylı içeriği yayında gösterir (zorunlu güvenlik uyarıları onay beklerken de "taslak" etiketiyle gösterilir).</p>
<h2>1. Kanıt kartları ve monografiler</h2>{kart_html}
<h2>2. Zorunlu güvenlik uyarıları</h2>{uyarilar()}
<h2>3. Şikâyet yolları</h2>{sikayet_yollari()}
<h2>4. Etkileşim ve karne kuralları</h2>{kurallar()}
<h2>5. Demo kayıtlar</h2>{demo()}
</body></html>"""
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(govde, encoding="utf-8")
    print(f"{kart_sayisi} kanıt kartı içeren paket yazıldı: {CIKTI.relative_to(KOK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
