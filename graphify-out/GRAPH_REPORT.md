# Graph Report - takviye-bilimi  (2026-10-30)

## Corpus Check
- 76 files · ~78,346 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .css 1)

## Summary
- 608 nodes · 1286 edges · 48 communities (29 shown, 19 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c979841f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- araclar.py
- Server App & Schemas
- MCP HTTP Integration Tests
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
- etken_madde_rehberi
- D vitamini · arama kaydı
- test_katalog_dogrulama.py
- test_ozet.py
- Katalog bulguları · Orzax web ve regülasyon ekibine bildirim
- 2026-10-30_faz0_once.md
- 2026-10-30_faz0_sonra.md
- urun_rehberi
- normalize
- kurallar
- standart_miktar
- B12 vitamini · arama kaydı
- Demir · arama kaydı
- Magnezyum · arama kaydı
- Omega-3 (EPA + DHA) · arama kaydı
- sikayet_yolu
- beyan_satirlarini_birlestir
- kart_onizleme.mjs
- 2026-10-30_faz1_sonra.md
- 2026-10-30_faz2_sonra.md
- ortak.js

## God Nodes (most connected - your core abstractions)
1. `etken_madde_rehberi()` - 56 edges
2. `kisisel_rutin()` - 43 edges
3. `yasam_karnesi()` - 41 edges
4. `urun_rehberi()` - 25 edges
5. `urunler()` - 23 edges
6. `sikayet_yolu()` - 21 edges
7. `kurallar()` - 19 edges
8. `normalize()` - 16 edges
9. `kaynak_kayitlari()` - 15 edges
10. `katalog_sayfasi()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `urun_rehberi tool` --semantically_similar_to--> `urun_bilimi MCP tool (planned)`  [INFERRED] [semantically similar]
  README.md → docs/KANIT_PROTOKOLU.md
- `Rule 8: Absolute numbers first` --semantically_similar_to--> `Plain Turkish rules (60-word summary, B1 level)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/KANIT_PROTOKOLU.md
- `test_streamable_http_mcp()` --indirect_call--> `yaz()`  [INFERRED]
  tests/test_mcp_sunucu.py → scripts/json_yaz.py
- `test_urun_rehberi_karantinadaki_satiri_isaretler()` --calls--> `urun_rehberi()`  [EXTRACTED]
  tests/test_katalog_dogrulama.py → server/araclar.py
- `test_urun_karti_uretici_kaynagini_ve_efsa_belgesini_ayri_turle_verir()` --calls--> `urun_rehberi()`  [EXTRACTED]
  tests/test_kaynaklar.py → server/araclar.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Current prototype MCP tools** — readme_urun_rehberi, readme_parti_analizi, readme_kisisel_rutin, readme_yasam_karnesi [EXTRACTED 1.00]
- **Evidence pipeline: search -> grade -> card -> validate -> board** — docs_kanit_protokolu_arama_ve_secim, docs_kanit_protokolu_kanit_duzeyi, docs_kanit_protokolu_kanit_karti_semasi, docs_kanit_protokolu_otomatik_dogrulama, docs_kanit_protokolu_medikal_kurul [INFERRED 0.85]
- **Public exposure and client connection** — readme_render_deploy, readme_ngrok_tunnel, readme_dns_rebinding_protection, readme_claude_connector, readme_chatgpt_developer_mode [INFERRED 0.85]

## Communities (48 total, 19 thin omitted)

### Community 0 - "araclar.py"
Cohesion: 0.07
Nodes (31): _cevap_metni(), DigerUrun, _etiket_miktari(), _genel_kilavuz(), Icerik, _karantina_metni(), KarneCevaplari, _kartsiz_yanit() (+23 more)

### Community 1 - "Server App & Schemas"
Cohesion: 0.08
Nodes (22): etken_madde_rehberi(), _guvenlik(), kanit_arayuzu(), karne_arayuzu(), katalog_sayfasi(), kisisel_rutin(), main(), parti_analizi() (+14 more)

### Community 2 - "MCP HTTP Integration Tests"
Cohesion: 0.07
Nodes (20): calistir(), main(), senaryolar(), _sonuc(), _bos_port(), main(), _olc(), _yuzdelik() (+12 more)

### Community 3 - "test_kanit_kartlari.py"
Cohesion: 0.11
Nodes (18): _kunye(), kaynak_kayitlari(), _katman_1(), _kelime_sayisi(), _rakamlar(), test_kart_semasi(), test_kartta_en_az_iki_kaynak_biri_katman_1(), test_karttaki_sayilar_kaynak_alintisinda_gecer() (+10 more)

### Community 4 - "kisisel_rutin"
Cohesion: 0.16
Nodes (24): kisisel_rutin(), _soru_var(), test_bos_rutin(), test_cocukta_d3_siniri_yasa_gore_degisir(), test_collagen_mag_plus_ve_d3k2_birlikte(), test_demir_ve_kalsiyum_arasinda_2_saat(), test_dogrulanan_kisim_siniri_asiyorsa_asim_kesindir(), test_doz_onermez_ve_urun_tavsiye_etmez() (+16 more)

### Community 5 - "veri.py"
Cohesion: 0.18
Nodes (12): main(), beyanlar(), kanit_tabani_kimlikleri(), katalog_tarihi(), monografi(), _monografiler(), _sunulabilir(), taslaklar_gosterilsin() (+4 more)

### Community 6 - "Evidence Pipeline Rules"
Cohesion: 0.18
Nodes (9): NCBI_API_KEY environment, Forbidden phrases list (lint_ifadeler.py), APIs: PubMed E-utilities, Europe PMC, Crossref, ClinicalTrials.gov, Search and selection process (arama_kaydi.md), Quarterly update cycle, Pending legal opinion: scientific cards as promotion, Medical board approval workflow (taslak -> onaylandi), Automated validation tests (re-fetch sources, retraction, lint, second look) (+1 more)

### Community 7 - "Render Deployment Config"
Cohesion: 0.18
Nodes (10): key, value, services, buildCommand, envVars, name, plan, runtime (+2 more)

### Community 8 - "re"
Cohesion: 0.09
Nodes (28): bicimle(), yaz(), _crossref(), dogrula(), _getir(), main(), _ncbi(), _pubmed() (+20 more)

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
Cohesion: 0.05
Nodes (41): _aralik(), _kopruler(), _kural_saglanir(), _puan(), _puanla(), _rehber_id(), yasam_karnesi(), karne_kurallari() (+33 more)

### Community 14 - "Public Exposure & ChatGPT"
Cohesion: 0.67
Nodes (3): ChatGPT Developer Mode setup, DNS rebinding protection / TB_ALLOWED_HOSTS, ngrok HTTPS tunnel

### Community 27 - "etken_madde_rehberi"
Cohesion: 0.07
Nodes (36): _beyan_anahtari(), etken_madde_rehberi(), _katalog_eslesmesi(), _rehber_adi(), etken_madde_adi(), zorunlu_uyarilar(), _metin(), taslak() (+28 more)

### Community 28 - "D vitamini · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, D vitamini · arama kaydı, Hatalı kimlikler, Hedefli doğrulama (kanıt protokolü, Katman 1 ve 3)

### Community 29 - "test_katalog_dogrulama.py"
Cohesion: 0.22
Nodes (8): brd_yuzdesi(), satir_miktari(), _satir(), test_brd_yuzdesi_ayristirma(), test_karantinadaki_her_satir_gerekce_tasir_ve_tutarli_satirlar_gecer(), test_supheli_satir_karantinada(), test_urun_rehberi_karantinadaki_satiri_isaretler(), test_yuksek_ama_tutarli_miktar_karantinaya_dusmez()

### Community 30 - "test_ozet.py"
Cohesion: 0.12
Nodes (14): _etken_madde_rehberi(), _kaynak_satirlari(), _kisisel_rutin(), _madde(), metin(), _sikayet_yolu(), _urun_rehberi(), _yasam_karnesi() (+6 more)

### Community 31 - "Katalog bulguları · Orzax web ve regülasyon ekibine bildirim"
Cohesion: 0.50
Nodes (3): Elle görülen bulgular, Karantinadaki içerik satırları, Katalog bulguları · Orzax web ve regülasyon ekibine bildirim

### Community 34 - "urun_rehberi"
Cohesion: 0.29
Nodes (12): urun_rehberi(), urun_ara(), urunler(), test_belirsiz_sorgu_adaylari_alfabetik_dondurur(), test_beyan_kosulu_ayri_alanda(), test_bulunamayan_urun_benzerleri_alfabetik_listeler(), test_parca_beyan_satirlari_birlesir(), test_sitede_okunamayan_hucre_tahmin_edilmez() (+4 more)

### Community 35 - "normalize"
Cohesion: 0.20
Nodes (7): _beyan_adlari(), etken_madde_id(), normalize(), urun_beyanlari(), urun_saglik_beyanlari(), test_bilesik_adlari_elementel_mineralle_eslesmez(), test_katalog_yalnizca_orzax_ve_kaynakli()

### Community 36 - "kurallar"
Cohesion: 0.19
Nodes (7): kurallar(), ust_sinir(), _metin_alanlari(), test_etkilesim_kurallarinin_ilac_gruplari_tanimli(), test_urunlerin_etken_madde_kimlikleri_tanimli(), test_ust_sinirlar_dogrulanmis_kaynaklara_bagli(), test_yasakli_ifade_yok()

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
Cohesion: 0.40
Nodes (4): Açık kalanlar, Hedefli arama (kanıt protokolü Katman 1 ve 3), Omega-3 (EPA + DHA) · arama kaydı, Sonuç

### Community 42 - "sikayet_yolu"
Cohesion: 0.18
Nodes (12): _kosul_saglanir(), sikayet_yolu(), sikayet_id(), sikayet_yollari(), test_dogal_ifade_yorgunluk_yoluna_gider(), test_kanit_karti_yoksa_hazirlaniyor_der(), test_kaynaklar_dogrulanmis(), test_tahlil_oncesi_takviye_uyarisi() (+4 more)

### Community 44 - "kart_onizleme.mjs"
Cohesion: 0.20
Nodes (4): { chromium }, senaryolar, rapor, require

## Knowledge Gaps
- **28 isolated node(s):** `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema`, `uyari response field (not a medicine disclaimer)`, `Tier 3: mandatory large RCTs (VITAL, D-Health, DO-HEALTH, ViDA, ASCEND, STRENGTH, REDUCE-IT, MRC)` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 215 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `etken_madde_rehberi()` connect `etken_madde_rehberi` to `araclar.py`, `Server App & Schemas`, `MCP HTTP Integration Tests`, `test_kanit_kartlari.py`, `kurallar`, `veri.py`, `normalize`, `urun_rehberi`, `sikayet_yolu`, `yasam_karnesi`, `test_ozet.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **What connects `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `araclar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06826241134751773 - nodes in this community are weakly interconnected._
- **Why does `kisisel_rutin()` connect `kisisel_rutin` to `araclar.py`, `Server App & Schemas`, `MCP HTTP Integration Tests`, `normalize`, `kurallar`, `standart_miktar`, `urun_rehberi`, `etken_madde_rehberi`, `test_katalog_dogrulama.py`, `test_ozet.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Should `Server App & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.0783744557329463 - nodes in this community are weakly interconnected._
- **Why does `yasam_karnesi()` connect `yasam_karnesi` to `araclar.py`, `Server App & Schemas`, `MCP HTTP Integration Tests`, `test_kanit_kartlari.py`, `test_ozet.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Should `MCP HTTP Integration Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07315233785822021 - nodes in this community are weakly interconnected._