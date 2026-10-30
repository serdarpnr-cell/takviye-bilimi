# Çinko · arama kaydı

Tarih: 2026-10-30 · Araçlar: PubMed E-utilities (esearch, esummary, efetch), NCBI API anahtarıyla. Ham yanıtlar: `data/ham/arama/cinko.json` (git'e girmez).

## Sistematik arama (v0.4 D4)

```
"Zinc"[Mesh] AND "Common Cold"[Mesh] AND (systematic review[pt] OR meta-analysis[pt])
```

Sonuç sayısı: **13** (2026-10-30). Ön eleme başlık ve PubMed yayın türüne göre yapıldı; özet okunarak doğrulanması ve tam metin değerlendirmesi kurulun ikinci elemesidir.

### PRISMA akış sayıları

| Aşama | Sayı |
|---|---|
| Veri tabanında tanımlanan kayıt | 13 |
| Yinelenen kayıt (çıkarılan) | 0 |
| Başlık/özet taranan | 13 |
| Başlık/özet aşamasında elenen (ön eleme: AI) | 11 (D3: 8, D4: 2, D5: 1) |
| Tam metin değerlendirmesine aday | 2 |
| Tam metin değerlendirilen (kurul) | — |
| Kartta kullanılan | kurul tam metin elemesinden sonra |

### Başlık/özet eleme tablosu

Gerekçe kodları: **DH** dahil (tam metin aşamasına) · **D1** popülasyon kapsam dışı (belirli hastalığın tedavisi, hastane/yoğun bakım, bebek maması) · **D2** sonuç alanı kapsam dışı ya da ara ölçüm · **D3** daha güncel sürümü var / geri çekilmiş · **D4** çalışma türü uygun değil (gözlemsel, yöntem makalesi, anlatı) · **D5** müdahale takviye değil ya da başka maddelerle karışık.

| PMID | Yıl | Başlık | Ön eleme: AI | İkinci eleme: kurul |
|---|---|---|---|---|
| 38719213 | 2024 | Zinc for prevention and treatment of the common cold. | dahil (DH) Cochrane 2024, en güncel sürüm: iki kartta kullanıldı | |
| 36097354 | 2023 | Pitfalls in choosing data examples for methodological work: Bayesian approaches to a fixed effects meta-analys | hariç (D4) Yöntem makalesi | |
| 32342851 | 2020 | Zinc Supplementation Reduces Common Cold Duration among Healthy Adults: A Systematic Review of Randomized Cont | dahil (DH) Sağlıklı yetişkinlerde süre: mikro besin RKÇ derlemesi 2020 (kurul değerlendirmeli) | |
| 25924708 | 2015 | WITHDRAWN: Zinc for the common cold. | hariç (D3) Geri çekilmiş Cochrane sürümü | |
| 23775705 | 2013 | Zinc for the common cold. | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |
| 22566526 | 2012 | Zinc for the treatment of the common cold: a systematic review and meta-analysis of randomized controlled tria | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |
| 21328251 | 2011 | Zinc for the common cold. | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |
| 20690364 | 2009 | Is intranasal zinc effective and safe for the common cold? A systematic review and meta-analysis. | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |
| 17636670 | 2007 | WITHDRAWN: Zinc for the common cold. | hariç (D3) Geri çekilmiş Cochrane sürümü | |
| 16291073 | 2005 | Non-antibiotic treatments for upper-respiratory tract infections (common cold). | hariç (D5) Antibiyotik dışı tedavilerin genel derlemesi | |
| 15499830 | 2004 | Zinc lozenges: cold cure or candy? Solution chemistry determinations. | hariç (D4) Laboratuvar kimyası çalışması | |
| 10796643 | 2000 | Zinc for the common cold. | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |
| 9361579 | 1997 | A meta-analysis of zinc salts lozenges and the common cold. | hariç (D3) Cochrane 2024 sürümüyle güncellendi | |

## Hedefli doğrulama (kanıt protokolü Katman 1 ve 3)

| Hedef | Kimlik | Sonuç |
|---|---|---|
| Cochrane 2024 | PMID 38719213 | Dahil (34 çalışma, 8.526 kişi) |
| NIH ODS çinko (sağlık profesyoneli) | ods.od.nih.gov | Genel bilgi ve etkileşim (önceden doğrulanmış) |
| EFSA üst sınır özeti | EFSA 2025 | Yetişkinde 25 mg/gün |

## Kurul için açık sorular

- Summary of findings tablosundan 100 kişide olay sayıları
- Tedavi çalışmalarındaki dozların EFSA üst sınırını aşmasının kartta nasıl gösterileceği
