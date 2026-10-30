# Karar paketi C5 · TB-24 etiket uyarıları: veri talebi

Tarih: 2026-10-30 · Talep eden: Serdar Pınar (Takviye Bilimi) · Alıcı: Orzax regülasyon / ambalaj ekibi

## Neden

Ürün sayfaları ambalajdaki etiket uyarılarını (ör. "Hamilelik ve emzirme döneminde doktorunuza danışınız", "Çocukların ulaşamayacağı yerde saklayınız", alerjen uyarıları) yayımlamıyor. Takviye Bilimi bugün her ürün kartında "Etiket uyarıları ürün sayfasında yayımlanmıyor; ambalajdaki uyarıları okuyun." notunu gösteriyor. Uyarıların ambalajdaki metinle **birebir** gösterilmesi için kaynak veri gerekiyor. Veri gelene kadar bu not araçlarda kalır.

## İstenen veri

| Sütun | Açıklama | Örnek biçim |
|---|---|---|
| `urun_kodu` | Takviye Bilimi ürün kodu (orzax.com.tr ürün sayfası adresinin son parçası) | `ocean-vitamin-d3k2-damla` |
| `urun_adi` | Ürün adı, sitedeki gibi | `Ocean D3K2 Damla` |
| `uyari_metni_birebir` | Ambalajdaki tek bir uyarı cümlesi, büyük-küçük harf ve noktalama korunarak. Her uyarı ayrı satır. | |
| `ambalaj_revizyon_no` | Metnin alındığı ambalaj/etiket revizyonu | `R03` |
| `tarih` | Revizyonun yürürlük tarihi | `2026-09-15` (YYYY-AA-GG) |

- **Format:** UTF-8 CSV, ilk satır sütun adları; boş şablon `data/etiket_uyarilari/sablon.csv`.
- **Kapsam:** katalogdaki 145 ürünün tamamı; önce D vitamini, K vitamini, demir ve çocuk ürünleri.
- **Güncelleme:** ambalaj revizyonu değiştikçe yeni satırlar (eski revizyon satırları silinmeden).

## Doğrulama ve yayın

`python scripts/etiket_uyarilari_al.py <dosya.csv>` dosyayı denetler (bilinmeyen ürün kodu, ad uyuşmazlığı, boş metin, eksik revizyon, hatalı/ileri tarih, tekrar). Hata varsa hiçbir şey alınmaz. Geçerli dosya `--yaz` ile `data/etiket_uyarilari/uyarilar.json` olur; ürün kartı notu kendiliğinden metinle değişir.

**Onay:** metinlerin ambalajla birebir olduğunu Orzax regülasyon ekibi onaylar (imza ve tarih e-postada).
