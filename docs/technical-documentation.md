# CrossPay Technical Documentation

**Project:** CrossPay (微众智汇) — AI Financial Assistant for International Students  
**Competition:** WeBank International AI Finance Challenge — Topic C  
**Version:** 2.1.0 (Market-Ready Autonomous & AI Studio Build)  

---

## 1. System Overview

CrossPay is an enterprise-grade AI financial assistant powered by a dual-engine architecture: a high-precision **Autonomous On-Device NLP Engine** (100% self-contained, zero external API keys needed, sub-5ms inference) alongside an optional **Google Gemini 3.8 Flash** cloud mode. Designed specifically for international students studying in China, CrossPay bridges foreign currencies (BDT, PKR, NGN) to CNY with full Chinese regulatory compliance (PBOC/SAFE), bank-grade safeguards, multi-dimensional Plotly analytics, proactive financial alerts, an interactive **AI Model Studio**, and a proprietary **Financial Health Score™**.

The system strictly enforces a **no-LLM-arithmetic** architecture: all monetary conversions, exchange rate lookups, budget aggregations, and compliance evaluations run via deterministic Python functions. The NLP engine serves exclusively as an intent classification, entity extraction, and conversational orchestration layer.

---

## 2. Architecture & Modular Layers

CrossPay is architected as a clean, decoupled 6-tier system:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION & VISUALIZATION LAYER                   │
│  app.py (Executive Portal) · pages/ (Multi-Page Navigation)            │
│  • 1_📊_Dashboard.py    • 2_🤖_AI_Assistant.py                         │
│  • 3_📈_Analytics.py    • 4_⚙️_Settings.py                             │
│  • 5_🌍_Global_Intelligence.py  • 6_🧪_AI_Model_Studio.py              │
│  • src/theme.py (CSS)   • src/charts.py (Plotly) • src/i18n.py (EN/ZH) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                  DUAL-ENGINE AGENTIC ORCHESTRATION LAYER               │
│  src/agent.py (CrossPayAgent) · src/autonomous_engine.py               │
│  • Engine A: Autonomous On-Device Model (100% Offline, Zero API Key)   │
│    - models/crosspay_production_model.joblib (20-class NLP model)      │
│    - 1,300 curated bilingual training samples (98.69% CV accuracy)     │
│    - Regex & entity parser (amounts, currencies, categories, dates)    │
│  • Engine B: Cloud Google Gemini 3.8 Flash (Multi-turn hybrid mode)    │
│  • 2-Step Confirmation Gate (intercepts write/regulated actions)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    TOOL REGISTRY & ROUTING LAYER                       │
│  src/tool_registry.py                                                  │
│  • 14 Gemini Function Declarations (JSON Schema)                       │
│  • dispatch_tool(name, args) dynamic router                            │
└───────────────────┬───────────────────────────────────┬────────────────┘
                    │                                   │
┌───────────────────▼───────────────┐   ┌───────────────▼────────────────┐
│      DETERMINISTIC TOOLS          │   │         AUDIT LOGGER           │
│  src/tools/                       │   │  src/logger.py                 │
│  • fx.py: rates & conversion      │   │  • logs/execution_log.jsonl    │
│  • remittance.py: cost comparison │   │  • mask_pii() redaction        │
│  • budget.py: expense tracking    │   │  • 100% immutable audit trail  │
│  • credit.py: scoring & simulation│   └────────────────────────────────┘
│  • compliance.py: AML & sanctions │
│  • analytics.py: FX/spend/credit  │
└───────────────────┬───────────────┘
                    │
┌───────────────────▼────────────────────────────────────────────────────┐
│                INTELLIGENCE & PROPRIETARY ENGINES                      │
│  • src/health_score.py: CrossPay Financial Health Score™ (0-100)       │
│  • src/alerts.py: Proactive smart risk and opportunity generator       │
│  • src/pdf_report.py: High-resolution ReportLab PDF financial report   │
│  • data/worldbank_remittance.csv: Official World Bank 2000-2024 flows  │
└───────────────────┬────────────────────────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER (SQLITE)                           │
│  src/db.py & src/mock_data.py                                          │
│  • accounts · expenses · budgets · fx_history · alerts · credit_history│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Proprietary Metric: CrossPay Financial Health Score™

The **CrossPay Financial Health Score™** is a normalized 0–100 multi-factor composite risk index designed specifically for international students:

$$\text{Health Score} = \text{Credit}\times 0.30 + \text{Discipline}\times 0.25 + \text{Reserve}\times 0.25 + \text{Tuition}\times 0.20$$

1. **Credit History (30%)**: Normalized from Chinese/host credit score [300, 850].
2. **Spending Discipline (25%)**: Ratio of current month expenses to the living budget limit ($3,000 \text{ CNY}$ default baseline). Penalizes uncontrolled discretionary spending.
3. **Emergency Reserve (25%)**: Liquidity runway measuring available CNY cash against the monthly burn rate.
4. **Tuition Readiness (20%)**: Total global liquidity (Host CNY + Home currency balance converted to CNY) divided by the upcoming semester tuition obligation.

