# Karar paketi C6 · Ürün kartında ambalaj görseli

Tarih: 2026-10-30 · Hazırlayan: geliştirme · Durum: **karar bekliyor (Serdar, pazarlama)**

Kartlar iframe içinde çalışır ve dış dosya yüklemez (v0.3 Bölüm 5.6, 7.4). Görsel ancak ya yanıtın içine gömülerek ya da host'a izinli bir alan adı bildirilerek gösterilebilir.

## Prototip

İki prototip de bayrak arkasında, **varsayılan kapalı** (`TB_AMBALAJ_GORSELI` tanımsız). 3 ürün: Ocean D3K2 Damla, Ocean Vitamin D3 400 IU Sprey, Ocean Magnezyum Complex. Görseller `data/ambalaj_gorselleri/` altında **yer tutucudur** (600×600 JPEG, ~36 KB; gerçek ambalaj değil). Gerçek görseller pazarlamadan alınmalı; siteden kazınmadı.

| Bayrak | Nasıl çalışır |
|---|---|
| `TB_AMBALAJ_GORSELI=base64` | Görsel `structuredContent.urun.ambalaj_gorseli.src` alanına `data:` adresi olarak gömülür. |
| `TB_AMBALAJ_GORSELI=cdn` (+ `TB_AMBALAJ_CDN`, varsayılan `https://cdn.orzax.com.tr`) | Kart görseli `<cdn>/ambalaj/<urun_kodu>.jpg` adresinden yükler; ürün kartı kaynağı `_meta.ui.csp.resourceDomains` ile bu tek alan adını bildirir. |

## Ölçüm (yerel, 30 tekrar, `urun_rehberi`)

| Mod | Araç sonucu boyutu | Sunucu işleme p95 | Modele giden metin |
|---|---|---|---|
| Kapalı | 5,7–6,5 KB | 1,0–1,3 ms | ~2.000 karakter |
| base64 | 53–55 KB (+~48 KB) | 1,3–1,5 ms | değişmedi |
| cdn | 5,8–6,6 KB | 1,0–1,3 ms | değişmedi |

Kart HTML'inin kendisi (`resources/read`, 16,4 KB) her üç modda aynıdır; görsel kart HTML'ine değil araç sonucuna eklenir. A3 bütçesi (tools/call + resources/read p95 < 1,5 sn) açısından sunucu işleme farkı ihmal edilebilir; asıl fark ağdır: +48 KB, 10 Mbit/sn bağlantıda ≈ 40 ms, mobil 3G'de birkaç yüz ms. cdn modunda görselin ayrıca indirilmesi ve host'un CSP desteği **canlıda ölçülmedi** (CDN yok; Render'a bu oturumdan erişilemedi) — A4 kitiyle ölçülmeli.

## Seçenekler

| Seçenek | Risk | Maliyet | Süre |
|---|---|---|---|
| (a) base64 gömme | Her ürün yanıtı ~50 KB büyür; host'un structuredContent'i modele de verip vermediği istemciye göre değişebilir (Claude'da model yalnızca metni görür); görsel güncellemesi sunucu yayını ister | Düşük | 2–3 gün (gerçek görsellerle) |
| (b) Tek izinli alan adı (CSP `resourceDomains`, ör. `cdn.orzax.com.tr`) | Host'ların CSP desteğine bağlı; dış istek kullanıcının IP'sini CDN'e gösterir (KVKK K3 ile birlikte değerlendirilmeli); CDN kurulumu | Orta (CDN + barındırma) | 1–2 hafta |
| (c) Görsel yok (bugün) | Kullanıcı ürünü adından tanır; marka görünürlüğü yok | Yok | — |

**Öneri: (c)**, ürün tanıma ihtiyacı kanıtlanırsa (a). Gerekçe: görsel bilimsel içeriğe katkı vermez ve tanıtım algısını artırır (bkz. C3 hukuk sorusu); (a) dış istek ve CSP bağımlılığı olmadan çalışır. Onay: Serdar + pazarlama (görsel hakları) + hukuk (C3 ile birlikte).
