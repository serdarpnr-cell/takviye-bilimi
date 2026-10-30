# Claude canlı test kiti (v0.4 A4)

Sahibi: Serdar Pınar · Hazırlayan: geliştirme · Sürüm: sunucu 0.3.0

Claude Code kartların çizimini göremez; MCP Apps kartlarını metin olarak alır. Bu kit, kartların claude.ai web ve Claude masaüstünde gerçekten nasıl göründüğünü ve ne kadar sürede açıldığını elle ölçmek içindir. Her oturumda **yeni sohbet** açın; bağlayıcı (Takviye Bilimi) açık olsun.

Kayıt: her hücreye ✓ / ✗ ve kısa not. Sonuçları `docs/olcumler/<tarih>_canli.md` olarak kaydedin.

---

## 1. Kart matrisi

7 kart × 2 istemci × 2 tema = 28 hücre. Her kartı iki yoldan tetikleyin: **(a)** "Takviye Bilimi ile …" ve **(b)** "/takviye …" (eklenti kuruluysa).

| # | Kart | Tetikleyen mesaj (a / b) | Beklenen görünüm |
|---|---|---|---|
| K1 | Kanıt (`kanit`) | (a) "Takviye Bilimi ile D vitamininin kanıt kartını göster, 42 yaşındayım." (b) "/takviye D vitamini kanıt kartı, 42 yaş" | Başlık bandı "Takviye Bilimi"; "Taslak · kurul onayı bekliyor" rozeti; "Ne biliyoruz" altında 3 sonuç kartı; solunum kartında **"Küçük fayda"** rozeti ve 100 noktalık iki dizi (62 / 61); "Güvenlik tavanı" 100 µg; katalogda 5 ürün, ilk sırada Ocean Dim Ultra **yok**; "Diğer ürünler" düğmesi çalışır |
| K2 | Ürün (`urun`) | (a) "Takviye Bilimi ile 8 yaşındaki kızım için Ocean Vitamin D3 400 IU Sprey etiketine bak." (b) "/takviye Ocean Vitamin D3 400 IU Sprey, 8 yaş" | Rozette "Yaş: 2 yaş ve üzeri"; **yaş uyarısı kutusu yok**; çubuk altında "Porsiyonda 10 µg: 50 µg olan EFSA yaş grubu üst sınırının %20'si" |
| K2b | Ürün, K vitamini | (a) "Takviye Bilimi ile Ocean D3K2 Damla etiketini göster." | Turuncu "K vitamini — varfarin: hekime danışın" kutusu; bileşimde "K vitamini formu: MK-7 (menakinon-7)" rozeti; beyanlarda "· Sayfada belirtilmemiş" **yazmıyor** |
| K3 | Kıyas (`kiyas`) | (a) "Takviye Bilimi ile D vitamini ürünlerini içeriğe göre kıyasla." (b) "/takviye D vitamini ürünlerini kıyasla" | Masaüstünde tablo, ilk sütun yatay kaydırmada sabit; form çipleri (Tümü, Damla, Sprey…) süzüyor; her satırda EFSA çubuğu ve kırmızı sınır çizgisi; ürün adına tıklayınca ürün sayfası açılıyor; dar pencerede (≤ 480 px) kart listesi |
| K3b | Kıyas, kapsam | (a) "Takviye Bilimi ile Solgar D3'ü Ocean D3 ile kıyasla." | Kapsam mesajı: "Katalog şu an yalnızca Orzax ürünlerini içeriyor; Solgar için etiket verisi yok…"; aday ürün **listelenmiyor** |
| K4 | Rutin (`rutin`) | (a) "Takviye Bilimi ile rutin kontrolü: annem 70 yaşında, varfarin kullanıyor, Ocean D3K2 Damla alıyor." (b) "/takviye rutin: 70 yaş kadın, varfarin, D3K2 Damla" | Yığılmış çubuk ve EFSA çizgisi; varfarin etkileşim rozeti; hekime sorulacaklar listesi |
| K5 | Karne (`karne`) | (a) "Takviye Bilimi ile yaşam karnemi çıkar." (b) "/takviye yaşam karnesi" | Seçenekli form; Claude soruları iki adımda (4 + 2) ve seçenekli sorar; gönderince puan kartı |
| K6 | Parti (`parti`) | (a) "Takviye Bilimi ile parti DEMO-0001 analizine bak." | "DEMO" etiketi her yerde; etiketteki / ölçülen çubukları |
| K7 | Tahlil (`tahlil`) | (a) "Takviye Bilimi ile ferritin tahlil görünümünü aç." | Değer ve referans aralığı kartta girilir; değer sohbete gitmez |

Her hücre için ayrıca **boş sonuç** kutusunu deneyin ve kaydedin:

