# Graph Report - takviye-bilimi  (2026-10-30)

## Corpus Check
- 124 files · ~127,892 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .csv 3, (none) 1, .css 1)

## Summary
- 984 nodes · 2060 edges · 88 communities (63 shown, 25 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee216834`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _yukle
- Server App & Schemas
- kart_onizleme.py
- test_kanit_kartlari.py
- kisisel_rutin
- veri.py
- Evidence Pipeline Rules
- Render Deployment Config
- re
- Project Overview & Deps
- Product vs Ingredient Rules
- Evidence Cards & Grading
- yasam_karnesi
- Source Hierarchy
- Public Exposure & ChatGPT
- graphify Rules
- Session Start Hook
- Phases & Scope
- Claude Connector & Render
- Folder Structure
- Package Metadata
- Batch Analysis Tool
- Lifestyle Scorecard Tool
- araclar.py
- D vitamini · arama kaydı
- test_katalog_dogrulama.py
- ozet.py
- Katalog bulguları · Orzax web ve regülasyon ekibine bildirim
- 2026-10-30_faz0_once.md
- 2026-10-30_faz0_sonra.md
- test_v03.py
- normalize
- Etkileşim kuralları · arama kaydı
- standart_miktar
- B12 vitamini · arama kaydı
- Demir · arama kaydı
- Magnezyum · arama kaydı
- Omega-3 (EPA + DHA) · arama kaydı
- sikayet_yolu
- kurul_paketi.py
- kart_onizleme.mjs
- 2026-10-30_faz1_sonra.md
- 2026-10-30_faz2_sonra.md
- ortak.js
- etken_madde_rehberi
- _madde_ozeti
- beyan_satirlarini_birlestir
- conftest.py
- 2026-10-30_faz3_sonra.md
- __init__.py
- sayac.py
- karsilastir
- test_faz3.py
- json
- argparse
- gecikme_olc.py
- test_mcp_sunucu.py
- properties
- ikinci_goz.py
- properties
- olcum.py
- yayin_onayi
- Takviye Bilimi v0.4 · durum
- C vitamini · arama kaydı
- Çinko · arama kaydı
- Folik asit · arama kaydı
- parti_analizi.schema.json
- demo
- sonuclar
- Claude canlı test kiti (v0.4 A4)
- Karar paketi C3 · Hukuk soru notu
- Karar paketi C7 · Parti analizleri: kalite/laboratuvar ekibine veri talebi
- gorunen_ad
- gercek_parti_analizi_var
- Karar paketi C6 · Ürün kartında ambalaj görseli
- Karar paketi C5 · TB-24 etiket uyarıları: veri talebi
- Duman testi · 2026-10-30
- Gecikme ölçümü · 2026-10-30
- akreditasyon_no
- parti_no
- denetle
- orzax_bildirim_taslagi.md
- .mcp.json
- SKILL.md

## God Nodes (most connected - your core abstractions)
1. `etken_madde_rehberi()` - 62 edges
2. `kisisel_rutin()` - 44 edges
3. `yasam_karnesi()` - 41 edges
4. `urun_rehberi()` - 36 edges
5. `urunler()` - 32 edges
6. `kurallar()` - 28 edges
7. `sikayet_yolu()` - 23 edges
8. `karsilastir()` - 23 edges
9. `takviye_rehberi()` - 23 edges
10. `normalize()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Kodda kanıt: sağlık verisi yalnızca anlık işlenir` --references--> `_yukle()`  [INFERRED]
  docs/karar/kvkk.md → server/veri.py
- `2. Teknik önlemler (uygulanmış)` --references--> `test_tahlil_karti_degeri_gondermez_ve_saklamaz()`  [INFERRED]
  docs/KVKK_KONTROL.md → tests/test_faz3.py
- `Kodda kanıt: sağlık verisi yalnızca anlık işlenir` --references--> `test_kisisel_veri_loglanmaz()`  [EXTRACTED]
  docs/karar/kvkk.md → tests/test_kisisel_rutin.py
- `2. Teknik önlemler (uygulanmış)` --references--> `test_kisisel_veri_loglanmaz()`  [EXTRACTED]
  docs/KVKK_KONTROL.md → tests/test_kisisel_rutin.py
- `urun_rehberi tool` --semantically_similar_to--> `urun_bilimi MCP tool (planned)`  [INFERRED] [semantically similar]
  README.md → docs/KANIT_PROTOKOLU.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Current prototype MCP tools** — readme_urun_rehberi, readme_parti_analizi, readme_kisisel_rutin, readme_yasam_karnesi [EXTRACTED 1.00]
- **Evidence pipeline: search -> grade -> card -> validate -> board** — docs_kanit_protokolu_arama_ve_secim, docs_kanit_protokolu_kanit_duzeyi, docs_kanit_protokolu_kanit_karti_semasi, docs_kanit_protokolu_otomatik_dogrulama, docs_kanit_protokolu_medikal_kurul [INFERRED 0.85]
- **Public exposure and client connection** — readme_render_deploy, readme_ngrok_tunnel, readme_dns_rebinding_protection, readme_claude_connector, readme_chatgpt_developer_mode [INFERRED 0.85]

## Communities (88 total, 25 thin omitted)

### Community 0 - "_yukle"
Cohesion: 0.17
Nodes (11): main(), beyanlar(), karne_kurallari(), katalog_tarihi(), urun_beyanlari(), _yukle(), _zorunlu_uyarilar(), test_kurul_paketi_her_taslak_icerigi_karar_alaniyla_listeler() (+3 more)

### Community 1 - "Server App & Schemas"
Cohesion: 0.07
Nodes (28): etken_madde_rehberi(), _guvenlik(), kanit_arayuzu(), karne_arayuzu(), karsilastir(), katalog_sayfasi(), kisisel_rutin(), kiyas_arayuzu() (+20 more)

### Community 2 - "kart_onizleme.py"
Cohesion: 0.23
Nodes (5): calistir(), main(), _ortam(), _playwright_var(), test_dort_kart_hatasiz_cizilir()

### Community 3 - "test_kanit_kartlari.py"
Cohesion: 0.08
Nodes (25): _kunye(), kaynak_kayitlari(), _katman_1(), _kelime_sayisi(), _rakamlar(), test_kart_semasi(), test_kartta_en_az_iki_kaynak_biri_katman_1(), test_karttaki_sayilar_kaynak_alintisinda_gecer() (+17 more)

### Community 4 - "kisisel_rutin"
Cohesion: 0.12
Nodes (27): DigerUrun, Icerik, KarneCevaplari, kisisel_rutin(), _soru_var(), test_bos_rutin(), test_cocukta_d3_siniri_yasa_gore_degisir(), test_collagen_mag_plus_ve_d3k2_birlikte() (+19 more)

### Community 5 - "veri.py"
Cohesion: 0.16
Nodes (11): ambalaj_cdn(), ambalaj_gorseli(), ambalaj_modu(), etiket_uyarilari(), kanit_tabani_kimlikleri(), _kaynak_gorunumu(), monografi(), _monografiler() (+3 more)

### Community 6 - "Evidence Pipeline Rules"
Cohesion: 0.18
Nodes (9): NCBI_API_KEY environment, Forbidden phrases list (lint_ifadeler.py), APIs: PubMed E-utilities, Europe PMC, Crossref, ClinicalTrials.gov, Search and selection process (arama_kaydi.md), Quarterly update cycle, Pending legal opinion: scientific cards as promotion, Medical board approval workflow (taslak -> onaylandi), Automated validation tests (re-fetch sources, retraction, lint, second look) (+1 more)

### Community 7 - "Render Deployment Config"
Cohesion: 0.18
Nodes (10): key, value, services, buildCommand, envVars, name, plan, runtime (+2 more)

### Community 8 - "re"
Cohesion: 0.08
Nodes (30): _crossref(), dogrula(), _getir(), main(), _ncbi(), _pubmed(), sade(), _sayfa_metni() (+22 more)

### Community 9 - "Project Overview & Deps"
Cohesion: 0.25
Nodes (7): Takviye Bilimi project rules, Evidence protocol (Kanit Protokolu), MCP Inspector testing, Takviye Bilimi MCP server (prototype), httpx>=0.27, mcp[cli]>=1.26,<2, pytest / pytest-asyncio

### Community 10 - "Product vs Ingredient Rules"
Cohesion: 0.40
Nodes (4): 'Bu urundeki miktar' block (numbers only, no interpretation), urun_bilimi MCP tool (planned), kisisel_rutin tool, urun_rehberi tool

### Community 11 - "Evidence Cards & Grading"
Cohesion: 0.33
Nodes (5): bilimsel_temel MCP tool (planned), Evidence levels (simplified GRADE: A/B/C/D/Etkisiz/Dikkat), Evidence card schema, Monograph schema, uyari response field (not a medicine disclaimer)

### Community 12 - "yasam_karnesi"
Cohesion: 0.06
Nodes (36): _aralik(), _kopruler(), _kural_saglanir(), _puan(), _puanla(), yasam_karnesi(), _idler(), kartlar_var() (+28 more)

### Community 14 - "Public Exposure & ChatGPT"
Cohesion: 0.67
Nodes (3): ChatGPT Developer Mode setup, DNS rebinding protection / TB_ALLOWED_HOSTS, ngrok HTTPS tunnel

### Community 27 - "araclar.py"
Cohesion: 0.15
Nodes (21): bilesim_ozeti(), _cevap_metni(), _etiket_miktari(), etkilesim_bayraklari(), _gecenler(), _karantina_metni(), _katalog_eslesmesi(), _katalog_ogesi() (+13 more)

### Community 28 - "D vitamini · arama kaydı"
Cohesion: 0.20
Nodes (9): Açık kalanlar, Başlık/özet eleme tablosu, D vitamini · arama kaydı, Hatalı kimlikler, Hedefli doğrulama (kanıt protokolü, Katman 1 ve 3), Hedefli doğrulama (kanıt protokolü Katman 1 ve 3), Kurul için açık sorular, PRISMA akış sayıları (+1 more)

### Community 29 - "test_katalog_dogrulama.py"
Cohesion: 0.22
Nodes (8): brd_yuzdesi(), satir_miktari(), _satir(), test_brd_yuzdesi_ayristirma(), test_karantinadaki_her_satir_gerekce_tasir_ve_tutarli_satirlar_gecer(), test_supheli_satir_karantinada(), test_urun_rehberi_karantinadaki_satiri_isaretler(), test_yuksek_ama_tutarli_miktar_karantinaya_dusmez()

### Community 30 - "ozet.py"
Cohesion: 0.09
Nodes (21): cumle(), _etken_madde_rehberi(), _karsilastir(), _kaynak_satirlari(), _kisisel_rutin(), _madde(), metin(), _parti_analizi() (+13 more)

### Community 31 - "Katalog bulguları · Orzax web ve regülasyon ekibine bildirim"
Cohesion: 0.50
Nodes (3): Elle görülen bulgular, Karantinadaki içerik satırları, Katalog bulguları · Orzax web ve regülasyon ekibine bildirim

### Community 34 - "test_v03.py"
Cohesion: 0.05
Nodes (45): hedef_bul(), parti_analizi(), _parti_no_coz(), takviye_rehberi(), urun_rehberi(), hedef_eslemesi(), urun_ara(), urunler() (+37 more)

### Community 35 - "normalize"
Cohesion: 0.16
Nodes (7): _beyan_anahtari(), _madde_beyanlari(), urun_formu(), _beyan_adlari(), normalize(), sorgudaki_etken_madde(), urun_saglik_beyanlari()

### Community 36 - "Etkileşim kuralları · arama kaydı"
Cohesion: 0.50
Nodes (3): Aramalar, Etkileşim kuralları · arama kaydı, Kural başına dayanak

### Community 37 - "standart_miktar"
Cohesion: 0.33
Nodes (4): _birim_kodu(), _ima_edilen_brd(), katalog_dogrula(), standart_miktar()

### Community 38 - "B12 vitamini · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, B12 vitamini · arama kaydı, Hedefli arama (kanıt protokolü Katman 1–3), Sonuç

### Community 39 - "Demir · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, Demir · arama kaydı, Hedefli arama, Sonuç

### Community 40 - "Magnezyum · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, Hedefli arama, Magnezyum · arama kaydı, Sonuç

### Community 41 - "Omega-3 (EPA + DHA) · arama kaydı"
Cohesion: 0.20
Nodes (9): Açık kalanlar, Başlık/özet eleme tablosu, Hedefli arama (kanıt protokolü Katman 1 ve 3), Hedefli doğrulama (kanıt protokolü Katman 1 ve 3), Kurul için açık sorular, Omega-3 (EPA + DHA) · arama kaydı, PRISMA akış sayıları, Sistematik arama (v0.4 D4) (+1 more)

### Community 42 - "sikayet_yolu"
Cohesion: 0.20
Nodes (11): sikayet_yolu(), sikayet_id(), sikayet_yollari(), test_dogal_ifade_yorgunluk_yoluna_gider(), test_kanit_karti_yoksa_hazirlaniyor_der(), test_kaynaklar_dogrulanmis(), test_tahlil_oncesi_takviye_uyarisi(), test_tanimsiz_sikayet_hazir_yollari_listeler() (+3 more)

### Community 43 - "kurul_paketi.py"
Cohesion: 0.46
Nodes (11): _alan(), demo(), h(), _karar(), kartlar(), _kaynak(), _kaynaklar(), kurallar() (+3 more)

### Community 44 - "kart_onizleme.mjs"
Cohesion: 0.20
Nodes (4): { chromium }, senaryolar, rapor, require

### Community 48 - "etken_madde_rehberi"
Cohesion: 0.13
Nodes (25): etken_madde_rehberi(), _metin(), taslak(), test_b12_form_bolumu_dolu(), test_b12_metformin_grubu_one_cikar(), test_beyan_baska_maddeye_sizmaz(), test_d_vitamini_tam_cikti(), test_doz_onermez() (+17 more)

### Community 49 - "_madde_ozeti"
Cohesion: 0.15
Nodes (9): _kart_ozeti(), _kosul_saglanir(), _liste(), _madde_ozeti(), sonuc_etiketi(), kart_durumu(), zorunlu_uyarilar(), test_ek4_tek_gosterim_kurali() (+1 more)

### Community 53 - "__init__.py"
Cohesion: 0.09
Nodes (4): _mesajlar(), taslak_ayari(), test_demir_erkek_notu_yalnizca_erkekte(), test_tahlil_oncesi_uyarisi()

### Community 54 - "sayac.py"
Cohesion: 0.10
Nodes (19): K1 · Sağlık verisinin anlık işlenmesi, K2 · Barındırma yeri ve yurt dışı aktarım, K3 · Platform logları, K4 · Sohbet içeriği (Claude / ChatGPT sağlayıcısı), K5 · Tahlil kartında saklama, K6 · Çocuklar (ebeveyn kullanımı), Karar paketi C1 · KVKK, Kararlar (+11 more)

### Community 55 - "karsilastir"
Cohesion: 0.13
Nodes (15): senaryolar(), _sonuc(), _genel_kilavuz(), karsilastir(), _kartsiz_yanit(), katalog_sayfasi(), _katalog_sayisi_metni(), tahlil_goster() (+7 more)

### Community 56 - "test_faz3.py"
Cohesion: 0.11
Nodes (14): 1. Sunucunun işlediği veriler, 2. Teknik önlemler (uygulanmış), 3. Karar bekleyen noktalar, 4. İmza, KVKK kontrol listesi · Faz 3 kapısı, taslak(), test_kiyas_form_ve_tek_bilesen_suzgeci(), test_kiyas_karti_olmayan_maddede_urun_listelemez() (+6 more)

### Community 57 - "json"
Cohesion: 0.23
Nodes (9): anthropic_cagir(), dogru_mu(), main(), olc(), openai_cagir(), ozetle(), rapor_yaz(), sunucu_bilgisi() (+1 more)

### Community 58 - "argparse"
Cohesion: 0.24
Nodes (5): denetle(), main(), bicimle(), yaz(), main()

### Community 59 - "gecikme_olc.py"
Cohesion: 0.27
Nodes (6): denetle(), main(), main(), olc(), rapor(), yuzdelik()

### Community 60 - "test_mcp_sunucu.py"
Cohesion: 0.23
Nodes (7): _arac_testleri(), _initialize(), test_bellek_ici_protokol(), test_izinli_ngrok_adresi_kabul_edilir(), test_izinsiz_host_reddedilir(), test_render_adresi_kabul_edilir(), test_streamable_http_mcp()

### Community 61 - "properties"
Cohesion: 0.15
Nodes (13): format, type, type, type, properties, analiz_tarihi, laboratuvar, not (+5 more)

### Community 62 - "ikinci_goz.py"
Cohesion: 0.32
Nodes (6): form_html(), kappa(), _kaynak_satiri(), main(), orneklem(), tum_kartlar()

### Community 63 - "properties"
Cohesion: 0.17
Nodes (12): type, type, type, properties, minimum, type, birim, etiketteki (+4 more)

### Community 64 - "olcum.py"
Cohesion: 0.30
Nodes (6): _bos_port(), main(), _olc(), _yuzdelik(), _bos_port(), http_sunucu()

### Community 65 - "yayin_onayi"
Cohesion: 0.22
Nodes (9): type, onaylayan, tarih, yayin_onayi, format, type, properties, required (+1 more)

### Community 66 - "Takviye Bilimi v0.4 · durum"
Cohesion: 0.25
Nodes (7): A. Ölçüm altyapısı, B. Yayına alma, C. Karar paketleri, D. İçerik (hepsi taslak, kurul paketinde), Ortam engelleri (bu oturum), Takviye Bilimi v0.4 · durum, Ön koşul: v0.3 iş paketi (bu oturumda uygulandı)

### Community 67 - "C vitamini · arama kaydı"
Cohesion: 0.29
Nodes (6): Başlık/özet eleme tablosu, C vitamini · arama kaydı, Hedefli doğrulama (kanıt protokolü Katman 1 ve 3), Kurul için açık sorular, PRISMA akış sayıları, Sistematik arama (v0.4 D4)

### Community 68 - "Çinko · arama kaydı"
Cohesion: 0.29
Nodes (6): Başlık/özet eleme tablosu, Hedefli doğrulama (kanıt protokolü Katman 1 ve 3), Kurul için açık sorular, PRISMA akış sayıları, Sistematik arama (v0.4 D4), Çinko · arama kaydı

### Community 69 - "Folik asit · arama kaydı"
Cohesion: 0.29
Nodes (6): Başlık/özet eleme tablosu, Folik asit · arama kaydı, Hedefli doğrulama (kanıt protokolü Katman 1 ve 3), Kurul için açık sorular, PRISMA akış sayıları, Sistematik arama (v0.4 D4)

### Community 70 - "parti_analizi.schema.json"
Cohesion: 0.29
Nodes (6): required, $schema, then, required, title, type

### Community 71 - "demo"
Cohesion: 0.33
Nodes (6): const, description, type, if, properties, demo

### Community 72 - "sonuclar"
Cohesion: 0.33
Nodes (6): required, type, sonuclar, items, minItems, type

### Community 73 - "Claude canlı test kiti (v0.4 A4)"
Cohesion: 0.33
Nodes (5): 1. Kart matrisi, 2. Kronometre protokolü, 3. Kartlı araç kısıtı testi, 4. Ekran görüntüsü kuralları (bağlayıcı dizini başvurusu), Claude canlı test kiti (v0.4 A4)

### Community 74 - "Karar paketi C3 · Hukuk soru notu"
Cohesion: 0.33
Nodes (5): Bağlam (bugünkü tasarım), Hukukçunun bakacağı başlıklar, Karar paketi C3 · Hukuk soru notu, Riski azaltan iki tasarım seçeneği, Soru

### Community 75 - "Karar paketi C7 · Parti analizleri: kalite/laboratuvar ekibine veri talebi"
Cohesion: 0.33
Nodes (5): İstenen alanlar (parti başına, etken madde başına bir satır), İçe aktarma, Karar paketi C7 · Parti analizleri: kalite/laboratuvar ekibine veri talebi, Neden, Yayın onayı kimde

### Community 76 - "gorunen_ad"
Cohesion: 0.33
Nodes (5): gorunen_ad(), kopru_kartlar(), _madde_adi(), _profil_parametreleri(), _rehber_adi()

### Community 77 - "gercek_parti_analizi_var"
Cohesion: 0.40
Nodes (5): gercek_parti_analizi_var(), parti_analizleri(), parti_bul(), test_demo_kayit_urunun_parti_analizi_bilgisini_degistirmez(), test_demo_kaydi_korunur()

### Community 78 - "Karar paketi C6 · Ürün kartında ambalaj görseli"
Cohesion: 0.40
Nodes (4): Karar paketi C6 · Ürün kartında ambalaj görseli, Prototip, Seçenekler, Ölçüm (yerel, 30 tekrar, `urun_rehberi`)

### Community 79 - "Karar paketi C5 · TB-24 etiket uyarıları: veri talebi"
Cohesion: 0.40
Nodes (4): Doğrulama ve yayın, İstenen veri, Karar paketi C5 · TB-24 etiket uyarıları: veri talebi, Neden

### Community 80 - "Duman testi · 2026-10-30"
Cohesion: 0.40
Nodes (4): Duman testi · 2026-10-30, Geçenler, Hatalar, Kart eşlemesi

### Community 81 - "Gecikme ölçümü · 2026-10-30"
Cohesion: 0.40
Nodes (4): Araçlar (tools/call), Gecikme ölçümü · 2026-10-30, Kartlar (resources/read), Soğuk başlangıç

### Community 82 - "akreditasyon_no"
Cohesion: 0.67
Nodes (3): description, type, akreditasyon_no

### Community 83 - "parti_no"
Cohesion: 0.67
Nodes (3): minLength, type, parti_no

## Knowledge Gaps
- **28 isolated node(s):** `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema`, `uyari response field (not a medicine disclaimer)`, `Tier 3: mandatory large RCTs (VITAL, D-Health, DO-HEALTH, ViDA, ASCEND, STRENGTH, REDUCE-IT, MRC)` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 393 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `etken_madde_rehberi()` connect `etken_madde_rehberi` to `Server App & Schemas`, `test_v03.py`, `normalize`, `test_kanit_kartlari.py`, `veri.py`, `gorunen_ad`, `_madde_ozeti`, `__init__.py`, `sayac.py`, `karsilastir`, `araclar.py`, `ozet.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Server App & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.06993006993006994 - nodes in this community are weakly interconnected._
- **Why does `kisisel_rutin()` connect `kisisel_rutin` to `Server App & Schemas`, `test_v03.py`, `standart_miktar`, `_madde_ozeti`, `sayac.py`, `karsilastir`, `araclar.py`, `test_katalog_dogrulama.py`, `ozet.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Should `test_kanit_kartlari.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07560975609756097 - nodes in this community are weakly interconnected._
- **Why does `yasam_karnesi()` connect `yasam_karnesi` to `Server App & Schemas`, `test_v03.py`, `test_kanit_kartlari.py`, `kisisel_rutin`, `sayac.py`, `karsilastir`, `araclar.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `kisisel_rutin` be split into smaller, more focused modules?**
  _Cohesion score 0.12043010752688173 - nodes in this community are weakly interconnected._