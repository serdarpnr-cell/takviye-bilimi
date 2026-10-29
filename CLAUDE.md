# Takviye Bilimi · proje kuralları

## Proje

Takviye Bilimi, ChatGPT ve Claude içinde çalışan bir MCP sunucusu. Orzax geliştiriyor.

Amaç: takviye edici gıdalarla ilgili bilimi Türkçe, sade ve dürüst biçimde insanların günlük hayatına taşımak. Bu bir bilimsel çalışma, pazarlama değil. Bir cümlenin doğruluğundan emin değilsen yazma, işaretle ve sor.

Araştırmanın nasıl yapılacağı `docs/KANIT_PROTOKOLU.md` dosyasında. Her fazın sonunda dur, özet ver ve onay bekle.

## Değişmez kurallar

1. **Uydurma kaynak yok.** Her kaynak PubMed, Europe PMC veya Crossref API'sinden doğrulanır ve PMID ya da DOI ile saklanır. Kurum belgeleri (EFSA, WHO, NIH ODS, TÜBER) için URL ve erişim tarihi saklanır. Doğrulanamayan kaynak kullanılmaz.
2. **Sorgu anında araştırma yok.** MCP sunucusu yalnızca kanıt tabanındaki `durum: "onaylandi"` kayıtlarını sunar. Canlı web araması ya da canlı literatür özetlemesi yapılmaz.
3. **Ürün ile etken madde ayrıdır.** Ürüne ait etki ifadesi yalnızca `data/beyanlar/` altındaki onaylı sağlık beyanlarından gelir. Bilimsel kartlar etken madde düzeyindedir ve "bu ürün şunu sağlar" demez.
4. **Kişiye doz yok.** Üç bilgi ayrı alanlarda sunulur, birbirine karıştırılmaz: etiketteki kullanım, çalışmalarda kullanılan dozlar, resmi üst sınır. "Sen şu kadar al" denmez.
5. **Tanı ve tedavi yok.** Takviye edici gıdaya hastalığı önleme, tedavi etme veya iyileştirme özelliği atfedilmez. Tek istisna onaylı hastalık riski azaltma beyanlarıdır.
6. **Olumsuz sonuç da yazılır.** "Kanıt yetersiz", "etkisiz bulundu" ve "güvenlik sinyali" sonuçları gizlenmez ve yumuşatılmaz.
7. **Marka ayrımı yok.** Orzax ürünleri ve diğer markalar aynı şablon ve aynı tonla gösterilir.
8. **Önce mutlak rakam.** Mümkünse göreli risk yerine mutlak fark verilir ("100 kişiden 2'si").
9. **Kaynak hiyerarşisi:** otoriter kurumlar ve sistematik derlemeler, büyük randomize kontrollü çalışmalar (RKÇ), küçük RKÇ'ler, gözlemsel çalışmalar. Hayvan ve hücre çalışmaları kanıt düzeyine katılmaz.
10. **Telif.** Tam metin kopyalanmaz; özet ve kısa alıntı kullanılır. Examine gibi lisanslı veya ücretli veritabanları kazınmaz.
11. **Kişisel veri yok.** Sunucu kullanıcı profilini saklamaz ve loglamaz.

## Yasaklı ifadeler

`scripts/lint_ifadeler.py` her içerik değişikliğinde çalışır. Bulunan ifade kartı otomatik reddetmez, insan incelemesine düşürür.

- tedavi eder, iyileştirir, şifa, mucize, garanti, kesin sonuç, %100
- hastalığı önler (onaylı risk azaltma beyanı yoksa)
- kanıtlanmıştır (tek çalışmaya dayanıyorsa)
- en iyi, resmi, bir numara
- doktora gerek yok, ilaç yerine

## Klasör yapısı

```
data/
  urunler.json                 # ürün → etken madde, form, etiket miktarı
  beyanlar/                    # onaylı sağlık beyanları (kaynak: regülasyon)
  etken_maddeler/<id>/
    monografi.json
    kartlar/*.json             # etken madde × sonuç alanı
    arama_kaydi.md             # arama dizeleri, tarih, sonuç sayısı, eleme
  kaynaklar.json               # doğrulanmış kaynak kayıtları
  ham/                         # API yanıt önbelleği (git'e girmez)
scripts/                       # arama, doğrulama, lint, kurul paketi
server/                        # MCP sunucusu
tests/
kurul/                         # medikal kurul inceleme paketleri
docs/KANIT_PROTOKOLU.md
```

## Ortam

- NCBI API anahtarı `NCBI_API_KEY` ortam değişkeninde. Yoksa sor; anahtarsız düşük hızla çalış.
- API yanıtlarını `data/ham/` altında önbelleğe al, hız sınırlarına uy.

## Komutlar

- Kurulum: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Test: `.venv/bin/python -m pytest -v`
- Sunucu: `.venv/bin/python -m server` → `http://127.0.0.1:8000/mcp` (ngrok için `TB_ALLOWED_HOSTS=<adres>`)
- Inspector: `npx -y @modelcontextprotocol/inspector` → Streamable HTTP, `http://localhost:8000/mcp`
