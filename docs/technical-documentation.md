# CrossPay Technical Documentation

**Project:** CrossPay (微众智汇) — AI Financial Assistant for International Students  
**Competition:** WeBank International AI Finance Challenge — Topic C  
**Version:** 2.0.0 (Competition Build)  

---

## 1. System Overview

CrossPay is an enterprise-grade AI financial assistant powered by **Google Gemini 3.8 Flash** and deployed on **Streamlit**. Designed specifically for international students studying in China, CrossPay bridges foreign currencies (BDT, PKR, NGN) to CNY with full Chinese regulatory compliance (PBOC/SAFE), bank-grade safeguards, multi-dimensional Plotly analytics, proactive financial alerts, and a proprietary **Financial Health Score™**.

The system strictly enforces a **no-LLM-arithmetic** architecture: all monetary conversions, exchange rate lookups, budget aggregations, and compliance evaluations run via deterministic Python functions. The LLM serves exclusively as an empathetic, bilingual conversational interface and agentic orchestrator.

---

## 2. Architecture & Modular Layers

CrossPay is architected as a clean, decoupled 6-tier system:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION & VISUALIZATION LAYER                   │
│  app.py (Executive Portal) · pages/ (Multi-Page Navigation)            │
│  • 1_📊_Dashboard.py    • 2_🤖_AI_Assistant.py                         │
│  • 3_📈_Analytics.py    • 4_⚙️_Settings.py                             │
│  • src/theme.py (CSS)   • src/charts.py (Plotly) • src/i18n.py (EN/ZH) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       AGENTIC ORCHESTRATION LAYER                      │
│  src/agent.py (CrossPayAgent)                                          │
│  • Gemini 3.8 Flash function-calling runtime                           │
│  • Stateful conversation persistence (previous_interaction_id)         │
│  • 2-Step Confirmation Gate (intercepts write/regulated actions)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    TOOL REGISTRY & ROUTING LAYER                       │
│  src/tool_registry.py                                                  │
│  • 13 Gemini Function Declarations (JSON Schema)                       │
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

## 4. Complete Tool Specification (13 Tools)

| Tool Name | Module | Tier | Description & Return Schema |
|---|---|---|---|
| `get_exchange_rate` | `fx.py` | 0 | Returns `{rate, from_currency, to_currency, provider, timestamp, fee_pct}` |
| `convert_amount` | `fx.py` | 0 | Deterministic conversion: `{original, converted, rate, fee_usd, provider}` |
| `compare_remittance_options` | `remittance.py` | 0 | Returns 4 providers sorted by total cost (WeBank Direct, Wise, UnionPay, SWIFT) |
| `schedule_tuition_payment` | `remittance.py` | 2 | Analyzes FX cycles; returns `{optimal_window, projected_rate, confirmation_required: True}` |
| `get_spending_summary` | `budget.py` | 0 | Summarizes monthly category spending and budget utilization percentage |
| `add_expense` | `budget.py` | 1 | Previews an expense addition; returns `{new_balance_cny, confirmation_required: True}` |
| `get_credit_profile` | `credit.py` | 0 | Returns score, tier, 5 actionable student credit tips, and next score milestone |
| `simulate_credit_action` | `credit.py` | 0 | Simulates credit score changes (e.g., +25 points for secured credit card) |
| `check_aml_threshold` | `compliance.py` | 2 | Checks transactions against $10,000 USD limit for PBOC/SAFE compliance |
| `check_sanctioned_destination` | `compliance.py` | 2 | Evaluates country code against 10 international sanctioned destinations |
| `get_fx_trend` | `analytics.py` | 0 | Retrieves 30-day daily historical FX rates against CNY for charting |
| `get_spending_trend` | `analytics.py` | 0 | Aggregates 6-month historical spending grouped by category |
| `get_credit_trend` | `analytics.py` | 0 | Returns 6-month historical credit score trajectory data |

---

## 5. Security & Permission Tiering

1. **Tier 0 (Read-Only)**: Read tools execute immediately without side effects.
2. **Tier 1 (Write - Confirmed)**: Operations modifying the database return `confirmation_required: True`. The Python runtime freezes execution, saves the call as `pending_action`, and prompts the user with Confirm/Cancel UI buttons. No prompt-injected LLM text can bypass this gate.
3. **Tier 2 (Regulated)**: Large transfers require both 2-step user confirmation and mandatory automated AML / sanctions checks.
4. **PII Masking**: RegEx patterns in `src/logger.py` mask 8+ digit bank accounts and passport numbers with `****` before persisting to `logs/execution_log.jsonl`.

---

## 6. Testing & Quality Assurance

- Total automated tests: **57**
- Test command: `python -m pytest tests/ -v`
- Pass rate: **100% (57/57)**
- Test modules:
  - `test_agent.py`: Multi-turn stateful memory, tool calling, 2-step confirmation handling
  - `test_tools.py`: Deterministic mathematics, FX conversions, remittance ordering, AML flags
  - `test_logger.py`: Audit logging, JSONL schema, PII redaction
  - `test_db.py`: SQLite creation, constraint verification, mock seeding
  - `test_analytics.py`: Financial Health Score calculation, alerts engine, analytics querying, ReportLab PDF generation