| Kart | Boş sonuç mesajı | Beklenen |
|---|---|---|
| Kanıt | "Takviye Bilimi ile C vitamininin kanıt kartını göster." | "Kanıt kartı hazırlanıyor" ve NIH ODS bağlantısı; ürün listesi yok |
| Ürün | "Takviye Bilimi ile Solgar Vitamin D3 etiketini göster." | Kapsam mesajı; adaylar yalnızca D vitamini içeren Orzax ürünleri |
| Kıyas | "Takviye Bilimi ile çinko ürünlerini kıyasla." | "Kanıt kartı hazırlanıyor; kart hazır olana kadar ürün listesi ve kıyas gösterilmez" |
| Rutin | "Takviye Bilimi ile rutinime bak: 30 yaş, ürün yok." | Boş tablolar, hata yok |
| Parti | "Takviye Bilimi ile parti XYZ-123 analizine bak." | "Yayımlanmış analiz bulunamadı" |
| Tahlil | "Takviye Bilimi ile kolesterol tahlil görünümü." | "Henüz yok; hazır olanlar …" |

Tablo (her hücre: ✓/✗ + not):

| Kart | Web · açık | Web · koyu | Masaüstü · açık | Masaüstü · koyu |
|---|---|---|---|---|
| K1 Kanıt | | | | |
| K2 Ürün | | | | |
| K3 Kıyas | | | | |
| K4 Rutin | | | | |
| K5 Karne | | | | |
| K6 Parti | | | | |
| K7 Tahlil | | | | |

Kart dayanıklılığı (v0.3 Ek 11): kart açıkken ağ bağlantısını kesip yeni soru sorun → 5 sn sonra kart içinde görünür hata metni beklenir. Hata ayıklama: istemcide kart iframe adresine `?debug` eklenebiliyorsa host mesajları tarayıcı konsoluna yazılır.

## 2. Kronometre protokolü

1. Yeni sohbet, bağlayıcı açık. Telefon kronometresini hazırlayın.
2. Mesajı gönderdiğiniz an başlatın.
3. Kartın **ilk boyandığı an** (başlık bandı "Takviye Bilimi" göründüğünde) durdurun.
4. Aynı kart için 5 ölçüm alın (her biri yeni sohbette), medyanı yazın.
5. İlk ölçümden önce sunucu 15 dk boşta kaldıysa o ölçümü "soğuk" diye ayrı işaretleyin.

| Kart | 1 | 2 | 3 | 4 | 5 | Medyan | Hedef |
|---|---|---|---|---|---|---|---|
| Kanıt | | | | | | | < 3 sn |
| Ürün | | | | | | | < 3 sn |
| Kıyas | | | | | | | < 3 sn |
| Rutin | | | | | | | < 3 sn |
| Karne | | | | | | | < 3 sn |

Sunucu tarafı bütçe (`scripts/gecikme_olc.py`): sıcakken tools/call + resources/read p95 < 1,5 sn. Kalan süre Claude'un düşünmesi ve host çizimidir.

## 3. Kartlı araç kısıtı testi

claude.ai'da kartlı araçlar ancak kullanıcı Takviye Bilimi'ni adıyla anarsa, bağlantı önerisinden seçerse ya da kalıcı tercih varsa doğrudan çağrılıyor. Aşağıdaki 5 mesajı **araç ve bağlayıcı adı anmadan**, yeni sohbette gönderin.

| # | Mesaj | Kapı aracı çağrıldı mı? (hangisi) | Bağlantı önerisi gösterildi mi? | Hiçbir şey yapmadı mı? | Köprü sorusu iletildi mi? | "Evet" → kart açıldı mı? |
|---|---|---|---|---|---|---|
| 1 | Kış geldi, hangi vitaminleri almam gerek? | | | | | |
| 2 | Hep yorgunum, ne kullanayım? | | | | | |
| 3 | D vitamini işe yarıyor mu? | | | | | |
| 4 | Bu ürün nasıl kullanılır? Ocean D3K2 Damla | | | | | |
| 5 | D vitamini markalarını kıyasla | | | | | |

Satır 4, v0.3'teki açık karar içindir (urun_rehberi kartlı kalsın mı): bağlantı önerisine takılma oranı yüksekse v0.4'te kartsız kapı moduna alınması önerilir.

## 4. Ekran görüntüsü kuralları (bağlayıcı dizini başvurusu)

- PNG, en az 1000 px genişlik.
- Yalnızca uygulama yanıtı (kart) kırpılmış; kullanıcının istemi **görünmeyecek**.
- Açık tema. 3–5 görüntü: karne, kanıt, ürün, kıyas ve rutin kartları.
- Kişisel veri ya da gerçek kişi adı içeren mesaj kullanılmaz; yukarıdaki test personaları kullanılır.
- Dosya adı: `<kart>_acik_<genislik>px.png`; `docs/dizin_goruntuleri/` altına konur.
