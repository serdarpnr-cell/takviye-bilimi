# Graph Report - takviye-bilimi  (2026-10-29)

## Corpus Check
- 37 files · ~55,838 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 351 nodes · 699 edges · 29 communities (16 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3aaee210`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_veri.py
- Server App & Schemas
- MCP HTTP Integration Tests
- test_kanit_kartlari.py
- kisisel_rutin
- veri.py
- Evidence Pipeline Rules
- Render Deployment Config
- kaynak_dogrula.py
- Project Overview & Deps
- Product vs Ingredient Rules
- Evidence Cards & Grading
- Test Fixtures
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

## God Nodes (most connected - your core abstractions)
1. `etken_madde_rehberi()` - 36 edges
2. `kisisel_rutin()` - 34 edges
3. `urun_rehberi()` - 18 edges
4. `kurallar()` - 16 edges
5. `yasam_karnesi()` - 15 edges
6. `ayristir()` - 13 edges
7. `normalize()` - 13 edges
8. `kisisel_rutin()` - 12 edges
9. `etken_madde_rehberi()` - 12 edges
10. `urunler()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `urun_rehberi tool` --semantically_similar_to--> `urun_bilimi MCP tool (planned)`  [INFERRED] [semantically similar]
  README.md → docs/KANIT_PROTOKOLU.md
- `Rule 8: Absolute numbers first` --semantically_similar_to--> `Plain Turkish rules (60-word summary, B1 level)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/KANIT_PROTOKOLU.md
- `test_streamable_http_mcp()` --indirect_call--> `yaz()`  [INFERRED]
  tests/test_mcp_sunucu.py → scripts/json_yaz.py
- `test_urun_karti_uretici_kaynagini_ve_efsa_belgesini_ayri_turle_verir()` --calls--> `urun_rehberi()`  [EXTRACTED]
  tests/test_kaynaklar.py → server/araclar.py
- `test_etkilesim_kurallarinin_ilac_gruplari_tanimli()` --calls--> `kurallar()`  [EXTRACTED]
  tests/test_veri.py → server/veri.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Current prototype MCP tools** — readme_urun_rehberi, readme_parti_analizi, readme_kisisel_rutin, readme_yasam_karnesi [EXTRACTED 1.00]
- **Evidence pipeline: search -> grade -> card -> validate -> board** — docs_kanit_protokolu_arama_ve_secim, docs_kanit_protokolu_kanit_duzeyi, docs_kanit_protokolu_kanit_karti_semasi, docs_kanit_protokolu_otomatik_dogrulama, docs_kanit_protokolu_medikal_kurul [INFERRED 0.85]
- **Public exposure and client connection** — readme_render_deploy, readme_ngrok_tunnel, readme_dns_rebinding_protection, readme_claude_connector, readme_chatgpt_developer_mode [INFERRED 0.85]

## Communities (29 total, 13 thin omitted)

### Community 0 - "test_veri.py"
Cohesion: 0.25
Nodes (4): _metin_alanlari(), test_etkilesim_kurallarinin_ilac_gruplari_tanimli(), test_urunlerin_etken_madde_kimlikleri_tanimli(), test_yasakli_ifade_yok()

### Community 1 - "Server App & Schemas"
Cohesion: 0.11
Nodes (10): etken_madde_rehberi(), _guvenlik(), kisisel_rutin(), main(), parti_analizi(), urun_rehberi(), yasam_karnesi(), DigerUrun (+2 more)

### Community 2 - "MCP HTTP Integration Tests"
Cohesion: 0.15
Nodes (9): _arac_testleri(), _bos_port(), http_sunucu(), _initialize(), test_bellek_ici_protokol(), test_izinli_ngrok_adresi_kabul_edilir(), test_izinsiz_host_reddedilir(), test_render_adresi_kabul_edilir() (+1 more)

### Community 3 - "test_kanit_kartlari.py"
Cohesion: 0.11
Nodes (17): _kunye(), kaynak_kayitlari(), _kelime_sayisi(), _rakamlar(), test_kart_semasi(), test_kartta_en_az_iki_kaynak_biri_kilavuz_veya_duzenleyici(), test_karttaki_sayilar_kaynak_alintisinda_gecer(), test_monografi_semasi_ve_kaynaklari() (+9 more)

### Community 4 - "kisisel_rutin"
Cohesion: 0.18
Nodes (20): kisisel_rutin(), _liste(), _soru_var(), test_bos_rutin(), test_cocukta_d3_siniri_yasa_gore_degisir(), test_demir_ve_kalsiyum_arasinda_2_saat(), test_doz_onermez_ve_urun_tavsiye_etmez(), test_etiketteki_en_yuksek_gunluk_kullanim_esas_alinir() (+12 more)

### Community 5 - "veri.py"
Cohesion: 0.08
Nodes (28): _rehber_id(), urun_rehberi(), beyanlar(), _birim_kodu(), etken_madde_id(), kanit_tabani_kimlikleri(), katalog_tarihi(), _kaynak_gorunumu() (+20 more)

### Community 6 - "Evidence Pipeline Rules"
Cohesion: 0.18
Nodes (9): NCBI_API_KEY environment, Forbidden phrases list (lint_ifadeler.py), APIs: PubMed E-utilities, Europe PMC, Crossref, ClinicalTrials.gov, Search and selection process (arama_kaydi.md), Quarterly update cycle, Pending legal opinion: scientific cards as promotion, Medical board approval workflow (taslak -> onaylandi), Automated validation tests (re-fetch sources, retraction, lint, second look) (+1 more)

### Community 7 - "Render Deployment Config"
Cohesion: 0.18
Nodes (10): key, value, services, buildCommand, envVars, name, plan, runtime (+2 more)

### Community 8 - "kaynak_dogrula.py"
Cohesion: 0.08
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

### Community 12 - "Test Fixtures"
Cohesion: 0.13
Nodes (16): parti_analizi(), _parti_no_coz(), _puanla(), yasam_karnesi(), kaynaklar(), zarf(), test_kaynaksiz_yanit_uretilemez(), test_karekod_ve_parti_no_bicimleri_cozulur() (+8 more)

### Community 14 - "Public Exposure & ChatGPT"
Cohesion: 0.67
Nodes (3): ChatGPT Developer Mode setup, DNS rebinding protection / TB_ALLOWED_HOSTS, ngrok HTTPS tunnel

### Community 27 - "etken_madde_rehberi"
Cohesion: 0.09
Nodes (32): _beyan_anahtari(), _etiket_miktari(), etken_madde_rehberi(), _katalog_eslesmesi(), _kosul_saglanir(), _rehber_adi(), _sayi(), _sinir_metni() (+24 more)

### Community 28 - "D vitamini · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, D vitamini · arama kaydı, Hatalı kimlikler, Hedefli doğrulama (kanıt protokolü, Katman 1 ve 3)

## Knowledge Gaps
- **28 isolated node(s):** `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema`, `uyari response field (not a medicine disclaimer)`, `Tier 3: mandatory large RCTs (VITAL, D-Health, DO-HEALTH, ViDA, ASCEND, STRENGTH, REDUCE-IT, MRC)` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 122 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `kisisel_rutin()` connect `kisisel_rutin` to `Server App & Schemas`, `etken_madde_rehberi`, `Test Fixtures`, `veri.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **What connects `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Server App & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.11290322580645161 - nodes in this community are weakly interconnected._
- **Why does `etken_madde_rehberi()` connect `etken_madde_rehberi` to `Server App & Schemas`, `test_kanit_kartlari.py`, `kisisel_rutin`, `veri.py`, `Test Fixtures`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Should `MCP HTTP Integration Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._
- **Why does `etken_madde_rehberi()` connect `Server App & Schemas` to `etken_madde_rehberi`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `test_kanit_kartlari.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11083743842364532 - nodes in this community are weakly interconnected._