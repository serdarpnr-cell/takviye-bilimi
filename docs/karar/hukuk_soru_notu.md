# Karar paketi C3 · Hukuk soru notu

Tarih: 2026-10-30 · Hazırlayan: geliştirme · Durum: **hukuk onayına** · Bu not yorum içermez; soruyu ve bağlamı aktarır.

## Soru

Etken madde düzeyindeki bilimsel kanıt kartlarının, Orzax'ın geliştirdiği ve kataloğunda yalnızca Orzax ürünleri bulunan bir aracın (Takviye Bilimi) içinde sunulması **tanıtım (ticari reklam) sayılır mı**? Sayılırsa hangi koşullarla sunulabilir?

## Bağlam (bugünkü tasarım)

- Kanıt kartları etken madde düzeyindedir; "bu ürün şunu sağlar" demez. Ürüne ait etki ifadesi yalnızca ürün sayfasındaki sağlık beyanlarından, kelimesi kelimesine gelir.
- Ürün listelerinde **sıralama öneri değildir**: önce yalnızca o maddeyi içerenler, sonra porsiyondaki miktar, sonra alfabetik. **Sponsorluk ve fiyat yoktur.**
- **Kartı olmayan maddede ürün listelenmez**; yalnızca katalogdaki ürün sayısı yazılır (tek gösterim kuralı).
- **Katalog yalnızca Orzax ürünlerini içerir**; bu her yanıtta ve araç açıklamalarında yazılıdır. Başka marka sorulduğunda "etiket verisi yok" denir, aday listelenmez.
- Olumsuz sonuçlar ("etkisiz bulundu", "güvenlik sinyali") gizlenmez. Kişiye doz önerilmez; tanı ve tedavi ifadesi yoktur.
- Araç, kullanıcı bir takviye sorusu sorduğunda Claude veya ChatGPT içinde çağrılır; kendiliğinden mesaj göndermez.

## Hukukçunun bakacağı başlıklar

- Takviye Edici Gıdalar Yönetmeliği (Tarım ve Orman Bakanlığı)
- Türk Gıda Kodeksi Beslenme ve Sağlık Beyanları Yönetmeliği ve TİTCK / Bakanlık kılavuz ekleri
- Ticari Reklam ve Haksız Ticari Uygulamalar Yönetmeliği
- Reklam Kurulu kararları (takviye edici gıda ve sağlık beyanı içeren)

## Riski azaltan iki tasarım seçeneği

| Seçenek | Ne değişir | Maliyet | Süre |
|---|---|---|---|
| **1. Kanıt modu: ürün bağlantısı kapalı** | Kanıt kartı, takviye rehberi ve şikâyet yolu yanıtlarında ürün listesi ve ürün sayısı hiç gösterilmez; ürün bilgisi yalnızca kullanıcı ürün adıyla sorduğunda (`urun_rehberi`) ya da açıkça kıyas istediğinde (`karsilastir`) gelir. Sunucuda bir ayarla açılıp kapanır. | Düşük (kod 1–2 gün) | 1 hafta |
| **2. Bağımsız yayın** | Kanıt kartları ayrı, marka içermeyen bir yayın olarak (ör. bağımsız kurul imzasıyla) sunulur; Orzax yalnızca "geliştiren" olarak alt bilgide kalır. Çok markalı katalog hedeflenir. | Orta–yüksek (kurul yapısı, içerik) | 2–3 ay |

Öneri yok: karar hukukun. Onay: Hukuk + Orzax yönetimi.
