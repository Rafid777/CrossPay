# WeBank Topic C – CrossPay Student Finance Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a competition-ready AI-powered Cross-border & Student Finance Assistant named "CrossPay" that helps international students manage FX, tuition payments, living expenses, and credit building — powered by Gemini 3.8 Flash with deterministic financial tool calls.

**Architecture:** Streamlit single-page app wrapping a stateful Gemini agent that routes all financial calculations to deterministic Python tool functions (never free-form LLM math). The agent uses Gemini function-calling to invoke tools, and all tool executions are logged with full audit trails for Deliverable 06 (Execution Evidence). A security layer enforces permission tiers (read-only vs. user-confirmed actions) and PII masking before any data is shown or stored.

**Tech Stack:** Python 3.14, Streamlit, google-genai >= 2.30.1, SQLite (mock accounts), python-dotenv, pytest, rich (CLI logging), pycountry, forex-python (fallback to mock rates if unavailable)

**Spec:** docs/spec/topic-c-spec.md (written inline with this plan — the competition PDF is the authoritative source)

## Global Constraints

- Language: Python 3.14 only; no TypeScript, no Node
- Gemini model: `gemini-3.8-flash` exclusively — never legacy models
- All monetary calculations routed through deterministic Python functions — LLM never does arithmetic
- Financial data never stored in plaintext — account numbers, passport numbers, IBAN masked with `****` before storage or display
- Transfer actions require explicit user confirmation step (2-step: preview → confirm)
- AML flag threshold: single transfer > $10,000 USD equivalent triggers hold + compliance note
- Sanctioned destination list checked on every transfer (mock list of 10 countries)
- All tool invocations logged to `logs/execution_log.jsonl` with timestamp, tool name, inputs (PII-masked), output summary
- Streamlit runs on port 8501
- SQLite database at `data/crosspay.db` with mock student accounts
- Tests use pytest, located in `tests/`, minimum 80% line coverage on `src/tools/`
- No real API calls to banking services — all remittance/FX data is realistically mocked
- README must include: project description, setup steps, how to run, how to run tests, architecture diagram (ASCII)
- Submission deadline: October 20, 2026, 23:59 Beijing Time (UTC+8)

## Review Focus

1. LLM arithmetic bypass: if any code path lets the LLM return a dollar amount without going through a tool function, it's a critical defect
2. PII leak: account/passport numbers appearing unmasked in logs, UI, or DB
3. Missing 2-step confirmation: any write action (transfer, budget update) that executes without a preview + confirm cycle
4. AML threshold miss: transfers above $10,000 that don't trigger the compliance flag
5. Missing audit log entries: any tool call not written to `logs/execution_log.jsonl`

---

### Task 1: Project Scaffolding, Mock Data & Database

**Files:**
- Create: `src/__init__.py`
- Create: `src/db.py`
- Create: `src/mock_data.py`
- Create: `data/.gitkeep`
- Create: `logs/.gitkeep`
- Create: `tests/__init__.py`
- Create: `tests/test_db.py`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`

**Interfaces:**
- Produces: `get_db() -> sqlite3.Connection` (from `src/db.py`)
- Produces: `seed_mock_data(conn: sqlite3.Connection) -> None` (from `src/mock_data.py`)
- Produces: 3 mock student accounts seeded in DB on first run

**Mock account schema (SQLite table `accounts`):**
```
id TEXT PRIMARY KEY,          -- "STU001", "STU002", "STU003"
name TEXT,                    -- display name
email TEXT,
home_currency TEXT,           -- "BDT", "PKR", "NGN"
home_country TEXT,
host_country TEXT,            -- "CN" (China)
host_currency TEXT,           -- "CNY"
balance_home REAL,            -- balance in home currency
balance_cny REAL,             -- balance in CNY
tuition_due_date TEXT,        -- ISO date
tuition_amount_cny REAL,
credit_score INTEGER,         -- 300-850
passport_number TEXT,         -- will be masked
bank_account TEXT             -- will be masked
```

- [ ] **Step 1: Write failing test for DB creation and seeding**

```python
# tests/test_db.py
def test_db_creates_accounts_table():
    conn = get_db(":memory:")
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
    assert cur.fetchone() is not None

