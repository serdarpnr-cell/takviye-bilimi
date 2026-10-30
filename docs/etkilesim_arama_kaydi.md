# Etkileşim kuralları · arama kaydı

Tarih: 2026-10-30 · Araçlar: NIH ODS sağlık profesyoneli bilgi sayfaları (`scripts/kaynak_dogrula.py` ile çekildi), PubMed E-utilities (NCBI API anahtarıyla).
Ham yanıtlar: `data/ham/` (git'e girmez). Kurallar: `data/kurallar.json` → `etkilesimler`.

## Kural başına dayanak

| Kural | Kaynak | Mesaj değişti mi |
|---|---|---|
| `k_vitamini_varfarin` | NIH ODS K vitamini (HP): ciddi etkileşim; alımdaki ani değişim etkiyi artırır ya da azaltır | Hayır |
| `omega3_kan_sulandirici` | NIH ODS Omega-3 (HP): yüksek miktarda pıhtılaşma süresini uzatabilir, antiplatelet etki; prospektüsler INR izlemi ister | Evet: neden ve INR izlemi eklendi |
| `demir_kalsiyum` | NIH ODS Demir (HP): kalsiyum demirin emilimini azaltabilir; farklı saatlerde alınması önerilir | **Evet**: "birbirinin emilimini" → "kalsiyum demirin emilimini"; kaynaksız "en az 2 saat" kaldırıldı, "günün farklı saatleri" |
| `demir_tiroid` | NIH ODS Demir (HP); Skelin 2017 derlemesi (PMID 28153426, demir sülfat) | Evet: levotiroksin adı ve etki büyüklüğü dili kaynağa göre |
| `magnezyum_tiroid` | ThyroMag 2025 (PMID 41221788, 15 kişilik randomize çapraz farmakokinetik çalışma) | Evet: etkinin demir ve kalsiyumdan zayıf olduğu ve ayrı saat önerisi eklendi |
| `mineral_antibiyotik` | NIH ODS Magnezyum, Çinko, Kalsiyum (HP); demir için tetrasiklin ve minosiklin emilim çalışması (PMID 3838321) ve siprofloksasin farmakokinetiği derlemesi (PMID 37850318) | Evet: antibiyotik grupları (kinolon, tetrasiklin) açık yazıldı |
| `folik_asit_antiepileptik` | NIH ODS Folat (HP): sara ilaçlarının kan düzeyini düşürebilir; kanser tedavisindeki metotreksatla etkileşir; düşük doz metotreksatta yan etkiyi azaltabilir | Evet: iki yönlü bilgi eklendi |

## Aramalar

| Hedef | Sorgu | Sonuç | Karar |
|---|---|---|---|
| Magnezyum–levotiroksin | NIH ODS Magnezyum (HP) sayfası | Levotiroksin geçmiyor | PubMed'e geçildi |
| | `levothyroxine[tiab] AND magnesium[ti]` | 2 | 41221788 dahil; 26854732 hayvan çalışması, elendi |
| Levotiroksin emilimi | `levothyroxine[ti] AND absorption[ti] AND review[pt]` | 6 | 28153426 dahil (demir sülfat ve kalsiyum etkileşimi); diğerleri belirli hasta grupları |
| Demir–tetrasiklin | `iron[ti] AND (tetracycline[ti] OR doxycycline[ti]) AND absorption[ti]` | 7 | 3838321 dahil (özetinde sayılar var); 1975 ve 1974 kayıtlarının özeti yok, 17691587 tek demir formu, elendi |
| Demir–kinolon | `ciprofloxacin[ti] AND (ferrous OR iron)[ti] AND (bioavailability OR absorption OR pharmacokinetics)[ti]` | 28 | 37850318 dahil (kapsam derlemesi); diğerleri laboratuvar ya da çevre çalışması |
| Kinolon–katyon | `quinolone*[ti] AND (iron OR ferrous)[ti] AND interaction*[ti]` | 7 | 1763542 ve 2286594 eski derlemeler, özetleri demiri sayısal anmıyor; dahil edilmedi |

Taranan: 50 kayıt + 7 NIH ODS sayfası · dahil: 4 PubMed kaydı + 7 NIH ODS sayfası.
