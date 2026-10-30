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

---

Tarih: 2026-10-30 · Araçlar: PubMed E-utilities (esearch, esummary, efetch), NCBI API anahtarıyla. Ham yanıtlar: `data/ham/arama/d3.json` (git'e girmez).

## Sistematik arama (v0.4 D4)

```
"Vitamin D"[Mesh] AND "Dietary Supplements"[Mesh] AND ("Cochrane Database Syst Rev"[ta] OR umbrella review[ti]) AND 2016:2026[dp]
```

Sonuç sayısı: **33** (2026-10-30). Ön eleme başlık ve PubMed yayın türüne göre yapıldı; özet okunarak doğrulanması ve tam metin değerlendirmesi kurulun ikinci elemesidir.

### PRISMA akış sayıları

| Aşama | Sayı |
|---|---|
| Veri tabanında tanımlanan kayıt | 33 |
| Yinelenen kayıt (çıkarılan) | 0 |
| Başlık/özet taranan | 33 |
| Başlık/özet aşamasında elenen (ön eleme: AI) | 22 (D1: 13, D2: 3, D3: 1, D4: 1, D5: 4) |
| Tam metin değerlendirmesine aday | 11 |
| Tam metin değerlendirilen (kurul) | — |
| Kartta kullanılan | kurul tam metin elemesinden sonra |

### Başlık/özet eleme tablosu

Gerekçe kodları: **DH** dahil (tam metin aşamasına) · **D1** popülasyon kapsam dışı (belirli hastalığın tedavisi, hastane/yoğun bakım, bebek maması) · **D2** sonuç alanı kapsam dışı ya da ara ölçüm · **D3** daha güncel sürümü var / geri çekilmiş · **D4** çalışma türü uygun değil (gözlemsel, yöntem makalesi, anlatı) · **D5** müdahale takviye değil ya da başka maddelerle karışık.

| PMID | Yıl | Başlık | Ön eleme: AI | İkinci eleme: kurul |
|---|---|---|---|---|
| 42746921 | 2026 | Vitamin D supplementation for prevention of vitamin D deficiency in preterm and low birth weight infants. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 42256481 | 2025 | The role of specific nutrients in preventing immune system and blood cell disorders: an umbrella review. | hariç (D2) Bağışıklık ve kan hastalıkları, çok besinli | |
| 42197022 | 2026 | Vitamin D Supplementation in Children with Asthma: An Umbrella Review. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 42037591 | 2026 | Vitamin D for preventing acute respiratory infections in children up to five years of age. | dahil (DH) 5 yaş altı çocuklarda solunum yolu enfeksiyonu (Cochrane 2026): solunum kartının güncellenmesi için | |
| 41865680 | 2026 | Effect of diet intervention on symptoms in autism spectrum disorder: An umbrella review. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 41830039 | 2026 | Vitamin D Status and Sepsis Outcomes: A PRISMA-Compliant Umbrella Review and Meta-Analysis. | hariç (D1) Sepsis | |
| 41814462 | 2026 | Vitamin D and Bladder Cancer Risk: An Umbrella Review and Second Order Meta-Analysis. | hariç (D4) Mesane kanseri, çoğunlukla gözlemsel | |
| 40818820 | 2025 | The efficacy of dietary interventions for prediabetes management: An umbrella review of meta-analyses. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 40792481 | 2025 | Vitamin D supplementation in pregnant or breastfeeding women or young children for preventing asthma. | dahil (DH) Gebelik ve küçük çocukta astım önleme (Cochrane 2025) | |
| 40037889 | 2025 | Umbrella Review on the Relationship Between Vitamin D Intake and Cancer. | dahil (DH) Kanser şemsiye derlemesi | |
| 39986938 | 2025 | The effect of vitamin D supplementation on endothelial function: An umbrella review of interventional meta-ana | hariç (D2) Endotel işlevi: ara ölçüm | |
| 39907316 | 2025 | Association Between Vitamin D and COVID-19-Related Outcomes: An Umbrella Review of Meta-Analyses. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 39374790 | 2024 | Vitamin D in Multiple Sclerosis: A Comprehensive Umbrella Review. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 39351881 | 2024 | Oral vitamin D supplementation for adults with obesity undergoing bariatric surgery. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 39178988 | 2024 | Vitamin D3 and cancer risk in healthy subjects: An umbrella review of systematic review and meta-analysis. | dahil (DH) Sağlıklı kişilerde kanser riski şemsiye derlemesi | |
| 39077939 | 2024 | Vitamin D supplementation for women during pregnancy. | dahil (DH) Gebelikte D vitamini (Cochrane 2024) | |
| 38816412 | 2024 | Effects of vitamin D in pregnancy on maternal and offspring health-related outcomes: An umbrella review of sys | dahil (DH) Gebelik sonuçları şemsiye derlemesi | |
| 38180112 | 2024 | Population-based interventions for preventing falls and fall-related injuries in older people. | hariç (D5) Toplum düzeyi düşme önleme programları; takviyeye özgü değil | |
| 37657652 | 2023 | The Effect of Vitamin D Supplementation on Lipid Profiles: an Umbrella Review of Meta-Analyses. | hariç (D2) Lipid profili: ara ölçüm | |
| 36099162 | 2023 | Effects of nutrition on metabolic and endocrine outcomes in women with polycystic ovary syndrome: an umbrella  | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 35684094 | 2022 | Efficacy and Safety of Nutrient Supplements for Glycaemic Control and Insulin Resistance in Type 2 Diabetes: A | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 34999745 | 2022 | Vitamin D and Multiple Health Outcomes: An Umbrella Review of Observational Studies, Randomized Controlled Tri | dahil (DH) Çoklu sonuç: RKÇ ve Mendel randomizasyonu şemsiye derlemesi | |
| 34687206 | 2022 | Vitamin D Supplementation and Fractures in Adults: A Systematic Umbrella Review of Meta-Analyses of Controlled | dahil (DH) Kırık: kontrollü çalışma meta-analizlerinin şemsiye derlemesi | |
| 34431511 | 2021 | Vitamin D supplementation for chronic liver diseases in adults. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 32526091 | 2020 | Interventions to prevent women from developing gestational diabetes mellitus: an overview of Cochrane Reviews. | hariç (D5) Gestasyonel diyabet önleme, çok müdahaleli genel derleme | |
| 32244496 | 2020 | Role of Vitamin D in Preventing and Treating Selected Extraskeletal Diseases-An Umbrella Review. | dahil (DH) İskelet dışı hastalıklar şemsiye derlemesi | |
| 32130738 | 2020 | Drugs for preventing lung cancer in healthy people. | hariç (D5) Akciğer kanserini önleyen ilaçlar | |
| 31348529 | 2019 | Vitamin D supplementation for women during pregnancy. | hariç (D3) 2024 Cochrane sürümüyle güncellendi | |
| 31116878 | 2019 | Calcium, vitamin D or recombinant parathyroid hormone for managing post-thyroidectomy hypoparathyroidism. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 30556597 | 2018 | Vitamin and mineral supplementation for maintaining cognitive function in cognitively healthy people in mid an | dahil (DH) Sağlıklı orta ve ileri yaşta bilişsel işlev (Cochrane 2018) | |
| 30277579 | 2018 | Calcium supplementation during pregnancy for preventing hypertensive disorders and related problems. | hariç (D5) Gebelikte kalsiyum | |
| 30047068 | 2018 | Pharmacological Interventions to Improve Muscle Mass, Muscle Strength and Physical Performance in Older People | dahil (DH) Yaşlılarda kas gücü ve fiziksel performans şemsiye derlemesi | |
| 28518221 | 2017 | Micronutrient supplementation in adults with HIV infection. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |

## Hedefli doğrulama (kanıt protokolü Katman 1 ve 3)

| Hedef | Kimlik | Sonuç |
|---|---|---|
| VITAL, FIND, USPSTF, Endocrine Society, EFSA | bkz. yukarıdaki ilk kayıt | Dahil (önceki kayıt) |
| D-Health ölüm | PMID 35026158 | Dahil: ölüm kartı (RKÇ, n = 21.315) |
| D-Health düşme | PMID 34337905 | Dahil: düşme kartı |
| D-Health depresyon | PMID 36462182 | Özet okundu (PHQ-9 farkı yok); Katman 1 kaynak bulunmadığı için depresyon kartı yazılmadı |
| USPSTF düşme 2018 | PMID 29710141 | Dahil: düşme kartı (kılavuz, D önerisi) |
| ViDA | PMID 28384800 | Dahil: kanser ve kalp-damar kartına eklendi (RKÇ, n = 5.110) |
| DO-HEALTH | PMID 33170239 | Dahil: kanser ve kalp-damar kartına eklendi (RKÇ, n = 2.157) |

## Kurul için açık sorular

- Cochrane 2026 çocuk solunum enfeksiyonu derlemesi (PMID 42037591) mevcut solunum kartını değiştiriyor mu?
- Depresyon kartı için Katman 1 kaynak (kılavuz ya da Cochrane) var mı?
- D-Health düşme ve ölüm kartlarında grup başına olay oranları (tam metin tabloları)
