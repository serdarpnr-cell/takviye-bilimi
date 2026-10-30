# Graph Report - takviye-bilimi  (2026-10-30)

## Corpus Check
- 50 files · ~64,123 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 465 nodes · 967 edges · 34 communities (19 shown, 15 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f76d538d`
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
- urun_rehberi
- arayuz.py
- Katalog bulguları · Orzax web ve regülasyon ekibine bildirim
- 2026-10-30_faz0_once.md
- 2026-10-30_faz0_sonra.md

## God Nodes (most connected - your core abstractions)
1. `etken_madde_rehberi()` - 44 edges
2. `kisisel_rutin()` - 38 edges
3. `yasam_karnesi()` - 31 edges
4. `urun_rehberi()` - 19 edges
5. `kurallar()` - 18 edges
6. `urunler()` - 17 edges
7. `kaynak_kayitlari()` - 14 edges
8. `ayristir()` - 13 edges
9. `normalize()` - 13 edges
10. `kisisel_rutin()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `urun_rehberi tool` --semantically_similar_to--> `urun_bilimi MCP tool (planned)`  [INFERRED] [semantically similar]
  README.md → docs/KANIT_PROTOKOLU.md
- `Rule 8: Absolute numbers first` --semantically_similar_to--> `Plain Turkish rules (60-word summary, B1 level)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/KANIT_PROTOKOLU.md
- `test_streamable_http_mcp()` --indirect_call--> `yaz()`  [INFERRED]
  tests/test_mcp_sunucu.py → scripts/json_yaz.py
- `test_urun_karti_uretici_kaynagini_ve_efsa_belgesini_ayri_turle_verir()` --calls--> `urun_rehberi()`  [EXTRACTED]
  tests/test_kaynaklar.py → server/araclar.py
- `test_taslak_bayragi_acikken_taslaklar_sunulur()` --calls--> `monografi()`  [EXTRACTED]
  tests/test_kanit_kartlari.py → server/veri.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Current prototype MCP tools** — readme_urun_rehberi, readme_parti_analizi, readme_kisisel_rutin, readme_yasam_karnesi [EXTRACTED 1.00]
- **Evidence pipeline: search -> grade -> card -> validate -> board** — docs_kanit_protokolu_arama_ve_secim, docs_kanit_protokolu_kanit_duzeyi, docs_kanit_protokolu_kanit_karti_semasi, docs_kanit_protokolu_otomatik_dogrulama, docs_kanit_protokolu_medikal_kurul [INFERRED 0.85]
- **Public exposure and client connection** — readme_render_deploy, readme_ngrok_tunnel, readme_dns_rebinding_protection, readme_claude_connector, readme_chatgpt_developer_mode [INFERRED 0.85]

## Communities (34 total, 15 thin omitted)

### Community 0 - "araclar.py"
Cohesion: 0.09
Nodes (22): _cevap_metni(), DigerUrun, _etiket_miktari(), _genel_kilavuz(), Icerik, _karantina_metni(), KarneCevaplari, _kartsiz_yanit() (+14 more)

### Community 1 - "Server App & Schemas"
Cohesion: 0.13
Nodes (7): etken_madde_rehberi(), _guvenlik(), kisisel_rutin(), main(), parti_analizi(), urun_rehberi(), yasam_karnesi()

### Community 2 - "MCP HTTP Integration Tests"
Cohesion: 0.12
Nodes (13): _bos_port(), main(), _olc(), _yuzdelik(), _arac_testleri(), _bos_port(), http_sunucu(), _initialize() (+5 more)

### Community 3 - "test_kanit_kartlari.py"
Cohesion: 0.21
Nodes (10): _kelime_sayisi(), _rakamlar(), test_kart_semasi(), test_kartta_en_az_iki_kaynak_biri_kilavuz_veya_duzenleyici(), test_karttaki_sayilar_kaynak_alintisinda_gecer(), test_monografi_semasi_ve_kaynaklari(), test_sunucu_yalnizca_onayli_kayitlari_sunar(), test_taslak_bayragi_acikken_taslaklar_sunulur() (+2 more)

### Community 4 - "kisisel_rutin"
Cohesion: 0.15
Nodes (23): kisisel_rutin(), urun_kaynagi(), _soru_var(), test_bos_rutin(), test_cocukta_d3_siniri_yasa_gore_degisir(), test_collagen_mag_plus_ve_d3k2_birlikte(), test_demir_ve_kalsiyum_arasinda_2_saat(), test_dogrulanan_kisim_siniri_asiyorsa_asim_kesindir() (+15 more)

### Community 5 - "veri.py"
Cohesion: 0.06
Nodes (36): main(), _kunye(), beyanlar(), _birim_kodu(), _ima_edilen_brd(), kanit_tabani_kimlikleri(), karne_kurallari(), katalog_dogrula() (+28 more)

### Community 6 - "Evidence Pipeline Rules"
Cohesion: 0.18
Nodes (9): NCBI_API_KEY environment, Forbidden phrases list (lint_ifadeler.py), APIs: PubMed E-utilities, Europe PMC, Crossref, ClinicalTrials.gov, Search and selection process (arama_kaydi.md), Quarterly update cycle, Pending legal opinion: scientific cards as promotion, Medical board approval workflow (taslak -> onaylandi), Automated validation tests (re-fetch sources, retraction, lint, second look) (+1 more)

### Community 7 - "Render Deployment Config"
Cohesion: 0.18
Nodes (10): key, value, services, buildCommand, envVars, name, plan, runtime (+2 more)

### Community 8 - "re"
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

### Community 12 - "yasam_karnesi"
Cohesion: 0.07
Nodes (31): _aralik(), _kopruler(), _kural_saglanir(), _puan(), _puanla(), _rehber_id(), yasam_karnesi(), etken_madde_id() (+23 more)

### Community 14 - "Public Exposure & ChatGPT"
Cohesion: 0.67
Nodes (3): ChatGPT Developer Mode setup, DNS rebinding protection / TB_ALLOWED_HOSTS, ngrok HTTPS tunnel

### Community 27 - "etken_madde_rehberi"
Cohesion: 0.10
Nodes (25): etken_madde_rehberi(), _katalog_eslesmesi(), _rehber_adi(), etken_madde_adi(), _metin(), taslak(), test_d_vitamini_tam_cikti(), test_doz_onermez() (+17 more)

### Community 28 - "D vitamini · arama kaydı"
Cohesion: 0.40
Nodes (4): Açık kalanlar, D vitamini · arama kaydı, Hatalı kimlikler, Hedefli doğrulama (kanıt protokolü, Katman 1 ve 3)

### Community 29 - "urun_rehberi"
Cohesion: 0.09
Nodes (24): _beyan_anahtari(), _urun_beyanlari(), urun_rehberi(), brd_yuzdesi(), normalize(), satir_miktari(), urun_ara(), urun_beyanlari() (+16 more)

### Community 30 - "arayuz.py"
Cohesion: 0.14
Nodes (8): karne_arayuzu(), karne_html(), _sayfa(), _arayuzler(), _gorunur_metin(), test_arayuze_bagli_her_aracin_kaynagi_kayitli(), test_her_arayuzde_marka_alt_bilgisi_var(), test_arayuz_tum_kodlari_icerir_ve_dis_kaynak_yuklemez()

### Community 31 - "Katalog bulguları · Orzax web ve regülasyon ekibine bildirim"
Cohesion: 0.50
Nodes (3): Elle görülen bulgular, Karantinadaki içerik satırları, Katalog bulguları · Orzax web ve regülasyon ekibine bildirim

## Knowledge Gaps
- **28 isolated node(s):** `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema`, `uyari response field (not a medicine disclaimer)`, `Tier 3: mandatory large RCTs (VITAL, D-Health, DO-HEALTH, ViDA, ASCEND, STRENGTH, REDUCE-IT, MRC)` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 156 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `etken_madde_rehberi()` connect `etken_madde_rehberi` to `araclar.py`, `Server App & Schemas`, `kisisel_rutin`, `veri.py`, `yasam_karnesi`, `urun_rehberi`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **What connects `takviye-bilimi`, `kisisel_rutin tool`, `Monograph schema` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `araclar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0946969696969697 - nodes in this community are weakly interconnected._
- **Why does `kisisel_rutin()` connect `kisisel_rutin` to `araclar.py`, `Server App & Schemas`, `veri.py`, `yasam_karnesi`, `etken_madde_rehberi`, `urun_rehberi`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Should `Server App & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.1349206349206349 - nodes in this community are weakly interconnected._
- **Why does `yasam_karnesi()` connect `yasam_karnesi` to `araclar.py`, `Server App & Schemas`, `veri.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `MCP HTTP Integration Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.12043010752688173 - nodes in this community are weakly interconnected._