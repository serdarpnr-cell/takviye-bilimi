"""data/kaynaklar.json içindeki kaynakları API'lerden doğrular ve künyesini doldurur.

Kullanım:
    python scripts/kaynak_dogrula.py            # tüm kaynaklar
    python scripts/kaynak_dogrula.py <id> ...   # yalnızca verilen kimlikler

Her kayıt için:
- DOI varsa Crossref'ten başlık, dergi ve yıl alınır.
- PMID varsa PubMed'den başlık, dergi, yıl ve özet alınır; DOI eşleşmesi kontrol edilir.
- Yalnızca URL varsa sayfa (PDF dahil) indirilir; erişim tarihi yazılır.
- 'alinti' alanı varsa özet, açık erişimli tam metin ya da sayfa metninde birebir geçmelidir.

Doğrulanamayan kaynak 'dogrulandi: false' kalır ve sunucu onu kaynak olarak göstermez.
Ham yanıtlar data/ham/kaynaklar/ altında önbelleğe alınır.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAKLAR = KOK / "data" / "kaynaklar.json"
HAM = KOK / "data" / "ham" / "kaynaklar"
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
AJAN = {"User-Agent": "TakviyeBilimi-kaynak-dogrulama/0.1"}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from json_yaz import yaz  # noqa: E402
from lint_ifadeler import bul as yasakli_ifadeler  # noqa: E402


def _getir(url: str, onbellek: str) -> bytes:
    dosya = HAM / onbellek
    if dosya.exists() and dosya.stat().st_size:
        return dosya.read_bytes()
    for deneme in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=AJAN), timeout=60) as y:
                govde = y.read()
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or deneme == 3:
                raise
            time.sleep(2 ** (deneme + 1))
    HAM.mkdir(parents=True, exist_ok=True)
    dosya.write_bytes(govde)
    # NCBI anahtarsız saniyede 3 istek kabul eder.
    time.sleep(0.12 if os.environ.get("NCBI_API_KEY") else 0.4)
    return govde


def _ncbi(yol: str, **parametre) -> bytes:
    if os.environ.get("NCBI_API_KEY"):
        parametre["api_key"] = os.environ["NCBI_API_KEY"]
    onbellek = f"ncbi_{yol.split('.')[0]}_{parametre.get('id')}.{parametre.get('retmode', 'xml')}"
    return _getir(f"{NCBI}/{yol}?" + urllib.parse.urlencode(parametre), onbellek)


def sade(metin: str) -> str:
    """Alıntı karşılaştırması için: Unicode biçimi, mikro işareti, tire ve boşluk farklarını giderir."""
    metin = unicodedata.normalize("NFKC", html.unescape(metin))
    metin = metin.replace("µ", "μ").replace("‐", "-").replace("–", "-").replace("−", "-")
    return re.sub(r"\s+", " ", metin).strip().casefold()


def _xml_metin(x: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x)))


def _crossref(doi: str) -> dict:
    ham = _getir(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}", f"crossref_{doi.replace('/', '_')}.json")
    m = json.loads(ham)["message"]
    return {
        "baslik": re.sub(r"\s+", " ", html.unescape(m["title"][0])).strip(),
        "kurum_veya_dergi": (m.get("container-title") or [m.get("publisher", "")])[0],
        "yil": m["issued"]["date-parts"][0][0],
    }


def _pubmed(pmid: str) -> dict:
    x = _ncbi("efetch.fcgi", db="pubmed", id=pmid, retmode="xml").decode("utf-8")
    baslik = _xml_metin(re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", x, re.S).group(1)).strip()
    kisa = re.search(r"<ISOAbbreviation>(.*?)</ISOAbbreviation>", x, re.S)
    dergi = _xml_metin((kisa or re.search(r"<Title>(.*?)</Title>", x, re.S)).group(1)).strip()
    yil = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", x, re.S) or re.search(r"<MedlineDate>(\d{4})", x)
    ozet = _xml_metin(" ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", x, re.S)))
    doi = re.search(r'<ArticleId IdType="doi">(.*?)</ArticleId>', x)
    pmc = re.search(r'<ArticleId IdType="pmc">(.*?)</ArticleId>', x)
    geri = "Retracted Publication" in x
    return {"baslik": baslik.rstrip("."), "kurum_veya_dergi": dergi, "yil": int(yil.group(1)) if yil else None,
            "ozet": ozet, "doi": doi.group(1) if doi else None, "pmcid": pmc.group(1) if pmc else None,
            "geri_cekildi": geri}


def _tam_metin(pmcid: str) -> str:
    try:
        return _xml_metin(_getir(f"{EPMC}/{pmcid}/fullTextXML", f"{pmcid}.xml").decode("utf-8"))
    except Exception:
        return ""


def _sayfa_metni(url: str) -> str:
    ad = re.sub(r"[^A-Za-z0-9]+", "_", url.split("://", 1)[1])[:120]
    govde = _getir(url, f"url_{ad}")
    if govde[:4] == b"%PDF":
        pdf = HAM / f"url_{ad}"
        return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    metin = govde.decode("utf-8", "replace")
    return _xml_metin(re.sub(r"<(script|style)[^>]*>.*?</\1>", "", metin, flags=re.S))


def dogrula(kayit: dict) -> tuple[dict, list[str]]:
    """Kaydı API'den doldurur ve doğrular. (güncel kayıt, sorunlar) döner."""
    k = dict(kayit)
    sorunlar: list[str] = []
    metinler: list[str] = []
    # Künye DOI/PMID'li kayıtlarda API'den yazılır (PubMed önceliklidir); elle girilen yalnızca URL'li kayıtlardadır.
    if k.get("doi"):
        cr = _crossref(k["doi"])
        for alan in ("baslik", "kurum_veya_dergi", "yil"):
            k[alan] = cr[alan]
        if sade(cr["baslik"])[:50] != sade(k["baslik"])[:50]:
            sorunlar.append(f"Başlık Crossref ile uyuşmuyor: {cr['baslik']!r}")
    if k.get("pmid"):
        pm = _pubmed(str(k["pmid"]))
        for alan in ("baslik", "kurum_veya_dergi", "yil"):
            if pm[alan]:
                k[alan] = pm[alan]
        if k.get("doi") and pm["doi"] and pm["doi"].casefold() != k["doi"].casefold():
            sorunlar.append(f"PubMed DOI'si farklı: {pm['doi']}")
        if pm["geri_cekildi"]:
            sorunlar.append("Yayın geri çekilmiş.")
        metinler.append(pm["ozet"])
        if pm["pmcid"]:
            metinler.append(_tam_metin(pm["pmcid"]))
    if k.get("url") and not k.get("doi") and not k.get("pmid"):
        sayfa = _sayfa_metni(k["url"])
        metinler.append(sayfa)
        k.setdefault("erisim_tarihi", dt.date.today().isoformat())
        if k["tur"] == "uretici_icerigi":
            # Yasaklı ifade içeren üretici içeriği reddedilmez, insan incelemesine düşer (CLAUDE.md).
            # Site alt bilgisi ve çerez bandı taramaya katılmaz.
            bulgular = yasakli_ifadeler(sayfa.split("Tüm hakları saklıdır")[0])
            k["inceleme"] = "gerekli" if bulgular else "gerekmiyor"
            k["lint_bulgulari"] = [b["baglam"] for b in bulgular]
    for alinti in k.get("alintilar", []):
        if not any(sade(alinti) in sade(m) for m in metinler if m):
            sorunlar.append(f"Alıntı kaynakta bulunamadı: {alinti[:80]!r}")
    if not (k.get("doi") or k.get("pmid") or k.get("url")):
        sorunlar.append("DOI, PMID veya URL yok.")
    k["dogrulandi"] = not sorunlar
    k["dogrulama_tarihi"] = dt.date.today().isoformat()
    return k, sorunlar


def main(kimlikler: list[str]) -> int:
    veri = json.loads(KAYNAKLAR.read_text(encoding="utf-8"))
    hata = 0
    for kid, kayit in veri["kaynaklar"].items():
        if kimlikler and kid not in kimlikler:
            continue
        try:
            yeni, sorunlar = dogrula(kayit)
        except Exception as e:  # ağ hatası, eksik alan
            yeni, sorunlar = {**kayit, "dogrulandi": False}, [f"Doğrulama yapılamadı: {e}"]
        veri["kaynaklar"][kid] = yeni
        durum = "tamam" if not sorunlar else "SORUN"
        print(f"{durum:6} {kid}: {yeni.get('baslik', '')[:70]}")
        for s in sorunlar:
            print(f"         - {s}")
        hata += bool(sorunlar)
    yaz(KAYNAKLAR, veri)
    return 1 if hata else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
