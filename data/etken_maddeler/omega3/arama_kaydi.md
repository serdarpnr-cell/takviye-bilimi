# Omega-3 (EPA + DHA) · arama kaydı

Tarih: 2026-10-30 · Araçlar: PubMed E-utilities (NCBI API anahtarıyla), Europe PMC REST.
Ham yanıtlar: `data/ham/arama/` ve `data/ham/kaynaklar/` (git'e girmez).

## Hedefli arama (kanıt protokolü Katman 1 ve 3)

| Hedef | Sorgu / kimlik | Sonuç sayısı | Karar |
|---|---|---|---|
| VITAL omega-3 kolu | `Marine n-3 Fatty Acids and Prevention of Cardiovascular Disease and Cancer[ti]` | 1 | 30415637 dahil (RKÇ, n = 25.871) |
| Cochrane kalp-damar | `Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease[ti]` | 8 | 32114706 dahil (2020 güncellemesi); 2018 sürümleri ve S Afr Med J özeti elendi |
| AHA 2017 omega-3 takviyesi bilimsel görüşü | `Omega-3 Polyunsaturated Fatty Acid (Fish Oil) Supplementation and the Prevention of Clinical Cardiovascular Disease[ti]` | 2 | 28289069 bulundu; özet öneri metnini içermiyor, tam metin Europe PMC'den alınamadı: karta eklenmedi |
| Gebelik (Cochrane) | `omega-3 pregnancy[ti] AND Cochrane Database Syst Rev[ta] AND 2018[dp]` | 1 | 30480773 dahil |
| ORIP | `Makrides M[au] AND omega-3 AND preterm[ti] AND 2019[dp]` | 4 | 31509674 dahil (RKÇ, n = 5517); diğer 3 kayıt konu dışı |
| ADORE | `higher dose docosahexaenoic acid preterm birth[ti] AND (ADORE OR randomised OR randomized)` | 4 | 34308309 dahil (RKÇ; kapsüller üretici tarafından sağlandı); 3 ikincil analiz elendi |

## Sonuç

Taranan: 20 kayıt · dahil: 5 · elenen: 15.
ORIP, Cochrane 2018'den sonra yayımlandı ve 34. haftadan önce doğumda fark bulmadı; gebelik kartının yönü bu nedenle "belirsiz".

## Açık kalanlar

- ASCEND, STRENGTH ve REDUCE-IT (kanıt protokolü Katman 3) henüz kartlanmadı; REDUCE-IT reçeteli yüksek doz olarak ayrı işaretlenecek.
- Trigliserit, kan basıncı, depresyon, atriyal fibrilasyon (güvenlik sinyali) sonuç alanları.

---

Tarih: 2026-10-30 · Araçlar: PubMed E-utilities (esearch, esummary, efetch), NCBI API anahtarıyla. Ham yanıtlar: `data/ham/arama/omega3.json` (git'e girmez).

## Sistematik arama (v0.4 D4)

```
"Fatty Acids, Omega-3"[Mesh] AND "Dietary Supplements"[Mesh] AND ("Cochrane Database Syst Rev"[ta] OR umbrella review[ti]) AND 2016:2026[dp]
```

Sonuç sayısı: **20** (2026-10-30). Ön eleme başlık ve PubMed yayın türüne göre yapıldı; özet okunarak doğrulanması ve tam metin değerlendirmesi kurulun ikinci elemesidir.

### PRISMA akış sayıları

| Aşama | Sayı |
|---|---|
| Veri tabanında tanımlanan kayıt | 20 |
| Yinelenen kayıt (çıkarılan) | 0 |
| Başlık/özet taranan | 20 |
| Başlık/özet aşamasında elenen (ön eleme: AI) | 14 (D1: 8, D3: 2, D5: 4) |
| Tam metin değerlendirmesine aday | 6 |
| Tam metin değerlendirilen (kurul) | — |
| Kartta kullanılan | kurul tam metin elemesinden sonra |

### Başlık/özet eleme tablosu

Gerekçe kodları: **DH** dahil (tam metin aşamasına) · **D1** popülasyon kapsam dışı (belirli hastalığın tedavisi, hastane/yoğun bakım, bebek maması) · **D2** sonuç alanı kapsam dışı ya da ara ölçüm · **D3** daha güncel sürümü var / geri çekilmiş · **D4** çalışma türü uygun değil (gözlemsel, yöntem makalesi, anlatı) · **D5** müdahale takviye değil ya da başka maddelerle karışık.

| PMID | Yıl | Başlık | Ön eleme: AI | İkinci eleme: kurul |
|---|---|---|---|---|
| 41102950 | 2025 | The effect of n-3 supplementation on clinical outcomes in patients with sepsis: an umbrella review of systemat | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 40990181 | 2025 | Omega-3 fatty acid supplementation for distal symmetrical peripheral neuropathy in adults with diabetes mellit | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 39568282 | 2025 | Impact of omega-3 fatty acid supplementation on clinical manifestations in autism spectrum disorders: an umbre | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 39564892 | 2024 | Omega-3 fatty acid supplementation for depression in children and adolescents. | dahil (DH) Çocuk ve ergende depresyon (Cochrane 2024) | |
| 39470212 | 2024 | Omega-3 fatty acids for intermittent claudication. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 37886879 | 2024 | Clinical impacts of n-3 fatty acids supplementation on depression symptoms: an umbrella review of meta-analyse | dahil (DH) Depresyon belirtileri şemsiye derlemesi | |
| 35104631 | 2022 | The effects of omega-3 polyunsaturated fatty acids supplementation in pregnancy, lactation, and infancy: An um | dahil (DH) Gebelik, emzirme ve bebeklik şemsiye derlemesi | |
| 33660821 | 2021 | Omega-3 fatty acids supplementation on major cardiovascular outcomes: an umbrella review of meta-analyses of o | dahil (DH) Kalp-damar sonuçları şemsiye derlemesi | |
| 33320335 | 2020 | Souvenaid for Alzheimer's disease. | hariç (D5) Çok bileşenli tıbbi beslenme ürünü | |
| 32677037 | 2020 | Nutritional interventions for treating foot ulcers in people with diabetes. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 32526091 | 2020 | Interventions to prevent women from developing gestational diabetes mellitus: an overview of Cochrane Reviews. | hariç (D5) Gestasyonel diyabet önleme, çok müdahaleli genel derleme | |
| 32428983 | 2020 | Dietary interventions for multiple sclerosis-related outcomes. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 32275788 | 2020 | Omega-3 fatty acid supplementation for cystic fibrosis. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |
| 32114706 | 2020 | Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease. | dahil (DH) Kalp-damar önleme (Cochrane 2020): kalp-damar kartında kullanılıyor | |
| 30521670 | 2018 | Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease. | hariç (D3) 2020 Cochrane sürümüyle güncellendi | |
| 30480773 | 2018 | Omega-3 fatty acid addition during pregnancy. | dahil (DH) Gebelikte omega-3 (Cochrane 2018): erken doğum kartında kullanılıyor | |
| 30019766 | 2018 | Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease. | hariç (D3) 2020 Cochrane sürümüyle güncellendi | |
| 28281303 | 2017 | Long chain polyunsaturated fatty acid supplementation in infants born at term. | hariç (D5) Bebek mamasına eklenen uzun zincirli yağ asidi | |
| 27995607 | 2016 | Longchain polyunsaturated fatty acid supplementation in preterm infants. | hariç (D5) Prematüre bebek beslenmesi | |
| 26730723 | 2016 | Omega-3 fatty acids for cystic fibrosis. | hariç (D1) Belirli bir hastalığın tedavisi ya da özel klinik grup | |

## Hedefli doğrulama (kanıt protokolü Katman 1 ve 3)

| Hedef | Kimlik | Sonuç |
|---|---|---|
| VITAL omega-3 | PMID 30415637 | Dahil (önceki kayıt) |
| ASCEND | PMID 30146932 | Dahil: kalp-damar kartına eklendi (RKÇ, n = 15.480, diyabetli) |
| STRENGTH | PMID 33190147 | Dahil: reçeteli yüksek doz kartı (takviyeye genellenemez) |
| REDUCE-IT | PMID 30415628 | Dahil: reçeteli yüksek doz kartı (takviyeye genellenemez; üretici finansmanı not edildi) |
| DO-HEALTH | PMID 33170239 | Özet okundu: omega-3 kolunda 6 sonuçta anlamlı fark yok; balık tüketimine göre grup ayrımı (D1-5) için veri vermiyor |

## Kurul için açık sorular

- Balık tüketimine göre grup ayrımı (v0.4 D1-5) için uygun RKÇ alt grup analizi var mı? (VITAL balık tüketimi alt grubu tam metinde)
- REDUCE-IT plasebo (mineral yağ) tartışmasının kaynakla eklenmesi
