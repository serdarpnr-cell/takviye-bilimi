# Takviye Bilimi v0.4 · durum

Güncelleme: 2026-10-30 · Dal: `claude/blissful-mayer-pr9cb9` (main'e push yapılmadı, bkz. B1) · Testler: 377 geçti

Durum değerleri: **yapıldı** · **karar bekliyor** · **veri bekliyor** · **yapılmadı** · **engellendi** (ortam/erişim).

## Ön koşul: v0.3 iş paketi (bu oturumda uygulandı)

v0.4 talimatı v0.3'ün bittiğini varsayıyordu; repoda v0.3 uygulanmamıştı (takviye_rehberi ve karsilastir yoktu, yönerge eski). Önce v0.3 Faz 1–2 ve Faz 3'ün kod kısmı yapıldı.

| Madde | Durum | Sahibi | Not / sonraki adım |
|---|---|---|---|
| Bölüm 1 kapı + derinlik, köprü | yapıldı | geliştirme | Kapı araçları `kopru` ile biter; köprü sorusu metnin son satırı |
| Bölüm 2 yönerge | yapıldı | geliştirme | Metin birebir; yalnızca `tahlil_goster` için bir yönlendirme satırı eklendi (v0.3 listesinde yoktu) |
| Bölüm 3 açıklamalar | yapıldı | geliştirme | Birebir; açıklama uzunluk testi 300 → 1.000 karaktere çıkarıldı |
| Bölüm 4 takviye_rehberi | yapıldı | geliştirme | Eşleme `data/hedef_eslemesi.json`, `durum: taslak`: yayın sunucusunda (TB_TASLAK_GOSTER yok) sunulmaz. **Kurul onayı gerekir** |
| Bölüm 5 karsilastir + kıyas kartı | yapıldı | geliştirme | `urun_karsilastir` ve `karsilastirma` kartı bunun yerine kaldırıldı |
| Bölüm 6 annotations | yapıldı | geliştirme | Tüm araçlarda Türkçe title + 4 ipucu |
| Bölüm 7.3 serverInfo | kısmen | geliştirme | version 0.3.0 ve websiteUrl var. `title` alanını SDK 1.30 göndermiyor; ad bu yüzden "Takviye Bilimi" kaldı. icons: logo dosyası bekleniyor |
| Bölüm 7.1, 7.2, 7.4, 7.6 alan adı, favicon, logo | veri bekliyor | Serdar / pazarlama | Kart başlık bandı hazır; `server/arayuz/logo.svg` konunca kendiliğinden görünür. Favicon kontrolü bu oturumdan yapılamadı (google.com ağ politikasıyla engelli) |
| Bölüm 8 eklenti | yapıldı | geliştirme | `takviye-bilimi-plugin/`; `.mcp.json` içinde `<SUNUCU_URL>` doldurulacak |
| Bölüm 9 dizin başvurusu | yapılmadı | Serdar / hukuk | Hukuk onayından sonra |
| Bölüm 11 ölçüm | yapıldı | geliştirme | Bellekte toplu sayaç; yeniden başlatmada sıfırlanır. "Köprü kabul edildi" doğrudan ölçülemez (durumsuz sunucu); derinlik çağrısı dolaylı gösterge |
| Ek 1–12 | yapıldı | geliştirme | Ek 1: 8 üründe yaş düzeldi, katalog genelinde yaş-etiket testi. Ek 6 zaten doğruydu, teste bağlandı |
| v0.3 Bölüm 12 kabul testleri (canlı) | yapılmadı | Serdar | `docs/claude_canli_test.md` ile |

## A. Ölçüm altyapısı

| Madde | Durum | Sahibi | Not / sonraki adım |
|---|---|---|---|
| A1 tetiklenme seti | yapıldı | geliştirme | `tests/tetiklenme/set_v1.jsonl`: 30 çekirdek (20/10), 10 zor, 5 negatif; dağılım ve "araç adı geçmez" testli |
| A2 koşucu | yapıldı, **koşulmadı** | Serdar | `scripts/tetiklenme_olc.py`. Ortamda `ANTHROPIC_API_KEY` yok; doğruluk ölçülemedi. Koşmak için: anahtarı tanımla, `.venv/bin/pip install anthropic`, `python scripts/tetiklenme_olc.py --url <sunucu>/mcp`. İyileştirme turları (en fazla 3) sonuçtan sonra |
| A3 gecikme | yapıldı (yerel), Render **engellendi** | Serdar | Yerel p95: tools/call 3–11 ms, resources/read 3–5 ms, kart HTML 14–20 KB (`docs/olcumler/2026-10-30_gecikme_yerel.md`). Render ve soğuk başlangıç bu oturumdan ölçülemedi (onrender.com ağ politikasıyla engelli) |
| A4 canlı test kiti | yapıldı | Serdar | `docs/claude_canli_test.md` |

## B. Yayına alma

| Madde | Durum | Sahibi | Not / sonraki adım |
|---|---|---|---|
| B1 Render yayını | **onay bekliyor** | Serdar | Testler yeşil. Render erişimi bu oturumdan doğrulanamadığı için main.e push yapılmadı. Değişiklikler PR serdarpnr-cell/takviye-bilimi#7 içinde; birleştirince Render ana daldan yayınlar, ardından duman testi |
| B2 duman testi | yapıldı (yerel) | geliştirme → Serdar | `scripts/duman_testi.py`; yerel sonuç GEÇTİ (`docs/olcumler/2026-10-30_duman_yerel.md`). Yayından sonra Render adresiyle tekrar |
| B2 bulgu: kart sayısı | rapor | Serdar | 7 kart: kanit, urun, kiyas, rutin, karne, parti, tahlil. v0.3'e göre kartlı derinlik aracı 5; fark `parti_analizi` (kapı) ve `tahlil_goster` (v0.3 listesinde yok) |
| B2 bulgu: kapı aracında _meta.ui | **rapor, değiştirilmedi** | Serdar | `parti_analizi` kapı aracı ama parti kartına bağlı: v0.3 Bölüm 1 ile çelişki. Karar: kartı kaldırmak mı, derinlik aracı saymak mı |
| B2 bulgu: araç sayısı | rapor | Serdar | tools/list 10 araç: v0.3'ün 8'i + `tahlil_goster` + modelden gizli `katalog_sayfasi` |

## C. Karar paketleri

| Madde | Durum | Sahibi | Belge |
|---|---|---|---|
| C1 KVKK (K1–K6) | karar bekliyor | Hukuk, KVKK sorumlusu | `docs/karar/kvkk.md`. Kodda kanıt: diske yazma ve log yok; örnek log çıktısı 0 satır. `render.yaml`'da bölge alanı yok, panelden doğrulanmalı |
| C2 ikinci göz | veri bekliyor | Medikal kurul | `kurul/ikinci_goz_formu.html` (kör), tohum 20261030, 2/19 kart; kappa: `scripts/ikinci_goz.py kappa` |
| C3 hukuk sorusu | karar bekliyor | Hukuk | `docs/karar/hukuk_soru_notu.md` |
| C4 Orzax bildirimi | karar bekliyor | Serdar (gönderir) | `docs/karar/orzax_bildirim_taslagi.md`; 9 satır + TB-17 |
| C5 TB-24 etiket uyarıları | veri bekliyor | Orzax regülasyon | Şablon, doğrulamalı içe aktarma (`scripts/etiket_uyarilari_al.py`), veri talebi `docs/karar/etiket_uyarilari_veri_talebi.md`; "ambalajı okuyun" notu kalıyor |
| C6 ambalaj görseli | karar bekliyor | Serdar, pazarlama, hukuk | `docs/karar/ambalaj_gorseli.md`; iki prototip bayrak arkasında, varsayılan kapalı; yer tutucu görsellerle ölçüldü (+~48 KB base64) |
| C7 parti analizleri | veri bekliyor | Orzax kalite | Şema, içe aktarma (`scripts/parti_analizi_al.py`), veri talebi `docs/karar/parti_analizi_veri_talebi.md`; DEMO-0001 korunuyor |

## D. İçerik (hepsi taslak, kurul paketinde)

| Madde | Durum | Sahibi | Not / sonraki adım |
|---|---|---|---|
| D1-1 C vitamini, çinko | yapıldı (taslak) | Kurul | 2 + 2 kart (Cochrane 2013, Cochrane 2024). 100 kişide fark özetlerden hesaplanamadı → kurul açık sorusu |
| D1-2 multivitamin | yapılmadı | geliştirme | |
| D1-3 K2 | yapılmadı | geliştirme | Varfarin etkileşimi kural tablosunda ve bayraklarda var; kanıt kartı yok |
| D1-4 folat | yapıldı (taslak) | Kurul | Nöral tüp kartı (MRC 1991, USPSTF 2023) |
| D1-5 omega-3 balık tüketimine göre | yapılmadı | Kurul | Uygun alt grup kaynağı açık soru (arama kaydında) |
| D1-6 probiyotik, E vitamini, beta-karoten | yapılmadı | geliştirme | |
| D2 büyük çalışmalar | yapıldı (taslak) | Kurul | D-Health (ölüm kartı), ViDA, DO-HEALTH → D vitamini; ASCEND → omega-3 kalp-damar; STRENGTH + REDUCE-IT ayrı kart, "takviyeye genellenemez" notu kartta ve görsel kartta |
| D3 yeni sonuç alanları | kısmen | Kurul | D vitamini düşme kartı yapıldı. D vitamini depresyon: özet okundu ama Katman 1 kaynak bulunamadı, yazılmadı. Magnezyum (uyku, kan basıncı, migren) ve demir (gebelik) yapılmadı |
| D4 sistematik arama | yapıldı (D vitamini, omega-3, C vitamini, çinko, folik asit) | Kurul (ikinci eleme) | MeSH dizesi, tarih, sayı, eleme tablosu (AI / kurul sütunları), PRISMA. Aramalar Cochrane + şemsiye derleme ya da SR/MA filtresiyle sınırlı tutuldu; tam metin değerlendirmesi kurulda |
| D5 şikâyet yolları | **engellendi** | geliştirme | NICE CKS ve NHS bu oturumun ağ politikasıyla engelli; kırmızı bayraklar kaynak doğrulanmadan yazılmaz. Erişim açılınca saç dökülmesi, kas krampı, uyku, sık hastalanma |

Yeni ya da genişletilen kart: **8 yeni + 2 genişletilen** (toplam kart 11 → 19). Yeni kaynak: 12, hepsi PubMed'den doğrulandı (PMID → başlık, dergi, yıl; alıntılar özette birebir).

## Ortam engelleri (bu oturum)

Ağ politikası şu adresleri engelledi: `takviye-bilimi.onrender.com`, `www.google.com` (favicon), `cks.nice.org.uk`, `www.nhs.uk`. `ods.od.nih.gov` bot korumasıyla 403 döndü (yeni NIH ODS sayfası doğrulanamadı; mevcut kayıtlar 2026-10-30'da doğrulanmıştı). `ANTHROPIC_API_KEY` tanımlı değil.