### Health Score Bands
- **91 – 100**: *Excellent (极佳)* — Unrestricted financial freedom and optimal runway.
- **76 – 90**: *Healthy (健康)* — Robust balances and disciplined spending.
- **61 – 75**: *Stable (稳定)* — Balanced but requires attention to upcoming tuition.
- **41 – 60**: *At Risk (有风险)* — Liquidity deficit or overspending trend.
- **0 – 40**: *Critical (危险)* — Imminent tuition payment default or negative balance.

---

## 4. Complete Tool Specification (24 Deterministic Tools)

| Tool Name | Module | Tier | Description & Return Schema |
|---|---|---|---|
| `get_exchange_rate` | `fx.py` | 0 | Returns `{rate, from_currency, to_currency, provider, timestamp, fee_pct}` |
| `convert_amount` | `fx.py` | 0 | Deterministic conversion: `{original, converted, rate, fee_usd, provider}` |
| `get_pboc_central_parity_rate` | `fx.py` | 0 | PBOC central parity rate (中间价) with ±2% band & buy/sell cash rates |
| `get_fx_volatility_metrics` | `fx.py` | 0 | 30-day Bollinger bands, z-scores, and OPTIMAL_BUY recommendations |
| `compare_remittance_options` | `remittance.py` | 0 | Returns 4 providers sorted by total cost (WeBank Direct, Wise, UnionPay, SWIFT) |
| `schedule_tuition_payment` | `remittance.py` | 2 | Analyzes FX cycles; returns `{optimal_window, projected_rate, confirmation_required: True}` |
| `get_spending_summary` | `budget.py` | 0 | Summarizes monthly category spending and budget utilization percentage |
| `add_expense` | `budget.py` | 1 | Previews an expense addition; returns `{new_balance_cny, confirmation_required: True}` |
| `get_credit_profile` | `credit.py` | 0 | Returns score, tier, 5 actionable student credit tips, and next score milestone |
| `simulate_credit_action` | `credit.py` | 0 | Simulates credit score changes (e.g., +25 points for secured credit card) |
| `check_aml_threshold` | `compliance.py` | 2 | Checks transactions against $10,000 USD limit for PBOC/SAFE compliance |
| `check_aml_structuring` | `compliance.py` | 2 | Detects micro-transactions avoiding the $10,000 USD AML threshold |
| `check_sanctioned_destination` | `compliance.py` | 2 | Evaluates country code against 10 international sanctioned destinations |
| `check_safe_quota` | `compliance.py` | 2 | Evaluates SAFE $50k USD quota & Circular [2020] No.17 tuition exemptions |
| `verify_student_tuition_eligibility`| `compliance.py` | 0 | Verifies student X1/X2 visa and tuition invoice for quota exemption |
| `get_cips_clearing_window` | `compliance.py` | 0 | Returns PBOC CIPS interbank clearing window status (09:00–17:00 CST) |
| `get_fx_trend` | `analytics.py` | 0 | Retrieves 30-day daily historical FX rates against CNY for charting |
| `get_spending_trend` | `analytics.py` | 0 | Aggregates 6-month historical spending grouped by category |
| `get_credit_trend` | `analytics.py` | 0 | Returns 6-month historical credit score trajectory data |
| `get_worldbank_remittance` | `analytics.py` | 0 | Official World Bank remittance volumes and 5-year CAGR across 221 nations |
| `detect_spending_anomalies` | `analytics.py` | 0 | Tukey's IQR statistical anomaly detector over student transaction history |
| `get_cohort_spending_benchmarks` | `analytics.py` | 0 | Aggregates cohort spending benchmarks from 5,000 empirical student records |
| `screen_tuition_proxy_scam` | `fraud.py` | 2 | Evaluates tuition discount proposals against stolen credit card chargeback schemes |
| `screen_peer_exchange_risk` | `fraud.py` | 2 | Evaluates P2P chat swaps under PBOC 'Card Break Action' (断卡行动) |
| `evaluate_transaction_fraud_risk` | `fraud.py` | 2 | Computes 0–100 multi-factor transaction risk index (velocity, off-hours, channel) |
| `check_telecom_fraud_keywords` | `fraud.py` | 2 | Scans text for PRC Anti-Telecom Fraud keywords (safe accounts, police impersonation) |

---

## 5. Autonomous On-Device NLP Engine & AI Model Studio

### 5.1 Architecture & Pipeline
To eliminate third-party cloud dependencies and guarantee 100% offline uptime, CrossPay features a dedicated, locally trained Natural Language Processing engine:
- **Vectorization**: Sublinear TF-IDF character n-grams `(char_wb, n=(2, 5))`, enabling robust simultaneous processing of English phonetics, abbreviations, and Chinese character combinations without heavy external tokenizers.
- **Classification**: Calibrated Multiclass Logistic Regression (`C=15.0`, balanced class weights) classifying user intents across **20 fine-grained categories**.
- **Confidence Calibration**: Implements Platt probability scaling via Softmax. Queries falling below 25% confidence or triggering non-financial keywords are routed to an out-of-domain safe rejection state.
- **Latency**: Benchmarked at an average of **3.48 ms per query** on standard consumer hardware, providing instantaneous response times.

