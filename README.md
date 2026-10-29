# Takviye Bilimi · MCP sunucusu (prototip)

Takviye edici gıdalar için Türkçe, markadan bağımsız bir MCP sunucusu. ChatGPT ve Claude içinde çalışır. Orzax tarafından geliştirilmiştir.

> **Prototip.** Ürün, marka (Marka A, Marka B), beyan ve parti analizi verileri temsilidir. Gerçek etiket, regülasyon onayı veya medikal kurul görüşü yerine geçmez. EFSA üst sınır değerleri henüz kaynaktan doğrulanmadı (`data/kurallar.json` içinde `dogrulandi: false`). Takviye edici gıdalar ilaç değildir.

- Python + resmi MCP Python SDK (`mcp` 1.x, `FastMCP`)
- Taşıma: Streamable HTTP, adres `http://127.0.0.1:8000/mcp`
- Durumsuz (stateless) ve JSON yanıtlı; oturum ya da kullanıcı verisi tutulmaz

## Araçlar

| Araç | Girdi | Ne döndürür |
|---|---|---|
| `urun_rehberi` | `urun` | Etken madde miktarları ("bu üründeki miktar" bloğu: etiket miktarı ve EFSA değeri, yorum yok), etiketteki kullanım, yaş sınırı, etiket uyarıları, onaylı beyanlar, ne beklememeli, menşe, şeffaflık rozeti. Belirsiz adda adayları, bulunamazsa kataloğu sıralama ölçütüyle döndürür. |
| `parti_analizi` | `karekod_veya_parti_no` | Karekod URL'si, GS1 metni (`(10)` alanı) ya da parti numarasından yayımlanmış analiz. |
| `kisisel_rutin` | `yas`, `cinsiyet`, `evre`, `ilac_grubu[]`, `mevcut_urunler[]`, `diger_urun_icerikleri[]` | Tekrar eden etken madde, EFSA üst sınırı karşılaştırması, etiket uyarıları ve yaş sınırı, etkileşim/zamanlama notları, hekime sorulacak sorular. Doz önermez. |
| `yasam_karnesi` | `cevaplar` (6 alan), isteğe bağlı `yas` | 6 soruluk testin karnesi (0–12 puan) ve en fazla 3 hedef. Cevaplar eksikse soruları döndürür. |

Her yanıtta şu alanlar bulunur: `uyari` ("Takviye edici gıdalar ilaç değildir. Kişisel kullanım miktarı ve tedavi için hekiminize danışın."), `gelistirici` ve `veri_notu`.

Tüm araçlar `readOnlyHint: true` olarak işaretlidir; hiçbir şey yazmaz, dışarıya istek atmaz.

### Gizlilik

- Sunucu girdileri yalnızca yanıtı üretmek için işler; saklamaz, loglamaz.
- Log düzeyi `WARNING`; araç argümanları hiçbir düzeyde loglanmaz (testlerle kontrol edilir).
- `ilac_grubu` ilaç adı değil, grup ister (ör. `kan_sulandirici_varfarin`, `tiroid_hormonu`).

## Klasör yapısı

```
data/
  urunler.json            # 6 Ocean ürünü + 2 temsili rakip
  kurallar.json           # EFSA üst sınırları, etkileşim kuralları, ilaç grupları
  beyanlar/beyanlar.json  # onaylı sağlık beyanları (temsili; regülasyon onayı bekliyor)
server/
  veri.py                 # veri yükleme, birim çevirme, arama
  araclar.py              # araçların iş mantığı (saf fonksiyonlar)
  app.py                  # FastMCP sunucusu ve araç tanımları
tests/                    # her araç için test + MCP protokol ve HTTP testleri
docs/KANIT_PROTOKOLU.md
```

Ürün düzeyindeki etki ifadeleri yalnızca `data/beyanlar/` altındaki beyanlardan gelir (`urunler.json` beyan kimliklerini tutar).

## Kurulum

Python 3.10+ gerekir.

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

