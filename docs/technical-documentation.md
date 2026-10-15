# CrossPay Technical Documentation

**Project:** CrossPay — AI Financial Assistant for International Students  
**Competition:** WeBank International AI Finance Challenge — Topic C  
**Version:** 1.0.0  

---

## 1. System Overview

CrossPay is a Streamlit-based AI financial assistant powered by Google Gemini 3.8 Flash. It helps international students studying in China manage cross-border finances through natural language conversation.

The system enforces a strict **no-LLM-arithmetic** principle: all monetary calculations, FX rates, fee comparisons, and compliance checks are routed through deterministic Python tool functions. The LLM acts as a natural language interface and orchestrator, never as a calculator.

## 2. Architecture

See `docs/architecture.md` for the full architecture diagram.

**Layers:**
1. **Presentation** (`app.py`, `src/ui_components.py`) — Streamlit frontend with chat interface, sidebar stats, quick action buttons, and a confirmation banner for write actions
2. **Agent** (`src/agent.py`) — Stateful `CrossPayAgent` class wrapping Gemini 3.8 Flash with multi-turn context via `previous_interaction_id`
3. **Tool Registry** (`src/tool_registry.py`) — Gemini function-calling declarations and the `dispatch_tool()` router
4. **Tools** (`src/tools/`) — Five deterministic modules: `fx`, `remittance`, `budget`, `credit`, `compliance`
5. **Audit Logger** (`src/logger.py`) — Appends PII-masked JSON lines to `logs/execution_log.jsonl` after every tool call
6. **Data** (`src/db.py`, `src/mock_data.py`) — SQLite with three seeded mock student accounts

## 3. Agent Algorithm

```
User Message
     │
     ▼
CrossPayAgent.chat(message)
     │
     ├─ Build create_kwargs (model, input, system_instruction, tools, previous_interaction_id)
     │
     ▼
gemini-3.8-flash interaction
     │
     ▼
Iterate interaction.steps
     │
     ├─ step.type == "function_call"?
     │       │
     │       ├─ dispatch_tool(step.name, step.arguments)
     │       │       └─ calls deterministic Python function
     │       │       └─ logs to execution_log.jsonl (PII masked)
     │       │
     │       ├─ result.confirmation_required == True?
     │       │       └─ YES: store as pending_action, return preview string
     │       │              (STOP — do not continue loop)
     │       │
     │       └─ NO: continue iterating steps
     │
     └─ Return interaction.output_text

Confirm button pressed:
     CrossPayAgent.confirm_action()
          └─ dispatch_tool(commit_variant, args)
          └─ clear pending_action
          └─ return success message
```

## 4. Tool Reference

| Tool | Module | Tier | Returns |
|------|--------|------|--------|
| `get_exchange_rate` | `fx.py` | 0 | `{rate, provider, timestamp, fee_pct}` |
| `convert_amount` | `fx.py` | 0 | `{original, converted, rate, fee_usd}` |
| `compare_remittance_options` | `remittance.py` | 0 | `list[{provider, fee_usd, total_cost_usd, recommended}]` |
| `schedule_tuition_payment` | `remittance.py` | 2 | `{optimal_window, projected_rate, confirmation_required: True}` |
| `get_spending_summary` | `budget.py` | 0 | `{categories, total_cny, vs_budget_pct}` |
| `add_expense` | `budget.py` | 1 | `{recorded: False, new_balance_cny, confirmation_required: True}` |
| `get_credit_profile` | `credit.py` | 0 | `{score, tier, tips, next_milestone}` |
| `simulate_credit_action` | `credit.py` | 0 | `{projected_score_change, new_score, timeline_months}` |
| `check_aml_threshold` | `compliance.py` | 2 | `{flagged, threshold_usd, reason}` |
| `check_sanctioned_destination` | `compliance.py` | 2 | `{blocked, country, reason}` |

## 5. Data Schema

### Table: `accounts`
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Student ID (STU001–STU003) |
| name | TEXT | Display name |
| home_currency | TEXT | ISO 4217 home currency |
| balance_cny | REAL | Current CNY balance |
| tuition_due_date | TEXT | ISO date |
| credit_score | INTEGER | 300–850 |
| passport_number | TEXT | Pre-masked (e.g. BD****1234) |
| bank_account | TEXT | Pre-masked (e.g. ****4321) |

### Table: `expenses`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| student_id | TEXT FK | References accounts.id |
| amount_cny | REAL | Expense amount |
| category | TEXT | food/transport/books/utilities/entertainment/other |
| timestamp | TEXT | ISO 8601 UTC |

## 6. Setup & Deployment

### Prerequisites
- Python 3.14+
- Gemini API key (get from [Google AI Studio](https://aistudio.google.com))

### Installation
```bash
cd "e:\Project China"
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### Testing
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## 7. Key Design Decisions

1. **Deterministic tools over LLM arithmetic** — Financial calculations are too critical to trust to probabilistic text generation. Every number the user sees came from a Python function, not the LLM.
2. **Stateful context via `previous_interaction_id`** — Gemini's server-side context management avoids re-sending full conversation history on each turn, reducing latency and cost.
3. **2-step confirmation at the Python layer** — The confirmation gate lives in Python, not in the LLM prompt, making it robust against prompt injection.
4. **SQLite with pre-masked PII** — No financial PII ever stored in plaintext. Mock data seeded with masked values from the start.
