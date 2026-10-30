# Karar paketi C7 · Parti analizleri: kalite/laboratuvar ekibine veri talebi

Tarih: 2026-10-30 · Talep eden: Serdar Pınar · Alıcı: Orzax kalite / laboratuvar ekibi

## Neden

Takviye Bilimi kutudaki karekod ya da parti numarasından o partinin analiz sonucunu gösterebilir: etiketteki miktar ile ölçülen miktar yan yana, laboratuvar ve tarihle. Altyapı hazır; bugün yalnızca `DEMO-0001` gösterim kaydı var ve her yerde "DEMO" diye etiketli. Gerçek bir analiz yayımlanana kadar araç "yayımlanmış analiz yok" der.

## İstenen alanlar (parti başına, etken madde başına bir satır)

| Alan | Açıklama |
|---|---|
| `parti_no` | Ambalajdaki parti numarası, ambalajdaki yazımla |
| `urun_kodu` | Takviye Bilimi ürün kodu (ürün sayfası adresinin son parçası) |
| `laboratuvar` | Analizi yapan laboratuvarın adı (iç laboratuvar ise belirtin) |
| `akreditasyon_no` | Varsa TÜRKAK ya da eşdeğer akreditasyon numarası |
| `analiz_tarihi`, `rapor_no` | Analiz raporunun tarihi (YYYY-AA-GG) ve numarası |
| `etken_madde` | Ör. "D vitamini", "K2 vitamini", "Magnezyum" |
| `etiketteki` | Etiketteki porsiyon miktarı |
| `olculen` | Ölçülen porsiyon miktarı (aynı birimde) |
| `birim` | Maddenin standart birimi (D ve K vitaminlerinde µg, minerallerde mg) |
| `yontem` | Analiz yöntemi (ör. HPLC, ICP-OES) |
| `yayin_onaylayan`, `yayin_onay_tarihi` | Bu sonucun kamuya açık yayımını onaylayan kişi/rol ve tarih |

- **Format:** UTF-8 CSV; boş şablon `data/parti_analizleri/sablon.csv`; kayıt şeması `data/parti_analizleri/parti_analizi.schema.json`.
- **Başlangıç kapsamı:** her D vitamini ve D3K2 ürününden son 3 parti.
- **Karekod:** karekodun içerdiği adres ya da GS1 metni parti numarasını `(10)` alanında ya da `?parti=` parametresinde taşımalı (araç ikisini de okur).

## Yayın onayı kimde

Yayın kararı **Orzax kalite yönetimindedir**; Takviye Bilimi onaysız satırı içe almaz (`scripts/parti_analizi_al.py` reddeder). Ölçülen değer etiketten saparsa sonuç yine yayımlanır ve yorumlanmaz (oran yalnızca rakamdır; olumsuz sonuç gizlenmez, CLAUDE.md kural 6). Bu ilkeye kalite ekibinin yazılı onayı gerekir.

## İçe aktarma

`python scripts/parti_analizi_al.py <dosya.csv>` denetler (katalogda olmayan ürün, üründe olmayan madde, katalogla uyuşmayan etiket miktarı, yanlış birim, eksik onay, hatalı tarih, tekrar); hata varsa hiçbir şey alınmaz. `--yaz` ile `data/parti_analizleri.json`'a `demo: false` olarak eklenir.