> Not: `mcp` 2.x sürümünde `FastMCP`'nin adı `MCPServer` oldu. Bu proje istenen `FastMCP` API'si için `mcp>=1.26,<2` kullanır.

## Testler

```bash
.venv/bin/python -m pytest -v
```

Kapsam: dört aracın her biri için ayrı test dosyası; veri bütünlüğü ve yasaklı ifade taraması (`tests/test_veri.py`); bellek içi MCP protokol testi ve sunucuyu gerçekten başlatıp Streamable HTTP üzerinden dört aracı çağıran test (`tests/test_mcp_sunucu.py`).

## Sunucuyu yerelde başlatma

```bash
.venv/bin/python -m server
```

Sunucu `http://127.0.0.1:8000/mcp` adresinde dinler. Ortam değişkenleri:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `TB_HOST` | `127.0.0.1` | Dinlenecek adres |
| `TB_PORT` | `8000` | Port |
| `TB_ALLOWED_HOSTS` | boş | Yerel adreslere ek olarak kabul edilecek `Host` başlıkları, virgülle (ör. ngrok adresi) |

DNS rebinding koruması açıktır: yalnızca yerel adresler ve `TB_ALLOWED_HOSTS` içindekiler kabul edilir.

## MCP Inspector ile deneme

Sunucu çalışırken ikinci bir terminalde (Node.js 18+ gerekir):

```bash
npx -y @modelcontextprotocol/inspector
```

Tarayıcıda açılan arayüzde:

1. **Transport Type:** `Streamable HTTP`
2. **URL:** `http://localhost:8000/mcp`
3. **Connect** → **Tools** → **List Tools**, sonra bir araç seçip çalıştır.

Denemek için örnek girdiler:

- `urun_rehberi` → `urun`: `Ocean D3K2 Damla`
- `parti_analizi` → `karekod_veya_parti_no`: `https://takviyebilimi.example/k/D3K2-24A117`
- `kisisel_rutin` → `yas`: 41, `cinsiyet`: `kadin`, `ilac_grubu`: `["kan_sulandirici_varfarin"]`, `mevcut_urunler`: `["Ocean D3K2 Damla", "Ocean Magnezyum"]`, `diger_urun_icerikleri`: `[{"ad": "Multivitamin", "icerikler": [{"etken_madde": "magnezyum", "miktar": 100, "birim": "mg"}]}]`
- `yasam_karnesi` → `cevaplar`: `{"hareket_gun": 1, "uyku_saat": 6, "sebze_meyve_porsiyon": 2, "balik_haftalik": 0, "sigara": "hayir", "stres": "sik"}`

Arayüz yerine komut satırından:

```bash
npx -y @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method tools/list
```

```bash
npx -y @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method tools/call --tool-name kisisel_rutin --tool-arg yas=41 --tool-arg cinsiyet=kadin --tool-arg 'ilac_grubu=["kan_sulandirici_varfarin"]' --tool-arg 'mevcut_urunler=["Ocean D3K2 Damla","Ocean Magnezyum"]'
```

## ngrok ile HTTPS adresi açma

Claude ve ChatGPT, sunucuya kendi bulutlarından bağlanır; `localhost` adresine ulaşamazlar. Bu yüzden herkese açık bir HTTPS adresi gerekir.