def test_mock_data_seeds_three_accounts():
    conn = get_db(":memory:")
    seed_mock_data(conn)
    count = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    assert count == 3

def test_passport_never_stored_plaintext():
    conn = get_db(":memory:")
    seed_mock_data(conn)
    rows = conn.execute("SELECT passport_number FROM accounts").fetchall()
    for row in rows:
        assert "****" in row[0], f"Passport not masked: {row[0]}"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_db.py -v
```
Expected: 3 FAILED (ImportError / table not found)

- [ ] **Step 3: Implement `src/db.py`**

`get_db(path: str = "data/crosspay.db") -> sqlite3.Connection`
Creates DB file if missing, runs `CREATE TABLE IF NOT EXISTS accounts (...)` with all columns above, returns connection with `row_factory = sqlite3.Row`.

- [ ] **Step 4: Implement `src/mock_data.py`**

`seed_mock_data(conn: sqlite3.Connection) -> None`
Uses `INSERT OR IGNORE` so re-runs are idempotent. Three accounts:
- STU001: Bangladeshi student, 50000 BDT, 3500 CNY, tuition 8000 CNY due 2026-11-01
- STU002: Pakistani student, 120000 PKR, 2100 CNY, tuition 12000 CNY due 2026-11-15
- STU003: Nigerian student, 800000 NGN, 5000 CNY, tuition 15000 CNY due 2026-12-01

Passport numbers stored as `"BD****1234"`, `"PK****5678"`, `"NG****9012"`. Bank accounts stored as `"****4321"`, `"****8765"`, `"****2109"`.

- [ ] **Step 5: Write `requirements.txt`**

```
streamlit>=1.40.0
google-genai>=2.30.1
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-cov>=5.0.0
rich>=13.0.0
pycountry>=24.6.1
```

- [ ] **Step 6: Write `.env.example`**

```
GEMINI_API_KEY=your_gemini_api_key_here
STUDENT_ID=STU001
```

- [ ] **Step 7: Write `.gitignore`**

Include: `.env`, `data/crosspay.db`, `logs/*.jsonl`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, `.venv/`

- [ ] **Step 8: Run tests to verify they pass**

```
pytest tests/test_db.py -v
```
Expected: 3 PASSED

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: project scaffold, mock DB, seeded accounts"
```

---

### Task 2: Financial Tools (Deterministic Core)

**Files:**
- Create: `src/tools/__init__.py`
- Create: `src/tools/fx.py`
- Create: `src/tools/remittance.py`
- Create: `src/tools/budget.py`
- Create: `src/tools/credit.py`
- Create: `src/tools/compliance.py`
- Create: `tests/test_tools.py`

**Interfaces:**
- Consumes: nothing from Task 1 (pure functions)
- Produces (all imported in Task 3 as `from src.tools import fx, remittance, budget, credit, compliance`):

```python
# fx.py
def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    # returns {"rate": float, "provider": str, "timestamp": str, "fee_pct": float}

def convert_amount(amount: float, from_currency: str, to_currency: str) -> dict:
    # returns {"original": float, "converted": float, "rate": float, "fee_usd": float}

# remittance.py
def compare_remittance_options(amount_usd: float, destination_country: str) -> list[dict]:
    # returns list of {"provider": str, "fee_usd": float, "fx_rate": float,
    #                   "total_cost_usd": float, "delivery_days": int, "recommended": bool}

def schedule_tuition_payment(student_id: str, amount_cny: float, due_date: str) -> dict:
    # returns {"scheduled": bool, "optimal_window": str, "projected_rate": float,
    #          "estimated_savings_usd": float, "confirmation_required": True}

# budget.py
def get_spending_summary(student_id: str, month: str) -> dict:
    # returns {"categories": dict[str, float], "total_cny": float, "vs_budget_pct": float}

def set_budget_category(student_id: str, category: str, amount_cny: float) -> dict:
    # returns {"category": str, "new_limit_cny": float, "confirmation_required": True}

def add_expense(student_id: str, amount_cny: float, category: str, note: str) -> dict:
    # returns {"recorded": bool, "new_balance_cny": float, "confirmation_required": True}

# credit.py
def get_credit_profile(student_id: str) -> dict:
    # returns {"score": int, "tier": str, "tips": list[str], "next_milestone": int}

def simulate_credit_action(action: str, student_id: str) -> dict:
    # returns {"action": str, "projected_score_change": int, "new_score": int,
    #          "timeline_months": int}

# compliance.py
def check_aml_threshold(amount_usd: float) -> dict:
    # returns {"flagged": bool, "threshold_usd": 10000, "reason": str | None}

def check_sanctioned_destination(country_code: str) -> dict:
    # returns {"blocked": bool, "country": str, "reason": str | None}

def mask_pii(text: str) -> str:
    # masks patterns: account numbers (8+ digits), passport patterns
    # returns masked string
```

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tools.py
def test_get_exchange_rate_returns_valid_dict():
    result = get_exchange_rate("BDT", "CNY")
    assert "rate" in result and result["rate"] > 0
    assert "provider" in result

def test_convert_amount_math_is_correct():
    # if rate is 0.0650, 1000 BDT → 65 CNY
    result = convert_amount(1000.0, "BDT", "CNY")
    assert result["original"] == 1000.0
    assert result["converted"] > 0
    assert abs(result["converted"] - result["original"] * result["rate"]) < 0.01

def test_compare_remittance_returns_sorted_by_cost():
    options = compare_remittance_options(500.0, "CN")
    assert len(options) >= 3
    costs = [o["total_cost_usd"] for o in options]
    assert costs == sorted(costs)
    assert any(o["recommended"] for o in options)

def test_aml_flags_above_10000():
    result = check_aml_threshold(10001.0)
    assert result["flagged"] is True

def test_aml_passes_below_10000():
    result = check_aml_threshold(9999.99)
    assert result["flagged"] is False

def test_sanctioned_destination_blocks_known():
    # Iran is in mock sanctioned list
    result = check_sanctioned_destination("IR")
    assert result["blocked"] is True

def test_mask_pii_masks_account_numbers():
    masked = mask_pii("Account 12345678 transfer")
    assert "12345678" not in masked
    assert "****" in masked

def test_set_budget_requires_confirmation():
    result = set_budget_category("STU001", "food", 1000.0)
    assert result["confirmation_required"] is True

def test_schedule_payment_requires_confirmation():
    result = schedule_tuition_payment("STU001", 8000.0, "2026-11-01")
    assert result["confirmation_required"] is True

def test_credit_profile_has_tips():
    result = get_credit_profile("STU001")
    assert isinstance(result["tips"], list) and len(result["tips"]) >= 3
```

- [ ] **Step 2: Run tests to verify they fail**
```
pytest tests/test_tools.py -v
```
Expected: all FAILED (ImportError)

- [ ] **Step 3: Implement `src/tools/fx.py`**

Mock FX rates hardcoded dict: BDT/CNY=0.0650, PKR/CNY=0.0270, NGN/CNY=0.0048, USD/CNY=7.28, BDT/USD=0.00893, PKR/USD=0.00370, NGN/USD=0.000660. `get_exchange_rate` looks up rates, adds simulated 0.5% fee. `convert_amount` calls `get_exchange_rate`, applies fee.

- [ ] **Step 4: Implement `src/tools/remittance.py`**

`compare_remittance_options`: returns 4 hardcoded providers (SWIFT Bank Transfer, WeBank Direct, Wise, UnionPay Cross-border) with realistic fee structures. Sorted by `total_cost_usd` ascending. `recommended=True` on lowest cost. `schedule_tuition_payment`: returns optimal 3-day window (next Monday) with 0.3% projected rate improvement.

- [ ] **Step 5: Implement `src/tools/budget.py`**

`get_spending_summary`: reads from SQLite `expenses` table (created here with `CREATE TABLE IF NOT EXISTS`). `add_expense`: inserts row, updates `balance_cny` in accounts. `set_budget_category`: upserts `budgets` table. Both set `confirmation_required=True` in return dict — they do NOT commit to DB; commitment happens only after user confirms in the UI layer (Task 4).

- [ ] **Step 6: Implement `src/tools/credit.py`**

`get_credit_profile`: reads `credit_score` from accounts, computes tier (Poor<580, Fair 580-669, Good 670-739, VeryGood 740-799, Excellent 800+), returns 5 actionable tips for international students (get secured card, pay on time, keep utilization <30%, become authorized user, report rent payments). `simulate_credit_action`: returns projected changes for actions like "open_secured_card" (+25 pts), "pay_on_time_3mo" (+15 pts), "pay_tuition_early" (+8 pts).

- [ ] **Step 7: Implement `src/tools/compliance.py`**

`check_aml_threshold`: flags if `amount_usd > 10000`. `check_sanctioned_destination`: checks against hardcoded set `{"IR","KP","SY","CU","SD","MM","BY","VE","ZW","RU"}`. `mask_pii`: regex replaces 8+ digit sequences with `****`, replaces passport patterns `[A-Z]{2}\d{6,9}` with `XX****`.

- [ ] **Step 8: Run tests to verify they pass**
```
pytest tests/test_tools.py -v --cov=src/tools --cov-report=term-missing
```
Expected: all PASS, coverage ≥ 80%

- [ ] **Step 9: Commit**
```bash
git add src/tools/ tests/test_tools.py
git commit -m "feat: deterministic financial tools (FX, remittance, budget, credit, compliance)"
```

---

### Task 3: Audit Logger & Tool Registry

**Files:**
- Create: `src/logger.py`
- Create: `src/tool_registry.py`
- Create: `tests/test_logger.py`

**Interfaces:**
- Consumes: all tool functions from Task 2
- Produces: `log_tool_call(tool_name: str, inputs: dict, output: dict) -> None` (from `src/logger.py`)
- Produces: `TOOL_DECLARATIONS: list[dict]` — Gemini function-calling schemas (from `src/tool_registry.py`)
- Produces: `dispatch_tool(name: str, args: dict) -> dict` (from `src/tool_registry.py`) — routes tool name to function, logs result

**Gemini tool declarations format (7 tools to declare):**
```python
{
    "name": "get_exchange_rate",
    "description": "Get the current exchange rate between two currencies with fee information",
    "parameters": {
        "type": "object",
        "properties": {
            "from_currency": {"type": "string", "description": "ISO 4217 currency code"},
            "to_currency": {"type": "string", "description": "ISO 4217 currency code"}
        },
        "required": ["from_currency", "to_currency"]
    }
}
```
Declare all 9 tool functions from Task 2 using this format.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_logger.py
def test_log_creates_jsonl_file(tmp_path):
    log_tool_call("test_tool", {"key": "val"}, {"result": "ok"},
                  log_dir=str(tmp_path))
    files = list(tmp_path.glob("execution_log.jsonl"))
    assert len(files) == 1

def test_log_entry_has_required_fields(tmp_path):
    log_tool_call("get_exchange_rate", {"from_currency": "BDT", "to_currency": "CNY"},
                  {"rate": 0.065}, log_dir=str(tmp_path))
    import json
    with open(tmp_path / "execution_log.jsonl") as f:
        entry = json.loads(f.readline())
    assert "timestamp" in entry
    assert "tool_name" in entry
    assert "inputs" in entry
    assert "output_summary" in entry
    assert entry["tool_name"] == "get_exchange_rate"

def test_log_masks_pii_in_inputs(tmp_path):
    log_tool_call("add_expense", {"student_id": "STU001", "account": "12345678"},
                  {"recorded": True}, log_dir=str(tmp_path))
    import json
    with open(tmp_path / "execution_log.jsonl") as f:
        entry = json.loads(f.readline())
    assert "12345678" not in json.dumps(entry)

def test_dispatch_tool_routes_correctly():
    result = dispatch_tool("get_exchange_rate", {"from_currency": "USD", "to_currency": "CNY"})
    assert "rate" in result

def test_dispatch_tool_unknown_raises():
    with pytest.raises(ValueError, match="Unknown tool"):
        dispatch_tool("nonexistent_tool", {})
```

- [ ] **Step 2: Run to verify failure**
```
pytest tests/test_logger.py -v
```

- [ ] **Step 3: Implement `src/logger.py`**

`log_tool_call(tool_name: str, inputs: dict, output: dict, log_dir: str = "logs") -> None`
Creates `logs/` dir if missing. Appends JSON line to `logs/execution_log.jsonl`:
```json
{"timestamp": "ISO8601", "tool_name": "...", "inputs": {...pii_masked...}, "output_summary": "...truncated to 200 chars..."}
```
Calls `mask_pii` from `src/tools/compliance.py` on `json.dumps(inputs)` before storing.

- [ ] **Step 4: Implement `src/tool_registry.py`**

`TOOL_DECLARATIONS`: list of 9 Gemini function declarations for all tools from Task 2.
`dispatch_tool(name: str, args: dict) -> dict`: maps tool names to functions, injects `student_id` from `args` where needed, calls `log_tool_call` after each call, raises `ValueError(f"Unknown tool: {name}")` for unknowns.

- [ ] **Step 5: Run tests to pass**
```
pytest tests/test_logger.py -v
```

- [ ] **Step 6: Commit**
```bash
git add src/logger.py src/tool_registry.py tests/test_logger.py
git commit -m "feat: audit logger and Gemini tool registry"
```

---

### Task 4: Gemini Agent Core (Stateful Chat + Tool Loop)

**Files:**
- Create: `src/agent.py`
- Create: `tests/test_agent.py`

**Interfaces:**
- Consumes: `TOOL_DECLARATIONS`, `dispatch_tool` from `src/tool_registry.py` (Task 3)
- Consumes: `get_db`, `seed_mock_data` from Tasks 1-2
- Produces: `CrossPayAgent` class with:
  ```python
  class CrossPayAgent:
      def __init__(self, student_id: str, api_key: str)
      def chat(self, user_message: str) -> str
      # Returns final text response after resolving all tool calls
      # pending_action: dict | None  (set when a write action needs confirmation)
      def confirm_action(self) -> str
      # Executes the pending_action, clears it, returns confirmation message
      def cancel_action(self) -> str
      # Clears pending_action, returns cancellation message
  ```

**Agent system prompt (use verbatim):**
```
You are CrossPay, an AI financial assistant for international students studying in China.
You help students with: FX rate lookups, tuition payment optimization, cross-border remittance comparison, living expense tracking, and credit score building.

RULES YOU MUST FOLLOW:
1. NEVER calculate money amounts yourself. Always call the appropriate tool.
2. For any action that moves money or changes records (transfers, budget updates, expenses), always present a preview and wait for user confirmation before calling the tool.
3. When a tool returns confirmation_required=True, present the details and ask "Shall I proceed? (yes/no)"
4. Always mention the exchange rate source and timestamp when quoting FX rates.
5. If a transfer is flagged by AML (over $10,000), explain the hold and next steps.
6. If a destination is sanctioned, refuse clearly and explain why.
7. Be concise, friendly, and use emojis sparingly.
```

- [ ] **Step 1: Write failing tests**

```python
# tests/test_agent.py (uses mock for Gemini API)
from unittest.mock import patch, MagicMock

def test_agent_initializes():
    agent = CrossPayAgent("STU001", "fake-key")
    assert agent.student_id == "STU001"
    assert agent.pending_action is None

def test_confirm_without_pending_returns_message():
    agent = CrossPayAgent("STU001", "fake-key")
    result = agent.confirm_action()
    assert "no pending" in result.lower()

def test_cancel_clears_pending():
    agent = CrossPayAgent("STU001", "fake-key")
    agent.pending_action = {"tool": "add_expense", "args": {}}
    result = agent.cancel_action()
    assert agent.pending_action is None
    assert "cancelled" in result.lower()
```

- [ ] **Step 2: Run to verify failure**
```
pytest tests/test_agent.py -v
```

- [ ] **Step 3: Implement `src/agent.py`**

`CrossPayAgent.__init__`: creates `genai.Client(api_key=api_key)`, stores `student_id`, `pending_action = None`, `previous_interaction_id = None`.

`CrossPayAgent.chat(user_message)`:
1. Calls `client.interactions.create(model="gemini-3.8-flash", input=user_message, system_instruction=SYSTEM_PROMPT, tools=TOOL_DECLARATIONS, previous_interaction_id=self.previous_interaction_id)`
2. Stores returned `interaction.id` as `self.previous_interaction_id`
3. Iterates `interaction.steps` — for each `function_call` step: calls `dispatch_tool(step.name, step.arguments)`, checks if result has `confirmation_required=True`; if yes, stores as `self.pending_action = {"tool": step.name, "args": step.arguments, "preview": result}` and returns a formatted preview string asking for confirmation; if no `confirmation_required`, continues the loop
4. Returns `interaction.output_text` when no more function calls

`CrossPayAgent.confirm_action()`: if no pending, returns "No pending action." Calls `dispatch_tool(pending.tool, pending.args)` with `_confirmed=True` flag stripped, clears `pending_action`, returns confirmation message.

`CrossPayAgent.cancel_action()`: clears `pending_action`, returns "Action cancelled."

- [ ] **Step 4: Run tests to pass**
```
pytest tests/test_agent.py -v
```

- [ ] **Step 5: Commit**
```bash
git add src/agent.py tests/test_agent.py
git commit -m "feat: CrossPay Gemini agent with stateful chat and 2-step confirmation"
```

---

### Task 5: Streamlit UI

**Files:**
- Create: `app.py`
- Create: `src/ui_components.py`

**Interfaces:**
- Consumes: `CrossPayAgent` from `src/agent.py` (Task 4)
- Consumes: `get_db`, `seed_mock_data` from Task 1
- No test file required for UI — visual verification via running

**UI layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  🏦 CrossPay — Student Finance Assistant    [Student: STU001]│
├──────────────────┬──────────────────────────────────────────┤
│ SIDEBAR          │  MAIN CHAT AREA                          │
│                  │                                          │
│ 📊 Quick Stats   │  [Chat messages history]                 │
│  Balance: X CNY  │                                          │
│  Credit: XXX     │  [User input box]                        │
│  Tuition due: XX │  [Send] [Confirm ✓] [Cancel ✗]          │
│                  │                                          │
│ ⚡ Quick Actions │                                          │
│  [Check FX Rate] │                                          │
│  [Compare Remit] │                                          │
│  [My Budget]     │                                          │
│  [Credit Tips]   │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

- [ ] **Step 1: Implement `src/ui_components.py`**

`render_sidebar(student_data: dict) -> None`: displays balance, credit score progress bar, tuition countdown.
`render_message(role: str, content: str) -> None`: renders chat bubble with role label.
`render_quick_stats(student_data: dict) -> None`: metric cards for balance CNY, tuition days remaining, credit score tier.

- [ ] **Step 2: Implement `app.py`**

Top section: `st.set_page_config(page_title="CrossPay", page_icon="🏦", layout="wide")`
Session state init: `agent`, `messages`, `student_id` (from env or selectbox).
On startup: init DB, seed mock data, create `CrossPayAgent`.
Sidebar: quick stats + quick action buttons (each button pre-fills input with a question string).
Main: `st.chat_input` → calls `agent.chat(msg)` → appends to `messages`.
If `agent.pending_action` is not None: show "⚠️ Confirmation Required" banner with Confirm/Cancel buttons.
Confirm button → `agent.confirm_action()`. Cancel → `agent.cancel_action()`.

- [ ] **Step 3: Commit**
```bash
git add app.py src/ui_components.py
git commit -m "feat: Streamlit UI with sidebar stats, chat interface, and confirmation buttons"
```

---

### Task 6: Security Self-Assessment Report & Technical Documentation

**Files:**
- Create: `docs/spec/topic-c-spec.md`
- Create: `docs/security-assessment.md`
- Create: `docs/technical-documentation.md`
- Create: `docs/architecture.md`

**Interfaces:**
- No code — documentation deliverables for competition submission

- [ ] **Step 1: Write `docs/spec/topic-c-spec.md`** — single paragraph summarizing Topic C requirements from competition PDF

- [ ] **Step 2: Write `docs/security-assessment.md`** (Deliverable 05)

Structure:
1. **Permission Tiers** — Tier 0 (read-only: FX, rates, credit profile), Tier 1 (write with confirmation: expense add, budget set), Tier 2 (regulated: transfers > $10k, sanctioned checks)
2. **Threat Model** — 5 threat vectors: prompt injection, PII leakage, LLM arithmetic bypass, AML threshold gaming, unauthorized transfer
3. **Mitigations** — one-to-one mapping to threats with code locations
4. **Known Risk Register** — 3 acknowledged residual risks with severity ratings
5. **Data Flow Diagram** (ASCII)

- [ ] **Step 3: Write `docs/technical-documentation.md`** (Deliverable 01)

Structure: System Overview, Architecture Diagram, Agent Algorithm (tool call flow with mermaid), API Usage, Data Schema, Deployment Instructions

- [ ] **Step 4: Write `docs/architecture.md`** — ASCII + mermaid architecture diagram

- [ ] **Step 5: Commit**
```bash
git add docs/
git commit -m "docs: security assessment, technical documentation, architecture"
```

---

### Task 7: README, Execution Evidence & Final Polish

**Files:**
- Create: `README.md`
- Create: `scripts/generate_execution_evidence.py`
- Create: `docs/execution-evidence-summary.md`
- Create: `presentation/slides-outline.md`

**Interfaces:**
- Consumes: all prior tasks
- Produces: final submission-ready package

- [ ] **Step 1: Write `README.md`**

Sections: Project Overview, Competition Track (WeBank International), Features, Architecture (ASCII), Prerequisites, Setup (pip install -r requirements.txt, cp .env.example .env, add GEMINI_API_KEY), Running the App (streamlit run app.py), Running Tests (pytest --cov), Project Structure (tree), Team

- [ ] **Step 2: Implement `scripts/generate_execution_evidence.py`**

Script that: initializes DB, creates agent with mock API key stub (no real Gemini calls), runs 8 scripted tool calls covering all tool types, writes full execution log to `logs/execution_log.jsonl`, prints pretty summary table using `rich`. Run with `python scripts/generate_execution_evidence.py`.

- [ ] **Step 3: Run the evidence script and capture output**
```
python scripts/generate_execution_evidence.py
```
Expected: 8 tool calls logged, rich table printed.

- [ ] **Step 4: Write `docs/execution-evidence-summary.md`** (Deliverable 06)

Summary of execution log entries, tool coverage matrix, sample input/output pairs (PII-masked).

- [ ] **Step 5: Write `presentation/slides-outline.md`** (Deliverable 02 outline)

10 slides: Problem, Solution, Architecture, Demo Flow, Security Design, Innovation Highlights, Technical Stack, Roadmap, Team, Conclusion

- [ ] **Step 6: Final test run with coverage**
```
pytest --cov=src --cov-report=term-missing --cov-report=html -v
```
Expected: all tests pass, ≥ 80% coverage

- [ ] **Step 7: Final commit**
```bash
git add .
git commit -m "feat: README, execution evidence, presentation outline — submission ready"
git tag -a v1.0.0 -m "WeBank Topic C Competition Submission — Oct 2026"
```
