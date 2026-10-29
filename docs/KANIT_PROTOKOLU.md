# Takviye Bilimi · kanıt protokolü

Bu protokol, örnek ürünlerdeki etken maddeler için bilimsel kanıtın nasıl toplanacağını, değerlendirileceğini, sade Türkçeye çevrileceğini ve kullanıcıya nasıl sunulacağını tarif eder. Proje kuralları `CLAUDE.md` dosyasındadır; çelişki olursa `CLAUDE.md` geçerlidir.

---

## 0. Kapsam

### Örnek ürünler ve etken maddeler

Miktarlar prototipten alınmıştır ve temsilidir. Regülasyon ekibi gerçek etiketleri verdiğinde `data/urunler.json` güncellenir.

| Ürün | Etken madde | Form | Günlük miktar (temsili) |
|---|---|---|---|
| Ocean Balık Yağı | EPA, DHA | Trigliserit | 330 mg EPA, 250 mg DHA |
| Ocean D3K2 Damla | D3 vitamini, K2 vitamini | Kolekalsiferol, menakinon-7 (MK-7) | 1.000 IU, 50 µg |
| Ocean Vitamin D3 1000 IU Sprey | D3 vitamini | Kolekalsiferol | 1.000 IU |
| Ocean Magnezyum | Magnezyum | Bisglisinat | 200 mg |
| Ocean Balık Yağı Şurup (4–12 yaş) | EPA, DHA, D3 vitamini | Trigliserit, kolekalsiferol | 120 mg, 200 mg, 400 IU |
| Ocean Folik Asit + Demir | Demir, folat, B12 vitamini | Demir bisglisinat, folik asit, metilkobalamin | 14 mg, 400 µg, 2,5 µg |

Buna göre 8 etken madde var: omega-3 (EPA + DHA birlikte), D3, K2, magnezyum, demir, folik asit, B12. Ayrıca iki özel popülasyon incelenir: **çocuklar** ve **gebelik planlayan ya da gebe kadınlar**.

### Başlangıç sonuç alanları

Faz 0'da bu listeyi gözden geçir, eksik olanları ekle ve onaya sun.

- **Omega-3:** kalp-damar olayları (genel popülasyon ve yüksek risk ayrı), trigliserit, kan basıncı, bilişsel işlev, gebelikte DHA ve erken doğum, depresyon, eklem; çocuklarda bilişsel gelişim ve dikkat.
- **D3 vitamini:** kemik mineral yoğunluğu, kırık, düşme, kas gücü, akut solunum yolu enfeksiyonları, kanser sıklığı ve kansere bağlı ölüm, kalp-damar olayları, tip 2 diyabet gelişimi, depresyon, tüm nedenlere bağlı ölüm; çocuklarda raşitizmin önlenmesi ve solunum yolu enfeksiyonları.
- **K2 vitamini (MK-7):** kemik mineral yoğunluğu ve kırık, damar kireçlenmesi; güvenlik başlığı olarak K vitamini antagonisti kan sulandırıcılarla etkileşim.
- **Magnezyum:** uyku, kas krampları, kan basıncı, kan şekeri ve insülin direnci, migren, yorgunluk; formlar arası emilim farkı.
- **Demir:** adet gören kadınlarda demir eksikliği ve aneminin önlenmesi, anemisi olmayan demir eksikliğinde yorgunluk, gebelik; sindirim yan etkileri; günlük ve aralıklı kullanım karşılaştırması.
- **Folik asit:** gebelik öncesi kullanımda nöral tüp defekti riski; B12 eksikliğini maskeleme riski.
- **B12 vitamini:** eksiklik riski olan gruplar (vegan beslenenler, ileri yaş, metformin ve mide asidi baskılayıcı kullananlar), bilişsel işlev, yorgunluk.

---

## 1. Üretilecek çıktılar

