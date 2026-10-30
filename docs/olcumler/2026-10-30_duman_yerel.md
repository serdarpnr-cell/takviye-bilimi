# Duman testi · 2026-10-30


> **Yerel duman testi.** Render adresine bu oturumdan erişilemedi (ağ politikası). Yayından sonra: `python scripts/duman_testi.py --url https://takviye-bilimi.onrender.com/mcp`.
Sunucu: `http://127.0.0.1:8765/mcp`

Sonuç: **GEÇTİ**

## Geçenler

- initialize instructions dolu (1182 karakter); serverInfo Takviye Bilimi 0.3.0
- tools/list: v0.3'ün 8 aracı var (toplam 10 araç: etken_madde_rehberi, karsilastir, katalog_sayfasi, kisisel_rutin, parti_analizi, sikayet_yolu, tahlil_goster, takviye_rehberi, urun_rehberi, yasam_karnesi)
- annotations: tüm araçlarda title, readOnly, destructive=false, idempotent, openWorld=false
- 7 ui:// kaynağı okundu; mimeType ve dış kaynak denetimi yapıldı
- örnek çağrılar: structuredContent ve kisa_ozet denetlendi

## Hatalar

- Yok.

## Kart eşlemesi

| Araç | Rol | Kart (_meta.ui) |
|---|---|---|
| etken_madde_rehberi | derinlik | ui://takviye-bilimi/kanit |
| karsilastir | derinlik | ui://takviye-bilimi/kiyas |
| katalog_sayfasi | ek | yalnızca kart (modelden gizli) |
| kisisel_rutin | derinlik | ui://takviye-bilimi/rutin |
| parti_analizi | kapı | ui://takviye-bilimi/parti |
| ⚠ | parti_analizi kapı aracı ama _meta.ui bağlı: v0.3 Bölüm 1 ile çelişki; değiştirilmedi, rapor edildi | |
| sikayet_yolu | kapı | yok |
| tahlil_goster | ek | ui://takviye-bilimi/tahlil |
| takviye_rehberi | kapı | yok |
| urun_rehberi | derinlik | ui://takviye-bilimi/urun |
| yasam_karnesi | derinlik | ui://takviye-bilimi/karne |
