# Gecikme ölçümü · 2026-10-30


> **Yerel ölçüm.** Bu oturumun ağ politikası `takviye-bilimi.onrender.com` adresine erişimi engelledi; bu tablo aynı kodun yerel sunucusundan (127.0.0.1) alındı ve ağ gecikmesini içermez. Render ölçümü: `python scripts/gecikme_olc.py --url https://takviye-bilimi.onrender.com/mcp --soguk-bekle-dk 15`.
Sunucu: `http://127.0.0.1:8765/mcp` · Tekrar: 20

Bütçe: sıcakken tools/call p95 + resources/read p95 < 1.5 sn ("ilk kart < 3 sn" hedefine host çizimi için pay).

## Araçlar (tools/call)

| Araç | p50 | p95 | p95 + en yavaş kart p95 | Bütçe |
|---|---|---|---|---|
| takviye_rehberi | 3 ms | 4 ms | 9 ms | içinde |
| sikayet_yolu | 4 ms | 4 ms | 9 ms | içinde |
| parti_analizi | 3 ms | 4 ms | 9 ms | içinde |
| etken_madde_rehberi | 10 ms | 10 ms | 15 ms | içinde |
| urun_rehberi | 4 ms | 4 ms | 9 ms | içinde |
| karsilastir | 9 ms | 11 ms | 16 ms | içinde |
| kisisel_rutin | 3 ms | 4 ms | 9 ms | içinde |
| yasam_karnesi | 3 ms | 3 ms | 8 ms | içinde |
| tahlil_goster | 2 ms | 4 ms | 9 ms | içinde |

## Kartlar (resources/read)

| Kart | p50 | p95 | HTML boyutu | mimeType |
|---|---|---|---|---|
| ui://takviye-bilimi/karne | 3 ms | 4 ms | 19.5 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/kanit | 3 ms | 3 ms | 18.1 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/urun | 2 ms | 3 ms | 16.4 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/rutin | 2 ms | 5 ms | 15.1 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/kiyas | 3 ms | 4 ms | 17.7 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/parti | 3 ms | 4 ms | 14.0 KB | text/html;profile=mcp-app |
| ui://takviye-bilimi/tahlil | 2 ms | 3 ms | 17.8 KB | text/html;profile=mcp-app |

## Soğuk başlangıç

Ölçülmedi (`--soguk-bekle-dk 15` ile koşun).