1. **Monografi:** Her etken madde için bir dosya. Nedir, ne işe yarar, nasıl kullanılır sorularının cevabı.
2. **Kanıt kartları:** Her etken madde × sonuç alanı × popülasyon için bir kart.
3. **Ürün bilimi sayfası:** Her ürün için etken maddeler, "bu üründeki miktar" bloğu, onaylı beyanlar ve ilgili kartlar.
4. **Arama kaydı:** Her etken madde için kullanılan arama dizeleri, tarih, sonuç sayıları ve eleme nedenleri.
5. **Kurul paketi:** Medikal kurulun onaylayacağı inceleme dosyası.

---

## 2. Kaynaklar ve araçlar

### Katman 1 · Otoriter kurumlar

- EFSA Beslenme Paneli: referans alım değerleri, üst sınırlar, sağlık beyanı görüşleri
- NIH Office of Dietary Supplements bilgi sayfaları (sağlık profesyoneli sürümü)
- WHO rehberleri (ör. gebelikte ve adet gören kadınlarda demir ve folik asit)
- Cochrane sistematik derlemeleri
- USPSTF önerileri
- Türkiye: Türkiye Beslenme Rehberi (TÜBER) referans alım değerleri; Sağlık Bakanlığı destek programları (bebek ve gebe D vitamini, gebe demir); TEMD kılavuzları; TİTCK sağlık beyanı kılavuz ekleri; Türkiye'de yapılmış eksiklik yaygınlığı çalışmaları

### Katman 2 · Sistematik derlemeler ve meta-analizler

Son 10 yıl önceliklidir. Şemsiye derlemeler dahildir.

### Katman 3 · Büyük RKÇ'ler

Mutlaka kapsanacak çalışmalar aşağıda. Her birini API'den doğrula; bulamazsan bildir.

- VITAL (D3 vitamini ve omega-3)
- D-Health (D3 vitamini)
- DO-HEALTH (D3 vitamini, omega-3, egzersiz)
- ViDA (D3 vitamini)
- ASCEND (omega-3)
- STRENGTH (omega-3)
- REDUCE-IT: reçeteli, yüksek doz ikosapent etil çalışmasıdır. Takviye dozlarıyla karşılaştırılmaz; kartta bu ayrım açıkça yazılır.
- MRC Vitamin Study, 1991 (folik asit ve nöral tüp defekti)

### Katman 4 · Gözlemsel çalışmalar

Yalnızca RKÇ yoksa kullanılır. Kanıt düzeyi en fazla "Sınırlı" olabilir.

### Hariç tutulanlar

Hayvan ve hücre çalışmaları, vaka sunumları, konferans özetleri, geri çekilmiş yayınlar, şüpheli (predatory) dergiler. Reçeteli ilaç dozlarıyla yapılan çalışmalar kanıt düzeyine katılmaz, kartta ayrıca işaretlenir.

### API'ler

| Amaç | Araç |
|---|---|
| Arama ve özet | PubMed E-utilities (NCBI API anahtarıyla), Europe PMC REST API |
| DOI doğrulama | Crossref REST API |
| Devam eden çalışmalar | ClinicalTrials.gov API v2 |
| Geri çekilme kontrolü | PubMed "Retracted Publication" yayın türü ve Crossref güncelleme kayıtları |

Hız sınırlarına uy. Ham yanıtları `data/ham/` altında önbelleğe al.

---

## 3. Arama ve seçim

Her etken madde × sonuç alanı için:

1. **Arama:** MeSH terimleri ve anahtar kelimelerle arama dizesi oluştur. Filtreleri, tarihi ve sonuç sayısını `arama_kaydi.md` dosyasına yaz.
2. **Eleme:** Başlık ve özete göre ele. Dahil etme ölçütleri: insan çalışması, ağızdan takviye, ilgili popülasyon, klinik olarak anlamlı sonuç. Elenen her kayıt için kısa bir neden yaz.
3. **Kayıt:** Dahil edilen her çalışma için şunları sakla:
   - tasarım, katılımcı sayısı, popülasyon (başlangıçta eksiklik var mı?)
   - doz, form, süre, karşılaştırma
   - sonuç ve etki büyüklüğü (güven aralığıyla), mümkünse mutlak fark
   - fon kaynağı ve çıkar çatışması
   - kalite notu: yüksek, orta veya düşük, gerekçesi tek cümle (derlemeler için AMSTAR-2'nin kısaltılmışı, RKÇ'ler için RoB 2'nin kısaltılmışı)
   - `kanit_alinti`: sayıların geçtiği özet cümlesi, kelimesi kelimesine

---

## 4. Kanıt düzeyi

GRADE'den sadeleştirilmiş ölçek:

| Düzey | Kullanıcıya anlamı | Ölçüt |
|---|---|---|
| **A · Güçlü** | Etki büyük olasılıkla gerçek | Birden fazla yüksek kaliteli RKÇ veya meta-analizde tutarlı sonuç |
| **B · Orta** | Etki olası, yeni çalışmalarla değişebilir | Tutarlı ama sınırlı sayıda RKÇ ya da kalite sorunları |
| **C · Sınırlı** | Sinyal var, emin değiliz | Küçük veya çelişkili RKÇ'ler, ya da yalnızca gözlemsel veri |
| **D · Yetersiz** | Bilmiyoruz | Anlamlı insan çalışması yok |
| **Etkisiz** | Fayda büyük olasılıkla yok | Yüksek kaliteli RKÇ'ler veya meta-analizler anlamlı fayda bulmadı |
| **Dikkat** | Güvenlik sinyali var | Yan etki, etkileşim veya fazla kullanım riski |

Kurallar:

- "Yetersiz" (bilmiyoruz) ile "Etkisiz" (yok gibi görünüyor) aynı şey değildir; asla karıştırılmaz.
- Aynı sonuç farklı popülasyonlarda farklı düzey alabilir. Özellikle başlangıçta eksikliği olanlar ile olmayanlar ayrı değerlendirilir.
- A düzeyi için en az iki bağımsız, yüksek kaliteli kaynak gerekir.
- Doz-yanıt ilişkisi varsa not edilir.

---

## 5. Veri şemaları

### Kanıt kartı (`kartlar/<sonuc_alani>__<populasyon>.json`)

```json
{
  "id": "d3__kirik__toplumda_yasayan_yetiskin",
  "etken_madde": "d3",
  "sonuc_alani": "Kırık",
  "populasyon": "Toplumda yaşayan, eksikliği bilinmeyen yetişkinler",
  "soru": "D3 takviyesi kırık sıklığını azaltır mı?",
  "kanit_duzeyi": "A | B | C | D | Etkisiz | Dikkat",
  "yon": "fayda | etkisiz | zarar | belirsiz",
  "halk_ozeti": "En fazla 60 kelime, sade Türkçe.",
  "gunluk_hayatta": "Pratik çıkarım: kimin için anlamlı, besinle karşılanır mı, ne zaman hekime.",
  "ne_bilmiyoruz": "Açık kalan sorular.",
  "teknik_ozet": "Kurul için: tasarım, n, etki büyüklüğü, GA, kalite.",
  "calisilan_dozlar": "Çalışmalarda kullanılan doz aralığı ve süre.",
  "etki": {"olcu": "RR", "deger": null, "ga95": [null, null], "mutlak_fark": "100 kişiden ..."},
  "kaynaklar": [
    {
      "kaynak_id": "pmid:XXXXXXXX",
      "tip": "meta-analiz | RKÇ | kurum | gözlemsel",
      "katman": 1,
      "kalite": "yüksek | orta | düşük",
      "fon": "kamu | endüstri | karma | belirtilmemiş",
      "kanit_alinti": "Özetten kelimesi kelimesine kısa alıntı.",
      "dogrulandi": true,
      "geri_cekildi": false
    }
  ],
  "onayli_beyan_iliskisi": "Bu sonuç alanında onaylı sağlık beyanı var mı? Varsa metni.",
  "durum": "taslak | kurul_incelemesinde | onaylandi | reddedildi",
  "onaylayan": null,
  "onay_tarihi": null,
  "son_arama_tarihi": "YYYY-AA-GG"
}
```

### Monografi (`monografi.json`)

| Alan | İçerik |
|---|---|
| `nedir` | Etken madde ve vücuttaki görevi (2–3 cümle) |
| `formlar` | Takviyelerde görülen formlar ve aralarındaki fark (ör. kolekalsiferol ile ergokalsiferol; magnezyum bisglisinat, sitrat ve oksit), kanıtıyla |
| `besin_kaynaklari` | Başlıca besinler; besinle karşılanabilirlik |
| `referans_alim` | TÜBER ve EFSA değerleri; yaş ve cinsiyete göre |
| `ust_sinir` | EFSA üst sınırı; yaş gruplarına göre |
| `risk_gruplari` | Eksiklik riski yüksek gruplar (Türkiye verisi varsa öncelikli) |
| `nasil_kullanilir` | Yemekle mi, aç karna mı, neyle birlikte alınmaz (ör. demir ile kalsiyum, çay ve kahve) |
| `etkilesimler` | İlaç ve takviye etkileşimleri, şiddet düzeyiyle |
| `yan_etkiler` | Sık ve önemli yan etkiler |
| `kimler_dikkat` | Gebelik, emzirme, çocuk, böbrek hastalığı vb. |
| `ne_beklenmeli` / `ne_beklenmemeli` | Kartlardan türetilir, kartlara bağlantılı |
| `kaynaklar` | Doğrulanmış kaynak kimlikleri |

Rakamları protokole yazma; güncel değerleri kaynaktan çek.

---

## 6. Sade Türkçe kuralları

- Halk özeti en fazla 60 kelime. Cümleler kısa, B1 düzeyi.
- Teknik terim ilk geçtiğinde açıklanır ("randomize kontrollü çalışma: katılımcıların kurayla iki gruba ayrıldığı çalışma").
- Rakamlar yüzde yerine "100 kişiden X" şeklinde verilir.
- Belirsizlik açıkça yazılır: "Emin değiliz, çünkü..."
- Özet şu sırayı izler: ne bulundu → kimde → ne kadar → ne anlama geliyor → ne bilmiyoruz.
- Abartı, korku dili ve satış dili kullanılmaz.

Örnek (rakamlar yer tutucudur, kartta kaynaktan doldurulur):

> **D3 vitamini ve kırık** · Etkisiz · toplumda yaşayan yetişkinler
> Eksikliği olmayan yetişkinlerde yapılan büyük çalışmalarda, D3 vitamini alanlarla almayanlar arasında kırık sıklığında anlamlı fark bulunmadı. Bu sonuç, eksikliği olan kişiler ve kalsiyumla birlikte kullanım için geçerli olmayabilir. Kemik sağlığı için düzeyinin ölçülmesi ve sonucun hekimle değerlendirilmesi önerilir.

---

## 7. Ürünle ilişkilendirme

- **"Bu üründeki miktar" bloğu** yalnızca rakam içerir, yorum içermez: etiketteki miktar, referans alım, çalışmalarda kullanılan doz aralığı, üst sınır. "Bu doz yeterli" veya "bu doz etkili" denmez.
- **Ürün düzeyindeki etki ifadesi** yalnızca `data/beyanlar/` altındaki onaylı beyanlardan gelir. Kaynak TİTCK kılavuz eki ve regülasyon ekibinin onayıdır.
- Diğer markaların ürünleri aynı şablonla gösterilir.
- **Hukuk görüşü bekleyen soru:** Etken madde düzeyindeki bilimsel kartların, bir markanın geliştirdiği araçta sunulması tanıtım sayılır mı? Görüş gelene kadar kartlar yalnızca kurul ve hukuk onayıyla yayına girer.

---

## 8. Otomatik doğrulama (`tests/`)

- Her kaynak API'den yeniden çekilir; başlık, yıl ve DOI/PMID eşleşmezse kart reddedilir.
- Karttaki her sayı, ilgili kaynağın `kanit_alinti` alanında geçmelidir.
- Geri çekilmiş yayın içeren kart reddedilir.
- Lint: yasaklı ifadeler, 60 kelime sınırı, zorunlu alanlar.
- Her kartta en az bir Katman 1–3 kaynağı olmalı; A düzeyi için en az iki bağımsız, yüksek kaliteli kaynak.
- **İkinci göz:** Kartların rastgele yüzde 10'u, ilk değerlendirmeyi görmeden yeniden değerlendirilir. Düzey uyuşmazlıkları raporlanır.
- Sunucu yalnızca `durum: "onaylandi"` kartları yükler; bunu bir test zorunlu kılar.

---

## 9. Medikal kurul onayı

- `kurul/` altında her etken madde için bir inceleme paketi (HTML veya XLSX) üretilir: kart, kaynak bağlantıları, kalite notu, ikinci göz sonucu ve "onayla / düzelt / reddet" alanı.
- Durum akışı: `taslak` → `kurul_incelemesinde` → `onaylandi` veya `reddedildi`. Onaylayan kişi ve tarih kaydedilir.
- Kurulun düzeltmeleri karta işlenir ve değişiklik kaydı tutulur.

---

## 10. MCP araçları

| Araç | Girdi | Çıktı |
|---|---|---|
| `bilimsel_temel` | `etken_madde`, isteğe bağlı `konu` ve `populasyon` | Monografi özeti, ilgili kartlar (en fazla 5), kaynak bağlantıları, son güncelleme tarihi |
| `urun_bilimi` | `urun` | Etken maddeler, "bu üründeki miktar" bloğu, onaylı beyanlar, ilgili kartlar |

Yanıt yapısı: `kisa_ozet`, `kartlar[]`, `kaynaklar[]` (PubMed veya DOI bağlantısıyla), `uyari`, `guncelleme`.

`uyari` alanı her yanıtta bulunur: "Takviye edici gıdalar ilaç değildir. Kişisel kullanım miktarı ve tedavi için hekiminize danışın."

Araç açıklamaları kısa ve abartısız yazılır; araçlar yalnızca takviye bilimiyle ilgili sorularda çağrılacak şekilde tarif edilir.

---

## 11. Güncelleme

- Üç ayda bir, her etken madde için yeni meta-analiz ve büyük RKÇ taraması yapılır.
- Değişiklik raporu üretilir: hangi kart etkilendi, düzey değişti mi.
- Düzeyi değişen kart yeniden kurul onayına gider.

---

## 12. Fazlar ve onay noktaları

Her fazın sonunda **dur**; yapılanları, sayıları (taranan, elenen, dahil edilen kaynak) ve açık soruları özetle; onay bekle.

| Faz | İş | Çıktı |
|---|---|---|
| **0 · Kapsam** | Etken madde × sonuç alanı × popülasyon listesi; arama stratejisi taslağı; proje iskeleti | Onaya sunulan kapsam dosyası |
| **1 · Pilot: D3 vitamini** | Tüm akış yalnızca D3 için: arama, eleme, kartlar, monografi, doğrulama testleri, kurul paketi | D3 kanıt seti; birlikte gözden geçirme |
| **2 · Diğer etken maddeler** | Pilotta düzeltilen akışla kalan 7 etken madde | 7 kanıt seti |
| **3 · Ürün ve sunucu** | Ürün bilimi sayfaları, `bilimsel_temel` ve `urun_bilimi` araçları, testler | Çalışan MCP sunucusu |
| **4 · Kurul ve yayın** | Kurul paketleri, onay işlemleri, yalnızca onaylı içerikle yayın | Yayına hazır kanıt tabanı |
