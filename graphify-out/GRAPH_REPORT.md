# Graph Report - takviye-bilimi  (2026-10-29)

## Corpus Check
- Corpus is ~11,223 words - fits in a single context window. You may not need a graph.

## Summary
- 211 nodes · 345 edges · 27 communities (13 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.87)
- Token cost: 88,468 input · 0 output

## Community Hubs (Navigation)
- Tool Business Logic
- Server App & Schemas
- MCP HTTP Integration Tests
- Data Loading Helpers
- Personal Routine Tool
- Product Search Tool
- Evidence Pipeline Rules
- Render Deployment Config
- Data Integrity Tests
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

## God Nodes (most connected - your core abstractions)
1. `kisisel_rutin()` - 28 edges
2. `urun_rehberi()` - 15 edges
3. `yasam_karnesi()` - 13 edges
4. `kisisel_rutin()` - 12 edges
5. `kurallar()` - 12 edges
6. `_urun_karti()` - 11 edges
7. `parti_analizi()` - 11 edges
8. `urunler()` - 10 edges
9. `yasam_karnesi()` - 9 edges
10. `services` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Rule 8: Absolute numbers first` --semantically_similar_to--> `Plain Turkish rules (60-word summary, B1 level)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/KANIT_PROTOKOLU.md
- `urun_rehberi tool` --semantically_similar_to--> `urun_bilimi MCP tool (planned)`  [INFERRED] [semantically similar]
  README.md → docs/KANIT_PROTOKOLU.md
- `test_istenen_urunler_katalogda()` --calls--> `urunler()`  [EXTRACTED]
  tests/test_veri.py → server/veri.py
- `test_etkilesim_kurallarinin_ilac_gruplari_tanimli()` --calls--> `kurallar()`  [EXTRACTED]
  tests/test_veri.py → server/veri.py
- `test_ust_sinir_kaynaklari_dogrulanmadi_olarak_isaretli()` --calls--> `kurallar()`  [EXTRACTED]
  tests/test_veri.py → server/veri.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Current prototype MCP tools** — readme_urun_rehberi, readme_parti_analizi, readme_kisisel_rutin, readme_yasam_karnesi [EXTRACTED 1.00]
- **Evidence pipeline: search -> grade -> card -> validate -> board** — docs_kanit_protokolu_arama_ve_secim, docs_kanit_protokolu_kanit_duzeyi, docs_kanit_protokolu_kanit_karti_semasi, docs_kanit_protokolu_otomatik_dogrulama, docs_kanit_protokolu_medikal_kurul [INFERRED 0.85]
- **Public exposure and client connection** — readme_render_deploy, readme_ngrok_tunnel, readme_dns_rebinding_protection, readme_claude_connector, readme_chatgpt_developer_mode [INFERRED 0.85]

## Communities (27 total, 14 thin omitted)

### Community 0 - "Tool Business Logic"
Cohesion: 0.12
Nodes (19): DigerUrun, Icerik, KarneCevaplari, _liste(), parti_analizi(), _parti_no_coz(), _puanla(), yasam_karnesi() (+11 more)

### Community 1 - "Server App & Schemas"
Cohesion: 0.12
Nodes (6): _guvenlik(), kisisel_rutin(), main(), parti_analizi(), urun_rehberi(), yasam_karnesi()

### Community 2 - "MCP HTTP Integration Tests"
Cohesion: 0.13
Nodes (9): _arac_testleri(), _bos_port(), http_sunucu(), _initialize(), test_bellek_ici_protokol(), test_izinli_ngrok_adresi_kabul_edilir(), test_izinsiz_host_reddedilir(), test_render_adresi_kabul_edilir() (+1 more)

### Community 3 - "Data Loading Helpers"
Cohesion: 0.16
Nodes (14): _sayi(), _sinir_metni(), _urun_karti(), _yas_metni(), beyanlar(), _birim_kodu(), etken_madde_adi(), etken_madde_id() (+6 more)

