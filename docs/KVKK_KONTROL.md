# KVKK kontrol listesi · Faz 3 kapısı

Tarih: 2026-10-30 · Hazırlayan: geliştirme (Claude Code) · Durum: **hukuk incelemesi bekliyor**

Bu belge hukuki görüş değildir. Kodun bugün gerçekte ne yaptığını veri akışı olarak tarif eder ve karar gereken noktaları işaretler. Kararlar hukuk ve KVKK sorumlusu tarafından verilir.

## 1. Sunucunun işlediği veriler

Sunucu durumsuzdur (`stateless_http=True`): her istek ayrı işlenir, oturum ya da profil tutulmaz. Veritabanı yoktur.

| Araç | Kullanıcıdan gelen alanlar | Sağlık verisi niteliği | Sunucuda ne olur |
|---|---|---|---|
| `urun_rehberi` | ürün adı, isteğe bağlı yaş | Düşük | Yanıt üretilir, saklanmaz |
| `etken_madde_rehberi` | madde adı; isteğe bağlı yaş, cinsiyet, gebelik/emzirme, sigara, ilaç grubu | **Var** (gebelik, ilaç grubu) | Yanıt üretilir, saklanmaz |
| `kisisel_rutin` | yaş, cinsiyet, gebelik/emzirme, ilaç grubu, kullanılan ürünler ve içerikleri | **Var** | Yanıt üretilir, saklanmaz |
| `yasam_karnesi` | hareket, uyku, beslenme, balık, tütün, stres cevapları; isteğe bağlı yaş | **Var** (tütün, stres) | Yanıt üretilir, saklanmaz |
| `sikayet_yolu` | yakınma metni, isteğe bağlı yaş ve cinsiyet | **Var** (yakınma) | Yanıt üretilir, saklanmaz |
| `urun_karsilastir` | ürün adları, isteğe bağlı yaş | Düşük | Yanıt üretilir, saklanmaz |
| `parti_analizi` | parti numarası ya da karekod içeriği | Yok | Yanıt üretilir, saklanmaz |
| `tahlil_goster` | yalnızca tahlil adı (ör. "ferritin") | Yok: **değer alınmaz** | Genel bilgi döner |
| `katalog_sayfasi` | madde adı, sayfa, isteğe bağlı yaş (kartın kendisi çağırır) | Düşük | Yanıt üretilir, saklanmaz |

İlaç adı istenmez; yalnızca ilaç grubu (ör. "kan sulandırıcı") seçilir.

## 2. Teknik önlemler (uygulanmış)

- [x] Kalıcı depolama yok: veritabanı, dosya yazımı ya da önbellekte kullanıcı girdisi yok.
- [x] Log düzeyi `WARNING`; araç argümanları hiçbir düzeyde loglanmaz (`tests/test_kisisel_rutin.py::test_kisisel_veri_loglanmaz`, `tests/test_mcp_sunucu.py` sunucu çıktısında girdi aranır).
- [x] DNS rebinding koruması açık; yalnızca izinli `Host` başlıkları kabul edilir.
- [x] Tahlil değeri sunucuya hiç gelmez: `tahlil_goster` aracının değer parametresi yoktur (`tests/test_faz3.py::test_tahlil_aracinin_deger_parametresi_yoktur`).
- [x] Tahlil kartı değeri dışarı göndermez ve saklamaz: kart betiğinde `localStorage`, `sessionStorage`, `indexedDB`, `fetch`, `tools/call`, `ui/message` yok (`test_tahlil_karti_degeri_gondermez_ve_saklamaz`); tarayıcı denetimi kartın yalnızca başlatma ve boyut mesajı gönderdiğini, girilen değerin hiçbir mesajda geçmediğini doğrular (`tests/test_kart_cizimi.py`).
- [x] Görsel kartlar dış ağa çıkmaz; dış betik, görsel ya da yazı tipi yüklemez.
- [x] Yanıtlarda `gizlilik` alanı, girdinin saklanmadığını ve loglanmadığını kullanıcıya söyler.

## 3. Karar bekleyen noktalar

| # | Konu | Neden önemli | Öneri |
|---|---|---|---|
| K1 | **Sağlık verisinin anlık işlenmesi** | Saklanmasa da gebelik, ilaç grubu, yakınma gibi alanlar sunucuda işlenir; KVKK'da işleme sayılabilir | Aydınlatma metni hazırlanması; açık rıza gerekip gerekmediğine hukukun karar vermesi |
| K2 | **Barındırma yeri ve yurt dışı aktarım** | Deneme sunucusu Render'da (ücretsiz plan); veri merkezinin ülkesi bu belgede doğrulanmadı | Yayın sunucusunun yeri netleşmeli; yurt dışıysa aktarım dayanağı belirlenmeli |
| K3 | **Platform logları** | Render ve ngrok gibi aracılar IP ve istek meta verisi tutabilir; uygulama logu bunları kapsamaz | Yayın ortamında erişim logu politikası ve saklama süresi |
| K4 | **Sohbet içeriği** | Kullanıcının sohbete yazdığı her şey (tahlil değeri dahil) Claude veya ChatGPT sağlayıcısına gider; bu sunucunun kontrolünde değildir | Aydınlatma metninde açıkça yazılmalı; tahlil kartı değeri sohbete yazmaya gerek olmadığını söylüyor |
| K5 | **Tahlil kartında saklama** | Tasarım "saklama ancak açık rızayla" diyor; bugün hiç saklama yok | Saklama istenirse açık rıza akışı ve cihazda şifreleme ayrıca tasarlanmalı; bugünkü öneri: saklamamak |
| K6 | **Çocuklar** | Yaş alanı 0–120 kabul eder; ebeveyn çocuğu için sorabilir | Aydınlatma metninde ebeveyn kullanımı |

## 4. İmza

| Rol | Ad | Karar | Tarih |
|---|---|---|---|
| KVKK sorumlusu | | ☐ Uygun ☐ Düzeltme gerekli | |
| Hukuk | | ☐ Uygun ☐ Düzeltme gerekli | |
