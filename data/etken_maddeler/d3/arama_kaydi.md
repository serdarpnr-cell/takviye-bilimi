# D vitamini · arama kaydı

Tarih: 2026-10-29 · Araçlar: PubMed E-utilities (efetch/esearch/esummary), Europe PMC REST, Crossref REST.
Ham yanıtlar: `data/ham/kaynaklar/` (git'e girmez).

## Hedefli doğrulama (kanıt protokolü, Katman 1 ve 3)

| Hedef | Sorgu / kimlik | Sonuç |
|---|---|---|
| VITAL ana sonuç | PMID 30415629 | Dahil (RKÇ, n = 25.871) |
| VITAL kırık | `LeBoff[au] AND vitamin D AND fractures AND "N Engl J Med"[ta]` → 2 kayıt | 35939577 dahil; 36300986 (yazara yanıt) elendi: veri içermiyor |
| FIND kırık | `"Supplemental Vitamin D and Incident Fractures in Midlife and Older Adults"` → 5 kayıt | 42704968 dahil (RKÇ, n = 2.495); diğer 4 kayıt konu dışı |
| USPSTF kırık önleme | PMID 29677309 | Dahil (kılavuz) |
| USPSTF D vitamini tarama | PMID 33847711 | Dahil (kılavuz) |
| USPSTF düşme önleme | `Interventions to Prevent Falls ... USPSTF Recommendation Statement` → 38833246 (2024), 29710141 (2018) | 2024 özeti D vitaminini anmıyor; düşme sonucu bu sürümde kartlanmadı |
| Solunum yolu enfeksiyonu | PMID 33798465 | Dahil (meta-analiz, 43 çalışma) |
| Endocrine Society 2024 | PMID 38828931 | Dahil (kılavuz) |
| EFSA üst sınır | DOI 10.2903/j.efsa.2023.8145, PMID 37560437 | Dahil (düzenleyici) |

## Hatalı kimlikler

Bellekten denenen iki PMID API kontrolünde yanlış çıktı ve kullanılmadı:
35353964 (karotis stenti), 29710338 (sigmoidoskopi taraması).

## Açık kalanlar

- D-Health, DO-HEALTH ve ViDA (kanıt protokolü, Katman 3) henüz kartlanmadı.
- Düşme, kas gücü, depresyon, tip 2 diyabet ve tüm nedenlere bağlı ölüm sonuç alanları kartlanmadı.
- Sistematik arama dizesi (MeSH) ve eleme sayıları Faz 1'in tamamında çalıştırılacak; bu kayıt pilot kartlar için hedefli doğrulamadır.
- Türkiye Sağlık Bakanlığı D vitamini programı sayfası (hsgm.saglik.gov.tr) bulut ortamından erişilemediği için eklenmedi.
