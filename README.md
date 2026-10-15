# 🏦 CrossPay — AI Financial Assistant for International Students

[![WeBank International Track](https://img.shields.io/badge/WeBank-International%20Track-blue)]
[![Topic C](https://img.shields.io/badge/Topic-C%3A%20Cross--border%20Finance-green)]
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue)]
[![Gemini 3.8 Flash](https://img.shields.io/badge/Gemini-3.8%20Flash-orange)]

CrossPay is an AI-powered financial assistant that helps international students studying in China manage cross-border finances through natural language conversation — powered by **Google Gemini 3.8 Flash** with deterministic financial tool functions.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💱 FX Rate Lookup | Real-time mock exchange rates: BDT, PKR, NGN ↔ CNY/USD |
| 🏦 Remittance Comparison | Compare SWIFT, WeBank, Wise, UnionPay by total cost |
| 📅 Tuition Optimization | Find optimal FX window to schedule tuition payments |
| 📊 Budget Tracking | Multi-category expense tracking in CNY |
| 💳 Credit Building | Score profile + actionable tips for newcomers |
| 🛡️ Compliance | AML threshold check + 10-country sanctions screen + PII masking |

## 🔐 Security Model

```
Tier 0 (Read)      → FX rates, profiles, comparisons — no confirmation needed
Tier 1 (Write)     → Expense recording, budget limits — 2-step confirm required  
Tier 2 (Regulated) → Transfers, AML/sanctions checks — 2-step + compliance check
```

**Key principle:** The LLM *never* calculates money. All financial computations go through deterministic Python tool functions.

## 🗂️ Project Structure

```
Project China/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── .env.example
├── src/
│   ├── agent.py              # CrossPayAgent (Gemini 3.8 Flash)
│   ├── db.py                 # SQLite schema + connection
│   ├── mock_data.py          # 3 seeded student accounts
│   ├── logger.py             # Audit logger → logs/execution_log.jsonl
│   ├── tool_registry.py      # Gemini function declarations + dispatcher
│   ├── ui_components.py      # Streamlit components
│   └── tools/
│       ├── fx.py             # Exchange rates + conversion
│       ├── remittance.py     # Provider comparison + tuition scheduling
│       ├── budget.py         # Expense tracking
│       ├── credit.py         # Credit score profile + simulator
│       └── compliance.py     # AML, sanctions, PII masking
├── tests/                    # 50 pytest tests (85%+ coverage)
├── docs/
│   ├── security-assessment.md       # Deliverable 05
│   ├── technical-documentation.md   # Deliverable 01
│   ├── execution-evidence-summary.md # Deliverable 06
│   └── architecture.md
├── scripts/
│   └── generate_execution_evidence.py
└── presentation/
    └── slides-outline.md            # Deliverable 02 outline
```

## 🚀 Setup

### Prerequisites
- Python 3.14+
- Gemini API key → [Get one free at Google AI Studio](https://aistudio.google.com)

### Installation

```bash
# 1. Clone / navigate to project
cd "Project China"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env and set: GEMINI_API_KEY=your_key_here
# Optionally set: STUDENT_ID=STU001  (or STU002, STU003)
```

### Run the App

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### Run Tests

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Generate Execution Evidence (Deliverable 06)

```bash
python scripts/generate_execution_evidence.py
# No API key needed — calls tool functions directly
# Output: logs/execution_log.jsonl
```

## 🎭 Demo Accounts

| ID | Name | From | Balance | Tuition Due | Credit Score |
|----|------|------|---------|-------------|-------------|
| STU001 | Rafi Ahmed | 🇧🇩 Bangladesh | 3,500 CNY | Nov 1, 2026 | 680 (Good) |
| STU002 | Ayesha Khan | 🇵🇰 Pakistan | 2,100 CNY | Nov 15, 2026 | 620 (Fair) |
| STU003 | Emeka Okafor | 🇳🇬 Nigeria | 5,000 CNY | Dec 1, 2026 | 590 (Fair) |

## 📋 Competition Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| 01 | Technical Documentation | `docs/technical-documentation.md` |
| 02 | Presentation Outline | `presentation/slides-outline.md` |
| 03 | Demo Video | Record `streamlit run app.py` |
| 04 | Source Code | This repository |
| 05 | Security Self-Assessment | `docs/security-assessment.md` |
| 06 | Execution Evidence | `logs/execution_log.jsonl` + `docs/execution-evidence-summary.md` |

## 🏗️ Architecture

```
User → Streamlit UI → CrossPayAgent → Gemini 3.8 Flash
                              ↓
                    Tool Call Loop (function_calling)
                              ↓
              dispatch_tool() → deterministic Python function
                              ↓              ↓
                    log (PII masked)    DB read/write
                              ↓
                 confirmation_required?
                    YES → Preview UI → User Confirm/Cancel
                    NO  → Return result to LLM
```

## 📄 License

MIT License — Competition submission for WeBank International AI Finance Challenge, October 2026.