### Community 4 - "Personal Routine Tool"
Cohesion: 0.23
Nodes (15): kisisel_rutin(), _soru_var(), test_bos_rutin(), test_cocukta_d3_siniri_yasa_gore_degisir(), test_demir_ve_kalsiyum_arasinda_2_saat(), test_doz_onermez_ve_urun_tavsiye_etmez(), test_ilac_grubu_sorulari(), test_k_vitamini_ve_kan_sulandirici() (+7 more)

### Community 5 - "Product Search Tool"
Cohesion: 0.29
Nodes (10): urun_rehberi(), normalize(), urun_ara(), urunler(), test_belirsiz_sorgu_adaylari_dondurur(), test_bulunamayan_urun_katalogu_olcutuyle_listeler(), test_rakip_urun_ayni_sablonla_ve_eksik_bilgi_acikca(), test_tek_urun_karti() (+2 more)

### Community 6 - "Evidence Pipeline Rules"
Cohesion: 0.18
Nodes (9): NCBI_API_KEY environment, Forbidden phrases list (lint_ifadeler.py), APIs: PubMed E-utilities, Europe PMC, Crossref, ClinicalTrials.gov, Search and selection process (arama_kaydi.md), Quarterly update cycle, Pending legal opinion: scientific cards as promotion, Medical board approval workflow (taslak -> onaylandi), Automated validation tests (re-fetch sources, retraction, lint, second look) (+1 more)

### Community 7 - "Render Deployment Config"
Cohesion: 0.18
Nodes (10): key, value, services, buildCommand, envVars, name, plan, runtime (+2 more)

### Community 8 - "Data Integrity Tests"
Cohesion: 0.22
Nodes (4): test_etkilesim_kurallarinin_ilac_gruplari_tanimli(), test_istenen_urunler_katalogda(), test_ust_sinir_kaynaklari_dogrulanmadi_olarak_isaretli(), test_yasakli_ifade_yok()

### Community 9 - "Project Overview & Deps"
Cohesion: 0.25
Nodes (7): Takviye Bilimi project rules, Evidence protocol (Kanit Protokolu), MCP Inspector testing, Takviye Bilimi MCP server (prototype), httpx>=0.27, mcp[cli]>=1.26,<2, pytest / pytest-asyncio

### Community 10 - "Product vs Ingredient Rules"
Cohesion: 0.40
Nodes (4): 'Bu urundeki miktar' block (numbers only, no interpretation), urun_bilimi MCP tool (planned), kisisel_rutin tool, urun_rehberi tool

### Community 11 - "Evidence Cards & Grading"
Cohesion: 0.33
Nodes (5): bilimsel_temel MCP tool (planned), Evidence levels (simplified GRADE: A/B/C/D/Etkisiz/Dikkat), Evidence card schema, Monograph schema, uyari response field (not a medicine disclaimer)

### Community 14 - "Public Exposure & ChatGPT"
Cohesion: 0.67
Nodes (3): ChatGPT Developer Mode setup, DNS rebinding protection / TB_ALLOWED_HOSTS, ngrok HTTPS tunnel

## Knowledge Gaps
- **28 isolated node(s):** `takviye-bilimi`, `graphify skill trigger (/graphify)`, `Takviye Bilimi project rules`, `Forbidden phrases list (lint_ifadeler.py)`, `Planned folder structure (data/, scripts/, server/, kurul/)` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 86 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `kisisel_rutin()` connect `Personal Routine Tool` to `Tool Business Logic`, `Server App & Schemas`, `Data Loading Helpers`, `Product Search Tool`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **What connects `takviye-bilimi`, `graphify skill trigger (/graphify)`, `Takviye Bilimi project rules` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Tool Business Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.11822660098522167 - nodes in this community are weakly interconnected._
- **Why does `kisisel_rutin()` connect `Server App & Schemas` to `Tool Business Logic`, `Personal Routine Tool`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `Server App & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.12307692307692308 - nodes in this community are weakly interconnected._
- **Why does `yasam_karnesi()` connect `Tool Business Logic` to `Server App & Schemas`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `MCP HTTP Integration Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.13043478260869565 - nodes in this community are weakly interconnected._