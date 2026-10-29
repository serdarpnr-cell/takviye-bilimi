# Takviye Bilimi · MCP sunucusu (prototip)

Takviye edici gıdalar için Türkçe, markalar arasında ayrım yapmayan bir MCP sunucusu. ChatGPT ve Claude içinde çalışır. Orzax tarafından geliştirilmiştir.

> **Prototip.** Ürün bilgileri orzax.com.tr ürün sayfalarından alınmıştır (`scripts/orzax_katalog.py`); katalog şu an yalnızca Orzax ürünlerini içerir. Yayımlanmış parti analizi yoktur. EFSA üst sınırları API'den doğrulanmış EFSA belgelerine bağlıdır; etkileşim kuralları, karne eşikleri ve kanıt kartları medikal kurul onayı bekler. Takviye edici gıdalar ilaç değildir.

- Python + resmi MCP Python SDK (`mcp` 1.x, `FastMCP`)
- Taşıma: Streamable HTTP, adres `http://127.0.0.1:8000/mcp`
- Durumsuz (stateless) ve JSON yanıtlı; oturum ya da kullanıcı verisi tutulmaz

## En kolay deneme yolu (kurulum gerektirmez)

Bilgisayarına bir şey kurmadan, sunucuyu ücretsiz Render servisinde yayına alıp Claude'a bağlayabilirsin. Gerekenler: GitHub hesabı ve claude.ai hesabı.

