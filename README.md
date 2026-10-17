# 🏦 CrossPay (微众智汇) — AI Financial Assistant for International Students

[![WeBank International AI Finance Challenge](https://img.shields.io/badge/WeBank-International%20Track-0A2463?style=for-the-badge&logo=bank)]()
[![Topic C: Cross-Border & Student Finance](https://img.shields.io/badge/Topic-C%3A%20Cross--border%20Finance-059669?style=for-the-badge)]()
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python)]()
[![Gemini 3.8 Flash](https://img.shields.io/badge/Gemini-3.8%20Flash-EA4335?style=for-the-badge&logo=google)]()
[![Tests Passing](https://img.shields.io/badge/Tests-135%2F135%20Passing-brightgreen?style=for-the-badge)]()
[![Bilingual EN/ZH](https://img.shields.io/badge/Language-English%20%7C%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-blue?style=for-the-badge)]()

**CrossPay** is a competition-grade AI financial assistant designed for international students studying in China, built for the **WeBank International AI Finance Challenge (Topic C: Cross-Border & Student Finance)**.

Powered by a **Dual Autonomous Intelligence Engine** (100% Offline Rule/Statistical Engine + Google Gemini 3.8 Flash fallback) with a deterministic Python financial tool execution layer, CrossPay ensures **zero mathematical hallucination**, bank-grade two-step write confirmation, PBOC/SAFE regulatory compliance, PRC Anti-Telecom Fraud Law & "Card Break Action" protection, PBOC central parity quotes, SAFE Circular [2020] No.17 tuition quota exemptions, Tukey's IQR spending anomaly detection, and a proprietary **Financial Health Score™** with downloadable audit PDF reports.

---

## 🌟 What Makes CrossPay Competition-Winning (v2.0)

| Dimension | Standard Prototype | CrossPay v2.0 (Our Build) |
|---|---|---|
| **Design System** | Generic UI | Custom WeBank Blue & Gold (`#0A2463`, `#E8B84B`), glassmorphic metric cards, responsive layout |
| **Architecture** | Single-page script | **6-Page Full Enterprise Application**: Executive Dashboard · Bilingual AI Assistant · Deep Analytics & Tukey IQR · Security & Settings · Global Macro Intelligence · AI Model Studio |
| **Language Support** | English only | **Full Bilingual Support** (🇬🇧 English / 🇨🇳 简体中文) with one-click live toggle & bilingual entity parsing |
| **Data Richness** | 3 static values | **5,000 Realistic Transactions** + 200 users, 6 months categorized history, 30-day daily FX rate trends, credit trajectories |
| **Analytics & Viz** | Plain text tables | **6+ Interactive Plotly Visualizations**: spending donut, monthly trend, credit growth, FX monitor, Tukey anomaly screener, remittance optimizer |
| **Central Bank & RegTech** | None | **PBOC Central Parity Rates** (中间价 $\pm 2\%$ band), **SAFE $50k Quota Exemption** (Circular [2020] No.17), **CIPS Clearing Windows** |
| **Fraud & Scam Defense** | None | **PRC Anti-Telecom Fraud Engine** (《反电信网络诈骗法》): tuition proxy scam defense, PBOC "Card Break Action" (断卡行动) private FX screening, 0–100 transaction risk index, 96110 hotline |
| **Financial Intelligence** | Reactive Q&A | **Proactive Smart Alerts** (tuition countdowns, favorable FX opportunities, low balance, credit tips, spending anomalies) |
| **Proprietary Metric** | None | **CrossPay Financial Health Score™** (0–100 composite index: credit 30%, discipline 25%, reserve 25%, tuition 20%) |
| **Formal Deliverables** | Screen captures | **One-Click Downloadable PDF Financial Audit Report** (ReportLab, branded, 3-page printable report) |
| **Compliance & Trust** | Generic notes | **3-Tier Permission Security Model**, $10,000 USD AML threshold screening, 10-country sanctions filter, PII masking |
| **Autonomy & Reliability** | Fails without API key | **100% Autonomous Offline Execution** (zero API key required for full core functionality, sub-15ms latency) |

---

## 🧭 Six-Page System Architecture

```
Project China/
├── app.py                      # Executive Portal & Launchpad
├── pages/
│   ├── 1_📊_Dashboard.py       # Financial Health Score, KPI cards, anti-fraud status, smart alerts, PDF export
│   ├── 2_🤖_AI_Assistant.py    # Bilingual Autonomous/Gemini AI chat with 2-step confirmation & anti-scam checks
│   ├── 3_📈_Analytics.py       # 6 interactive Plotly charts, Tukey IQR anomaly detection & cohort benchmarks
│   ├── 4_⚙️_Settings.py        # Student profiles, PII masking, AML/Sanctions & Anti-Telecom Fraud baselines
│   ├── 5_🌍_Global_Intelligence.py # 5,000 transaction global macro data, World Bank corridors, live API exchange rates
│   └── 6_🧪_AI_Model_Studio.py # AI dual-engine inference studio, latency benchmarks & test matrix
├── src/
│   ├── agent.py                # Stateful CrossPayAgent with tool loop & confirmation gate
│   ├── autonomous_engine.py    # 100% offline regex & rule-based bilingual NLU engine (<15ms latency)
│   ├── health_score.py         # Proprietary Financial Health Score™ multi-factor engine
│   ├── alerts.py               # Proactive financial risk & opportunity alert generator
│   ├── pdf_report.py           # ReportLab audit report generation (returns valid PDF bytes)
│   ├── charts.py               # 6 Plotly interactive visualizers
│   ├── theme.py                # CSS injection & fintech HTML cards
│   ├── i18n.py                 # Full EN/ZH localization dictionary
│   ├── db.py                   # SQLite database (accounts, expenses, budgets, fx, alerts, credit)
│   ├── mock_data.py            # 3 student accounts with 6 months rich history
│   ├── logger.py               # Immutable JSONL audit logger with PII masking
│   ├── tool_registry.py        # 24 Gemini & Autonomous function declarations & dispatcher
│   └── tools/
│       ├── fx.py               # FX rates, PBOC central parity, volatility metrics, live API fallback
│       ├── remittance.py       # Provider benchmarking (WeBank Direct, Wise, UnionPay, SWIFT)
│       ├── budget.py           # Multi-category spending & 2-step confirmed expense recording
│       ├── credit.py           # Credit scoring, milestones, & action simulator
│       ├── compliance.py       # AML threshold ($10,000 USD), SAFE quota exemption, CIPS windows, sanctions list, PII regex
│       ├── analytics.py        # Historical FX, spending trends, Tukey IQR anomaly detection, cohort benchmarks
│       └── fraud.py            # Tuition proxy scams, PBOC 'Card Break' screening, multi-factor risk index
├── tests/                      # 135 automated pytest tests across 12 test suites (100% passing)
├── docs/                       # Formal competition deliverables (01, 02, 05, 06)
├── assets/style.css            # Fintech design styling
└── scripts/
    ├── generate_5000_transactions.py  # 5,000 transaction statistical dataset generator
    └── generate_execution_evidence.py # Deliverable 06 evidence generator
```

---

## 🔐 Bank-Grade Security & Compliance Model

```
┌────────────────────────────────────────────────────────┐
│                   3-TIER PERMISSION MODEL              │
├─────────┬──────────────────────┬───────────────────────┤
│ Tier 0  │ Read-Only            │ FX rates, remittance  │
│         │ (Unrestricted)       │ compare, spending     │
├─────────┼──────────────────────┼───────────────────────┤
│ Tier 1  │ Write (Financial DB) │ Add expense, set      │
│         │ (2-Step Confirmed)   │ budget limits         │
├─────────┼──────────────────────┼───────────────────────┤
│ Tier 2  │ Regulated & Large    │ Tuition remittances,  │
│         │ (AML + Sanctions)    │ AML screening > $10k  │
└─────────┴──────────────────────┴───────────────────────┘
```

1. **Deterministic Execution**: The LLM *never* performs arithmetic or database modifications directly. It issues structured `function_call` tokens that are intercepted by the Python supervisor.
2. **Two-Step Confirmation Gate**: Write operations (`add_expense`, `set_budget_category`, `schedule_tuition_payment`) return `confirmation_required: True`. The action is suspended in memory until the student clicks **Confirm** in the Streamlit UI.
3. **Zero-Knowledge PII Protection**: All 8+ digit bank card numbers and passport patterns are automatically masked with `****` before persisting to `logs/execution_log.jsonl`.
4. **FATF & PBOC/SAFE Compliance**: Automatic detection of single transactions exceeding $10,000 USD and hard blocks for international sanctions destinations.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.14+
- Gemini API key → [Google AI Studio](https://aistudio.google.com)

### 1. Installation
```bash
# Clone or navigate to the repository
cd "Project China"

# Install dependencies (Streamlit, Google GenAI, Plotly, ReportLab, etc.)
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

### 2. Launch the Application
```bash
streamlit run app.py
```
*The application opens automatically at `http://localhost:8501`.*

### 3. Run Automated Verification Tests
```bash
python -m pytest tests/ -v
```
*Expected: 135 passed across 12 test suites in ~17 seconds.*

### 4. Generate Audit Execution Evidence (Deliverable 06)
```bash
python scripts/generate_execution_evidence.py
```
*Executes all 11 tool scenarios and populates `logs/execution_log.jsonl`.*

---

## 🎭 Pre-Seeded Student Profiles

| Student ID | Name | Country | Host | Balance (CNY) | Home Reserve | Credit | Tuition Due |
|---|---|---|---|---|---|---|---|
| **STU001** | Rafi Ahmed | 🇧🇩 Bangladesh | 🇨🇳 China | ¥ 3,500 | 50,000 BDT | 680 (Good) | ¥ 8,000 (Nov 1, 2026) |
| **STU002** | Ayesha Khan | 🇵🇰 Pakistan | 🇨🇳 China | ¥ 2,100 | 120,000 PKR | 620 (Fair) | ¥ 12,000 (Nov 15, 2026) |
| **STU003** | Emeka Okafor | 🇳🇬 Nigeria | 🇨🇳 China | ¥ 5,000 | 800,000 NGN | 590 (Fair) | ¥ 15,000 (Dec 1, 2026) |

---

## 📋 Competition Deliverables Matrix

| Deliverable ID | Requirement | Project File / Location | Status |
|---|---|---|---|
| **Deliverable 01** | Technical Documentation | [`docs/technical-documentation.md`](docs/technical-documentation.md) | ✅ Complete |
| **Deliverable 02** | Presentation Deck / Outline | [`presentation/slides-outline.md`](presentation/slides-outline.md) | ✅ Complete |
| **Deliverable 03** | Demo Video Script & Walkthrough | `streamlit run app.py` (Ready to record) | ✅ Ready |
| **Deliverable 04** | Complete Source Code | Full repository | ✅ Complete |
| **Deliverable 05** | Security Self-Assessment (30% weight) | [`docs/security-assessment.md`](docs/security-assessment.md) | ✅ Complete |
| **Deliverable 06** | Execution Evidence & Audit Log | [`logs/execution_log.jsonl`](logs/execution_log.jsonl) + [`docs/execution-evidence-summary.md`](docs/execution-evidence-summary.md) | ✅ Complete |

---

## 📄 License & Attribution

Developed for the **WeBank International AI Finance Challenge (October 2026)**.  
Released under the MIT License.