1. [ngrok](https://ngrok.com/download) kur ve hesabındaki authtoken ile bağla:

   ```bash
   ngrok config add-authtoken <AUTHTOKEN>
   ```

2. ngrok panelinde (Domains) hesabına tanımlı ücretsiz sabit adresi öğren, ör. `ornek-ad.ngrok-free.app`. Sabit adres, sunucuyu her başlattığında connector ayarını değiştirmeni gerektirmez.

3. Sunucuyu bu adrese izin vererek başlat:

   ```bash
   TB_ALLOWED_HOSTS=ornek-ad.ngrok-free.app .venv/bin/python -m server
   ```

4. Başka bir terminalde tüneli aç:

   ```bash
   ngrok http 8000 --url=https://ornek-ad.ngrok-free.app
   ```

5. Kontrol et (Inspector'da URL olarak da kullanılabilir):

   ```bash
   npx -y @modelcontextprotocol/inspector --cli https://ornek-ad.ngrok-free.app/mcp --transport http --method tools/list
   ```

MCP adresi: `https://ornek-ad.ngrok-free.app/mcp`. Sabit adres kullanmazsan ngrok'un verdiği rastgele adresi `TB_ALLOWED_HOSTS` içine yazıp sunucuyu yeniden başlat. `TB_ALLOWED_HOSTS` boşsa sunucu ngrok'tan gelen istekleri `Invalid Host header` hatasıyla reddeder.

> Prototipte kimlik doğrulama yoktur. Tüneli yalnızca deneme süresince açık tut.

## Claude'a custom connector olarak bağlama

Custom connector'lar claude.ai'nin Free, Pro, Max, Team ve Enterprise planlarında kullanılabilir (Free planda tek connector). Team ve Enterprise'da connector'ı önce bir kuruluş sahibi eklemelidir.

1. claude.ai → **Settings** → **Connectors**.
2. **Add custom connector**.
3. **Name:** `Takviye Bilimi`, **Remote MCP server URL:** `https://ornek-ad.ngrok-free.app/mcp`. OAuth alanlarını boş bırak.
4. **Add** ile kaydet.
5. Yeni bir sohbette mesaj kutusundaki **+** (Search and tools) menüsünden **Takviye Bilimi**'nin açık olduğunu kontrol et.
6. Dene: "Ocean D3K2 Damla'nın etiketinde ne yazıyor?" veya "41 yaşındayım, varfarin kullanıyorum; Ocean D3K2 Damla ve Ocean Magnezyum'u birlikte kullanıyorum, kontrol eder misin?"

Claude Desktop'ta da aynı connector görünür (Settings → Connectors).

## ChatGPT'ye Developer Mode ile bağlama

Developer Mode, ChatGPT web sürümünde Plus, Pro, Business, Enterprise ve Edu planlarında açılabilir. Business/Enterprise'da yöneticinin izin vermesi gerekebilir.

1. chatgpt.com → **Settings** → **Apps & Connectors** → **Advanced settings** → **Developer mode**'u aç.
2. **Apps & Connectors** sayfasına dön → **Create**.
3. **Name:** `Takviye Bilimi`, **Description:** "Takviye ürünlerinin etiket bilgisi, parti analizi, rutin kontrolü ve yaşam karnesi", **MCP Server URL:** `https://ornek-ad.ngrok-free.app/mcp`, **Authentication:** `No authentication`.
4. "I trust this application" kutusunu işaretle → **Create**. Araç listesi görünmelidir.
5. Yeni sohbette mesaj kutusundaki **+** → **More** → **Developer mode** → **Takviye Bilimi**'ni seç.
6. Aynı örnek sorularla dene. Araçlar salt okuma olarak işaretli olduğundan ChatGPT her çağrıda onay istemez.

Araç listesi değişirse uygulama sayfasındaki **Refresh** ile güncelle.

Menü adları platformlarda sık değişebilir; adım bulunamazsa ilgili yardım sayfasına bak: [Claude custom connectors](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp), [ChatGPT developer mode](https://platform.openai.com/docs/guides/developer-mode).

## Açık konular

- EFSA değerleri kaynaktan doğrulanıp `url` ve `erisim_tarihi` alanları doldurulmalı (kanıt protokolü, kural 1).
- Demir için 18 yaş altı EFSA değerleri eklenmedi.
- Etkileşim kuralları ve yaşam karnesi eşikleri medikal kurul onayı bekliyor.
- Beyan metinleri regülasyon ekibinin onayını bekliyor.
- `calismalarda_kullanilan_dozlar` alanı kanıt kartları hazırlanınca dolacak.