### 5.2 Training Dataset & Metrics
- **Dataset Size**: 1,300 curated bilingual (English & Mandarin Chinese) intent samples.
- **Validation**: 5-Fold Stratified Cross-Validation score: **98.69% (±0.83%)**.
- **Model Artifacts**:
  - Pipeline Model: `models/crosspay_production_model.joblib`
  - Classifier Backup: `models/crosspay_intent_classifier.joblib`
  - Class-level Classification Report: `models/class_report.json`
  - Global Performance Metrics: `models/production_metrics.json`

### 5.3 AI Model Studio (`pages/6_🧪_AI_Model_Studio.py`)
CrossPay embeds an interactive model evaluation and operations suite directly into the application:
1. **Live Inference Inspector**: Test arbitrary text queries, inspect top predicted intent, real-time confidence gauge, inference latency in milliseconds, extracted regex entities, and rendered assistant output.
2. **Model Performance & Benchmarks**: Full 20-class breakdown of Precision, Recall, F1-Score, sample support, and cross-validation metrics.
3. **Training Dataset Explorer**: Searchable, filterable table of all 1,300 training samples with intent distribution charts.
4. **Model Training Operations**: Live one-click retraining button executing `scripts/train_production_model.py` with immediate session state reload.

---

## 6. Security & Permission Tiering

1. **Tier 0 (Read-Only)**: Read tools execute immediately without side effects.
2. **Tier 1 (Write - Confirmed)**: Operations modifying the database return `confirmation_required: True`. The Python runtime freezes execution, saves the call as `pending_action`, and prompts the user with Confirm/Cancel UI buttons. No prompt-injected LLM text can bypass this gate.
3. **Tier 2 (Regulated)**: Large transfers require both 2-step user confirmation and mandatory automated AML / sanctions checks.
4. **PII Masking**: RegEx patterns in `src/logger.py` mask 8+ digit bank accounts and passport numbers with `****` before persisting to `logs/execution_log.jsonl`.
5. **Prompt Injection Resilience**: The autonomous local parser deterministically extracts tool calls based on intent classification and entity regex, preventing jailbreak sequences like `"ignore previous instructions"` from altering system behavior.

---

## 7. Testing & Quality Assurance

- **Total Automated Tests**: **144**
- **Test Command**: `python -m pytest tests/ -v`
- **Pass Rate**: **100% (144/144)**
- **Test Coverage Across 13 Specialized Suites**:
  - `test_agent.py` (10 tests): Multi-turn stateful memory, tool calling, 2-step confirmation handling, API fallback
  - `test_tools.py` (35 tests): Deterministic mathematics, FX conversions with zero-fee same-currency logic, expanded international student currencies, remittance ordering, single & multi-day AML structuring flags, negative amount exploit guards, PII masking, tuition commitment alerts, and PyCountry sanctions screening
  - `test_fraud_detection.py` (20 tests): Tuition proxy discount scam detection, underground P2P chat swap screening under PBOC "Card Break Action", composite multi-factor fraud risk evaluation, and PRC telecom fraud keyword screening
  - `test_audit_fixes.py` (9 tests): Currency-aware SAFE quota conversions (CNY/BDT to USD), defensive PBOC unsupported currency error handling, negative tuition commit guards, empty chart input resilience, CSS aliases, and CJK PDF font registration
  - `test_fx_accuracy.py` (4 tests): Live interbank rate fetching, PBOC official central parity rates (中间价), statutory +/-2% floating bands, commercial bank bid/ask spreads, and 30-day Bollinger band volatility models
  - `test_compliance_accuracy.py` (5 tests): China SAFE $50k USD annual facilitation quota tracking, university tuition genuine non-quota exemption (Circular [2020] No.17), student eligibility verification (X1/X2 visa), and PBOC CIPS clearing window monitoring
  - `test_data_accuracy.py` (3 tests): 5,000 empirical transaction processing, Tukey's IQR outlier and anomaly detection, and destination country peer spend benchmarks
  - `test_nlp_accuracy.py` (7 tests): Advanced multilingual entity extraction (Chinese shorthand `5万`, `3千`, `10k`, relative dates `下周一`), high-precision intent classification, and autonomous chat generation
  - `test_logger.py` (13 tests): Audit logging, JSONL schema, PII redaction, tool dispatching
  - `test_db.py` (4 tests): SQLite creation, constraint verification, mock seeding, and strict foreign key integrity (`PRAGMA foreign_keys = ON`)
  - `test_analytics.py` (11 tests): Financial Health Score calculation, alerts engine, analytics querying, World Bank dataset integration, ReportLab PDF generation
  - `test_autonomous_engine.py` (16 tests): 100% offline autonomous inference, intent prediction, entity extraction, bilingual EN/ZH response generation, tuition confirmation workflows, dynamic World Bank country detection, and sanctions verification
  - `test_production_robustness.py` (7 tests): Adversarial prompt injection resistance, out-of-domain rejection, boundary AML stress testing, complete 10-country sanctions matrix, sub-15ms inference latency SLA, unicode fuzzing, and multi-turn state integrity
