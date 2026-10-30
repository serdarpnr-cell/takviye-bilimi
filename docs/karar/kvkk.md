# Karar paketi C1 · KVKK

Tarih: 2026-10-30 · Hazırlayan: geliştirme (Claude Code) · Durum: **hukuk onayına**

Bu belge hukuki görüş değildir. Hukuki sonuç yazılmadı; her karar "hukuk onayına" bırakıldı. Kaynak: `docs/KVKK_KONTROL.md` (K1–K6).

## Kodda kanıt: sağlık verisi yalnızca anlık işlenir

| İddia | Kanıt |
|---|---|
| İstek içeriği diske yazılmaz | `server/` altında tek dosya erişimi `veri._yukle` içindeki **salt okuma** `open(...)` çağrısıdır (`data/*.json`). Yazma çağrısı (`write`, `write_text`, veritabanı) yoktur. |
| İstek içeriği loglanmaz | Sunucuda `logging`/`print` çağrısı yoktur; FastMCP `log_level="WARNING"` (`server/app.py`). Testler: `tests/test_mcp_sunucu.py` (sunucu çıktısında girdi aranır), `tests/test_kisisel_rutin.py::test_kisisel_veri_loglanmaz`. |
| Log satırlarında yaş aralığı dışında profil alanı yok | Uygulama log satırı üretmez. Toplu sayaçlar (`server/sayac.py`, v0.3 Bölüm 11) yalnızca araç adı, hedef kodu, kural tablosundaki madde kimliği, kart durumu, köprü sayısı ve **yaş aralığı** tutar; bellektedir, diske ve loga yazılmaz. Test: `tests/test_v03.py::test_sayaclar_kisisel_veri_tutmaz` (ad, telefon, gebelik, ilaç grubu, cinsiyet, yaşın kendisi ve serbest metin sayaçlarda aranır). |

**Örnek log satırları.** 2026-10-30'da yerel sunucuya gebe, varfarin kullanan 37 yaşında bir test personasıyla `kisisel_rutin`, yakınma metniyle `sikayet_yolu` ve hatalı girdili bir çağrı gönderildi. Sunucunun stdout/stderr çıktısı **0 satır** oldu (hatalı girdi de loglanmadı). Not: Render'ın kendi erişim logları (IP, zaman, yol) bu kapsamın dışındadır; bkz. K3.

## Kararlar

### K1 · Sağlık verisinin anlık işlenmesi
| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Aydınlatma metni + profil alanları isteğe bağlı kalır (bugünkü tasarım) | Açık rıza gerekiyorsa eksik kalır | Düşük (metin) | 1 hafta |
| B. A + sağlık alanları (gebelik, ilaç grubu, yakınma) için açık rıza adımı | Kullanım sürtünmesi; MCP istemcilerinde rıza akışı standart değil | Orta | 3–4 hafta |
| C. Sağlık alanlarını sunucudan kaldırıp yalnızca genel bilgi vermek | Güvenlik uyarıları (varfarin, gebelik) kişiselleştirilemez | Orta, ürün değeri düşer | 2 hafta |

Öneri: **A**, hukuk açık rızayı zorunlu görürse B. Gerekçe: veri saklanmıyor ve loglanmıyor; alanlar isteğe bağlı. Onay: Hukuk + KVKK sorumlusu.

### K2 · Barındırma yeri ve yurt dışı aktarım
`render.yaml`'da `region` alanı **yok**; bölge Render panelinde seçilen değerdir. Render belgelerinde varsayılan bölgenin Oregon (ABD) olduğu bilinir, ancak bu oturumda Render'a erişilemediği için **doğrulanmadı**; panelden kontrol edilmeli.

Soru (hukuka): Sunucu ABD'de çalışırsa, istek sırasında anlık işlenen sağlık verisi KVKK m.9 kapsamında yurt dışı aktarım sayılır mı; sayılırsa hangi dayanak kullanılır?

| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Render AB bölgesi (Frankfurt) | Yine yurt dışı; ABD'ye göre gecikme düşer | Ücretli plan farkı yok, yeniden kurulum | 1 gün |
| B. Türkiye'de barındırma (yerli bulut / Orzax altyapısı) | Aktarım sorusu ortadan kalkar; işletme yükü artar | Orta–yüksek | 2–4 hafta |
| C. Bugünkü bölge + aktarım dayanağı (hukukun belirleyeceği) | Hukuki | Düşük teknik | Hukuka bağlı |

Öneri: hukuk kararını bekle; teknik olarak en hızlı adım A, en temiz B. Onay: Hukuk + BT.

### K3 · Platform logları
| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Render log saklama süresini en kısaya ayarla, erişimi kısıtla | IP + zaman yine tutulur | Düşük | 1 gün |
| B. Önüne kendi ters vekil sunucumuz (IP maskeleme) | Ek bileşen | Orta | 1–2 hafta |
| C. Türkiye'de barındırmada log politikası Orzax'ta | K2-B'ye bağlı | — | — |

Öneri: **A** hemen; K2 kararına göre C. Onay: KVKK sorumlusu + BT.

### K4 · Sohbet içeriği (Claude / ChatGPT sağlayıcısı)
| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Aydınlatma metninde açıkça yaz: sohbet içeriği sağlayıcıya gider, bu sunucunun kontrolünde değil | — | Düşük | 1 hafta |
| B. A + araç açıklamalarında "değeri sohbete yazmayın" uyarısı (tahlil kartı zaten söylüyor) | Model uyarıyı iletmeyebilir | Düşük | 1 gün |

Öneri: **A + B**. Onay: Hukuk.

### K5 · Tahlil kartında saklama
| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Saklama yok (bugün) | Kullanıcı değeri her seferinde girer | Yok | — |
| B. Cihazda, açık rızayla, şifreli saklama | Rıza ve şifreleme tasarımı; denetim | Orta | 3 hafta |

Öneri: **A**. Onay: KVKK sorumlusu.

### K6 · Çocuklar (ebeveyn kullanımı)
| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| A. Aydınlatma metnine ebeveyn kullanımı paragrafı | — | Düşük | 1 hafta |
| B. A + 18 yaş altı profilde yanıtlara "ebeveyn ve hekim" notu | Metin yükü | Düşük | 2 gün |

Öneri: **B**. Onay: Hukuk.