1. **Kodu ana dala al:** GitHub'da bu deponun Pull requests sekmesinde açık PR'ı aç, **Merge pull request** → **Confirm merge**.
2. **Render hesabı aç:** [render.com](https://render.com) → **Get Started** → **GitHub** ile giriş yap.
3. **Sunucuyu kur:** Render panelinde **New +** → **Blueprint**. GitHub erişimi isterse `takviye-bilimi` deposuna izin ver. Listeden `takviye-bilimi` deposunu seç, **Deploy Blueprint** (ya da **Apply**) düğmesine bas. Ayarlar `render.yaml` dosyasından otomatik gelir.
4. **Bekle:** 3–5 dakika sonra servisin durumu **Live** olur. Servis sayfasının üstünde `https://takviye-bilimi.onrender.com` gibi bir adres görünür (ad doluysa sonuna ek gelebilir).
5. **Claude'a bağla:** claude.ai → **Settings** → **Connectors** → **Add custom connector** → Ad: `Takviye Bilimi`, URL: Render adresinin sonuna `/mcp` ekleyerek yaz (ör. `https://takviye-bilimi.onrender.com/mcp`) → **Add**.
6. **Dene:** Yeni sohbet aç ve sor: "Ocean D3K2 Damla'nın etiketinde ne yazıyor?" Claude aracı kullanmak için izin isterse **Allow** de.

ChatGPT için de aynı adres kullanılır; adımlar aşağıda, "ChatGPT'ye Developer Mode ile bağlama" bölümünde.

Bilmen gerekenler:

- Ücretsiz planda sunucu 15 dakika kullanılmazsa uykuya geçer; ilk soruda uyanması yaklaşık 1 dakika sürer. Claude "bağlanamadı" derse bir dakika sonra tekrar dene.
- Adresi bilen herkes araçları kullanabilir. Sunucu kullanıcı bilgisi saklamaz; yine de adresi yalnızca deneyecek kişilerle paylaş. İş bitince Render'da servisi **Settings** → **Delete Web Service** ile silebilirsin.

## Araçlar

| Araç | Girdi | Ne döndürür |
|---|---|---|
| `urun_rehberi` | `urun` | Etken madde miktarları ("bu üründeki miktar" bloğu: etiket miktarı, beslenme referans değeri ve EFSA değeri, yorum yok), bileşim, etiketteki kullanım, yaş sınırı, ürün sayfasındaki sağlık beyanları, ürün sayfası bağlantısı. Belirsiz adda adayları, bulunamazsa benzer adlı ürünleri alfabetik döndürür. |
| `parti_analizi` | `karekod_veya_parti_no` | Karekod URL'si, GS1 metni (`(10)` alanı) ya da parti numarasını çözer. Katalogda yayımlanmış parti analizi olmadığı için analiz bulunamadığını bildirir; uydurma sonuç döndürmez. |
| `kisisel_rutin` | `yas`, `cinsiyet`, `evre`, `ilac_grubu[]`, `mevcut_urunler[]`, `diger_urun_icerikleri[]` | Tekrar eden etken madde, EFSA üst sınırı karşılaştırması (etiketteki en yüksek günlük kullanıma göre), etiketteki kullanım ve yaş sınırı, etkileşim/zamanlama notları, hekime sorulacak sorular. Doz önermez. |
| `etken_madde_rehberi` | `etken_madde`; isteğe bağlı `yas`, `cinsiyet`, `evre`, `sigara`, `ilac_grubu[]` | Kısa özet, kimde kanıt var, sonuç alanı bazında kanıt düzeyi (`guclu` / `orta` / `zayif` / `yetersiz` ve `sonuc_yonu`), ürün sayfalarındaki beyanlar, besinle karşılama, EFSA üst sınırı (güvenlik tavanı), etkileşimler, profile göre dikkat edilecekler, hekime sorulacaklar, alfabetik katalog ürünleri. Kanıt kartı olmayan maddede bunu söyler ve kataloğu gösterir. |
| `yasam_karnesi` | `cevaplar` (6 alan), isteğe bağlı `yas` | 6 soruluk testin karnesi (0–12 puan), en fazla 3 hedef, `takviye_baglantilari` (ör. az balık → omega-3 kanıtını incele), `guvenlik_uyarilari` (ör. sigara → beta-karoten) ve `tahlil_onerisi` (D vitamini, B12, ferritin). Kurallar `data/karne_kurallari.json` dosyasındadır. Cevaplar eksikse soruları döndürür. |

Her yanıtta şu alanlar bulunur: `kaynaklar`, `uyari` ("Takviye edici gıdalar ilaç değildir. Kişisel kullanım miktarı ve tedavi için hekiminize danışın."), `gelistirici` ve `veri_notu`.

### Kaynaklar

`kaynaklar[]` her öğede `baslik`, `kurum_veya_dergi`, `yil`, `tur` (`kilavuz` | `meta_analiz` | `rct` | `duzenleyici` | `uretici_icerigi`), `url` ve varsa `pmid` taşır. Kayıtlar `data/kaynaklar.json` dosyasındadır ve `scripts/kaynak_dogrula.py` ile doğrulanır:

```bash
.venv/bin/python scripts/kaynak_dogrula.py
```

Betik DOI'yi Crossref'ten, PMID'yi PubMed'den, kurum belgelerini URL'den kontrol eder; kayıttaki `alintilar` kaynağın özetinde, açık erişimli tam metninde ya da sayfasında birebir geçmelidir. Doğrulanamayan kaynak (`dogrulandi: false`) yanıtlarda gösterilmez. EFSA üst sınırları bu şekilde doğrulanmış EFSA belgelerine bağlıdır. Ürün sayfaları `uretici_icerigi` olarak, bağımsız kaynakların yanında verilir.

Tüm araçlar `readOnlyHint: true` olarak işaretlidir; hiçbir şey yazmaz, dışarıya istek atmaz.

### Gizlilik

- Sunucu girdileri yalnızca yanıtı üretmek için işler; saklamaz, loglamaz.
- Log düzeyi `WARNING`; araç argümanları hiçbir düzeyde loglanmaz (testlerle kontrol edilir).
- `ilac_grubu` ilaç adı değil, grup ister (ör. `kan_sulandirici_varfarin`, `tiroid_hormonu`).

## Klasör yapısı

```
data/
  urunler.json                  # orzax.com.tr'den alınan katalog (etiket bilgisi; fiyat yok)
  kurallar.json                 # etken maddeler, EFSA üst sınırları, etkileşim kuralları, ilaç grupları
  kaynaklar.json                # doğrulanmış kaynak kayıtları (DOI, PMID veya URL + erişim tarihi)
  karne_kurallari.json          # karneden takviye kanıtına, güvenlik uyarısına ve tahlile köprü kuralları
  beyanlar/urun_beyanlari.json  # ürün sayfalarındaki sağlık ve beslenme beyanları (kelimesi kelimesine)
  beyanlar/beyanlar.json        # etken madde düzeyindeki beyan metinleri (regülasyon onayı bekliyor)
  ham/                          # indirilen sayfaların önbelleği (git'e girmez)
scripts/
  orzax_katalog.py              # katalog indirme ve ayrıştırma
  kaynak_dogrula.py             # kaynakları Crossref, PubMed ve URL'den doğrular
  json_yaz.py                   # veri dosyalarını okunur biçimde yazar
server/
  veri.py                 # veri yükleme, birim çevirme, arama
  araclar.py              # araçların iş mantığı (saf fonksiyonlar)
  app.py                  # FastMCP sunucusu ve araç tanımları
tests/                    # her araç için test + MCP protokol ve HTTP testleri
docs/KANIT_PROTOKOLU.md
```

Ürün düzeyindeki etki ifadeleri yalnızca `data/beyanlar/urun_beyanlari.json` dosyasındaki, ürün sayfasından alınmış beyanlardan gelir.

### Kanıt tabanı

`data/etken_maddeler/<id>/` altında `monografi.json`, `kartlar/*.json` (etken madde × sonuç alanı × popülasyon) ve `arama_kaydi.md` bulunur. Şema ve süreç `docs/KANIT_PROTOKOLU.md` dosyasındadır. Testler şunları zorunlu kılar: her kartta en az 2 doğrulanmış kaynak ve bunlardan en az biri kılavuz ya da düzenleyici; karttaki her sayının kaynak alıntısında ya da `mutlak_fark.hesap` alanında geçmesi; halk özetinin en fazla 60 kelime olması; yasaklı ifade bulunmaması.

Sunucu yalnızca `durum: "onaylandi"` kayıtları sunar. Deneme sunucusunda `TB_TASLAK_GOSTER=1` verilirse kurul onayı bekleyen taslaklar "taslak" notuyla gösterilir (`render.yaml` bu ayarla gelir; yayın sunucusunda kaldırılır).

İlk set: D vitamini (pilot, taslak). Omega-3, B12, folat, demir, magnezyum, C vitamini, çinko, multivitamin, beta-karoten, E vitamini ve probiyotik için araç EFSA değeri, ürün beyanları ve kataloğu verir; kanıt kartları pilot onaylandıktan sonra eklenecek.

### Kataloğu güncelleme

```bash
.venv/bin/python scripts/orzax_katalog.py indir
.venv/bin/python scripts/orzax_katalog.py ayristir
```

`indir` sitemap'teki Türkçe ürün sayfalarını saniyede bir istekle `data/ham/orzax/` altına indirir (var olan sayfaları yeniden indirmez). `ayristir` içerik tablosu, bileşim, beyanlar ve kullanım şeklini okur. Sitedeki tablo hataları (boş miktar hücresi, birimsiz sayı vb.) tahmin edilmez; `okuma_notlari` alanına yazılır. Reçeteli ürünler ve içerik miktarı yazmayan ürünler atlanır, nedenleri `atlanan_sayfalar` alanında listelenir.

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
| `TB_PORT` | `8000` | Port (yoksa `PORT` kullanılır) |
| `TB_ALLOWED_HOSTS` | boş | Yerel adreslere ek olarak kabul edilecek `Host` başlıkları, virgülle (ör. ngrok adresi). Render'da `RENDER_EXTERNAL_HOSTNAME` kendiliğinden eklenir. |

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

- Etkileşim kuralları ve yaşam karnesi eşikleri medikal kurul onayı bekliyor; etkileşim kurallarına henüz kaynak bağlanmadı.
- Etken madde düzeyindeki beyan metinleri (`data/beyanlar/beyanlar.json`) regülasyon ekibinin onayını bekliyor.
- `mevzuat.gov.tr` ve `hsgm.saglik.gov.tr` bulut ortamından erişilemiyor; TGK yönetmeliği ve Sağlık Bakanlığı belgelerinin URL'leri elle doğrulanmalı. `ods.od.nih.gov` otomatik istekleri reddediyor.
- `calismalarda_kullanilan_dozlar` alanı kanıt kartları hazırlanınca dolacak.
