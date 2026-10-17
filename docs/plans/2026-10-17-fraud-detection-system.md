# CrossPay Institutional Fraud Detection & Anti-Scam System (智能反诈与风控系统) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an institutional-grade, deterministic Fraud Detection and Anti-Scam Risk Engine (智能反诈与风控系统) tailored for international students in China, covering tuition proxy payment scams, illegal underground FX ("Card Break Action" / 断卡行动), money mule detection, telecom fraud keyword filtering, and multi-factor transaction risk scoring.

**Architecture:** Layered deterministic Python risk engine (`src/tools/fraud.py`) exposing standardized risk scoring (0–100 index) and actionable tiers (LOW, MEDIUM, HIGH, CRITICAL). Integrated into `src/tool_registry.py` for Gemini function calling, wired into `src/autonomous_engine.py` for sub-15ms offline bilingual NLU intent classification, and surfaced via interactive Streamlit UI badges and alerts.

**Tech Stack:** Python 3.14, SQLite3, Pytest, Streamlit, Google GenAI SDK (`gemini-3.8-flash`).

**Spec:** `docs/spec/topic-c-spec.md` + WeBank International AI Finance Challenge (Topic C: Cross-Border & Student Finance) + PRC Anti-Telecom and Online Fraud Law (《中华人民共和国反电信网络诈骗法》).

## Global Constraints

- **Zero Mathematical / Risk Hallucination**: All fraud risk calculations and threshold screenings must execute in deterministic Python, never in LLM prompt arithmetic.
- **100% Offline Autonomy**: The fraud detection engine must run with zero external API calls and zero cloud dependencies.
- **Bilingual Support**: All risk warnings, red flag advisories, and recommendations must provide both English and Simplified Chinese (简体中文).
- **Test Integrity**: Every test suite must achieve 100% pass rate (`python -m pytest tests/ -v`).
- **Regulatory Grounding**: Must explicitly cite PRC Anti-Telecom and Online Fraud Law, PBOC regulations, Ministry of Education tuition warnings, and China's National Anti-Fraud Hotline (96110).

## Review Focus

1. **Tuition Discount Gaming**: Input with a small (<5%) currency rounding variance should NOT be flagged as a scam, while discounts >= 10% must trigger CRITICAL tuition proxy scam warnings.
2. **Channel Validation**: Transactions through official university portals or WeBank Direct must be recognized as verified/safe, while WeChat private groups, Telegram, and unverified P2P must trigger high "Card Break" (断卡行动) risk scores.
3. **Off-Hours & Velocity Edge Cases**: High-frequency transactions (>3 txns/hour) or transactions occurring during high-risk night hours (01:00–05:00 CST) must elevate transaction risk tiers even for legitimate amounts.
4. **Telecom Keyword False Positives**: General words like "safe", "account", or "tax" in normal budgeting sentences must not trigger telecom scam alarms; only fraud-specific multi-word patterns (e.g. "safe account transfer", "安全账户", "公检法调查", "8折代缴学费") should trigger.
5. **PII Masking Preservation**: Recipient accounts analyzed by fraud detection must undergo the same regex PII masking before logging to `logs/execution_log.jsonl`.

---

### Task 1: Core Fraud Detection Engine (`src/tools/fraud.py`)

**Files:**
- Create: `src/tools/fraud.py`
- Test: `tests/test_fraud_detection.py`

**Interfaces:**
- Produces:
  - `screen_tuition_proxy_scam(tuition_amount_cny: float, quoted_cost_cny: float, payment_channel: str, is_official_portal: bool) -> dict`
  - `screen_peer_exchange_risk(amount: float, currency: str, counterparty_type: str, platform: str) -> dict`
  - `evaluate_transaction_fraud_risk(student_id: str, amount_cny: float, channel: str, recipient_account: str, hour_of_day: int, recent_txn_count_1h: int) -> dict`
  - `check_telecom_fraud_keywords(text: str) -> dict`

- [ ] **Step 1: Write the failing tests in `tests/test_fraud_detection.py`**

```python
import pytest
from src.tools.fraud import (
    screen_tuition_proxy_scam,
    screen_peer_exchange_risk,
    evaluate_transaction_fraud_risk,
    check_telecom_fraud_keywords,
)

def test_screen_tuition_proxy_scam_flags_deep_discount():
    # 20% discount offered by third-party proxy
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=8000.0,
        payment_channel="WeChat Private Agent",
        is_official_portal=False
    )
    assert result["scam_detected"] is True
    assert result["risk_tier"] == "CRITICAL"
    assert result["risk_score"] >= 85
    assert any("discount" in flag.lower() for flag in result["red_flags"])

def test_screen_tuition_proxy_scam_passes_official_portal():
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=10000.0,
        payment_channel="University Portal",
        is_official_portal=True
    )
    assert result["scam_detected"] is False
    assert result["risk_tier"] == "LOW"
    assert result["risk_score"] < 20

def test_screen_peer_exchange_risk_flags_underground_p2p():
    result = screen_peer_exchange_risk(
        amount=5000.0,
        currency="CNY",
        counterparty_type="Private Individual",
        platform="WeChat Group"
    )
    assert result["card_freeze_risk"] is True
    assert result["risk_tier"] in ["HIGH", "CRITICAL"]
    assert "断卡行动" in result["warning_zh"]

def test_screen_peer_exchange_risk_passes_licensed_bank():
    result = screen_peer_exchange_risk(
        amount=5000.0,
        currency="CNY",
        counterparty_type="Licensed Bank",
        platform="WeBank"
    )
    assert result["card_freeze_risk"] is False
    assert result["risk_tier"] == "LOW"

def test_evaluate_transaction_fraud_risk_high_velocity_and_night():
    result = evaluate_transaction_fraud_risk(
        student_id="STU001",
        amount_cny=4500.0,
        channel="Alipay Unverified QR",
        recipient_account="622202******9876",
        hour_of_day=3,  # 3 AM off-hours
        recent_txn_count_1h=4  # High velocity
    )
    assert result["risk_score"] >= 70
    assert result["risk_tier"] in ["HIGH", "CRITICAL"]
    assert result["action_required"] in ["STEP_UP_AUTH", "HARD_BLOCK"]

def test_evaluate_transaction_fraud_risk_normal_daytime_single():
    result = evaluate_transaction_fraud_risk(
        student_id="STU001",
        amount_cny=150.0,
        channel="WeBank Direct",
        recipient_account="University Cafeteria",
        hour_of_day=12,
        recent_txn_count_1h=1
    )
    assert result["risk_score"] < 30
    assert result["risk_tier"] == "LOW"
    assert result["action_required"] == "PROCEED"

def test_check_telecom_fraud_keywords_triggers_safe_account():
    result = check_telecom_fraud_keywords("Please transfer funds to the safe account 安全账户 for verification")
    assert result["fraud_pattern_detected"] is True
    assert "safe account" in result["pattern_type"].lower()
    assert "96110" in result["hotline"]

def test_check_telecom_fraud_keywords_clean_query():
    result = check_telecom_fraud_keywords("What is the exchange rate for BDT to CNY?")
    assert result["fraud_pattern_detected"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_fraud_detection.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.tools.fraud')

- [ ] **Step 3: Implement `src/tools/fraud.py`**

Implement the 4 deterministic risk scoring and anti-scam evaluation functions:
1. `screen_tuition_proxy_scam`: Computes discount percentage ($1 - \frac{\text{quoted}}{\text{tuition}}$), flags unverified proxy intermediaries, assesses risks against university chargeback penalties.
2. `screen_peer_exchange_risk`: Evaluates P2P private chat exchange risks under China's "Card Break Action" (断卡行动) and Anti-Telecom and Online Fraud Law, warning of account freezes.
3. `evaluate_transaction_fraud_risk`: Multi-factor composite risk index (0–100) combining amount, velocity, channel verification, and off-hours factors.
4. `check_telecom_fraud_keywords`: Scans for classic fraud patterns ("安全账户", "公检法", "代缴学费打折", "跑分", "租卡", "安全基金", "私下换汇") and returns bilingual advisories citing the 96110 hotline.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_fraud_detection.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/tools/fraud.py tests/test_fraud_detection.py
git commit -m "feat(fraud): implement deterministic anti-scam & transaction fraud risk engine"
```

---

### Task 2: Tool Registry Registration & Function Calling Declarations

**Files:**
- Modify: `src/tool_registry.py`
- Test: `tests/test_logger.py` & `tests/test_fraud_detection.py`

**Interfaces:**
- Consumes: `src/tools/fraud.py`
- Produces: 4 new function declarations in `TOOL_DECLARATIONS` and entries in `_TOOL_MAP`.

- [ ] **Step 1: Write tests for fraud tool dispatch in `tests/test_fraud_detection.py`**

```python
from src.tool_registry import dispatch_tool, TOOL_DECLARATIONS

def test_dispatch_tool_screen_tuition_proxy_scam():
    result = dispatch_tool("screen_tuition_proxy_scam", {
        "tuition_amount_cny": 10000.0,
        "quoted_cost_cny": 7500.0,
        "payment_channel": "WeChat Agent",
        "is_official_portal": False
    })
    assert "scam_detected" in result
    assert result["scam_detected"] is True

def test_dispatch_tool_evaluate_fraud_risk():
    result = dispatch_tool("evaluate_transaction_fraud_risk", {
        "student_id": "STU001",
        "amount_cny": 12000.0,
        "channel": "P2P",
        "recipient_account": "6222000011112222",
        "hour_of_day": 3,
        "recent_txn_count_1h": 5
    })
    assert "fraud_risk_score" in result
    assert result["fraud_risk_score"] > 60

def test_fraud_tools_in_tool_declarations():
    names = [d["name"] for d in TOOL_DECLARATIONS]
    assert "screen_tuition_proxy_scam" in names
    assert "screen_peer_exchange_risk" in names
    assert "evaluate_transaction_fraud_risk" in names
    assert "check_telecom_fraud_keywords" in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_fraud_detection.py -k "dispatch" -v`
Expected: FAIL (KeyError / Unknown tool)

- [ ] **Step 3: Update `src/tool_registry.py`**

Import functions from `src.tools.fraud`, add `screen_tuition_proxy_scam`, `screen_peer_exchange_risk`, `evaluate_transaction_fraud_risk`, and `check_telecom_fraud_keywords` to `_TOOL_MAP`, and add corresponding Gemini schema declarations to `TOOL_DECLARATIONS`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_fraud_detection.py -v`
Expected: 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/tool_registry.py tests/test_fraud_detection.py
git commit -m "feat(registry): register fraud detection and anti-scam tools in tool registry"
```

---

### Task 3: Autonomous NLU Engine Integration & Bilingual Anti-Scam Response

**Files:**
- Modify: `src/autonomous_engine.py`
- Test: `tests/test_nlp_accuracy.py` & `tests/test_fraud_detection.py`

**Interfaces:**
- Consumes: `src/tools/fraud.py`
- Produces: `INTENT_FRAUD_CHECK` intent classification and bilingual conversational risk reporting.

- [ ] **Step 1: Write tests for autonomous engine fraud detection in `tests/test_fraud_detection.py`**

```python
from src.autonomous_engine import AutonomousFinTechEngine

def test_autonomous_engine_detects_tuition_scam_query_en():
    engine = AutonomousFinTechEngine("STU001")
    response = engine.chat("Someone on WeChat offered me 20% discount on my tuition, is it a scam?")
    assert "scam" in response.lower() or "fraud" in response.lower()
    assert "96110" in response or "chargeback" in response.lower()

def test_autonomous_engine_detects_card_break_risk_zh():
    engine = AutonomousFinTechEngine("STU001")
    response = engine.chat("有人想租借我的银行卡和微信支付二维码，可以借吗？")
    assert "断卡行动" in response or "违法" in response or "反诈" in response
    assert "96110" in response

def test_autonomous_engine_telecom_safe_account_warning():
    engine = AutonomousFinTechEngine("STU001")
    response = engine.chat("Police told me my account is frozen and asked to transfer money to a safe account")
    assert "safe account" in response.lower() or "安全账户" in response or "fraud" in response.lower()
    assert "96110" in response
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_fraud_detection.py -k "autonomous" -v`
Expected: FAIL (engine handles query as generic greeting or unknown intent)

- [ ] **Step 3: Update `src/autonomous_engine.py`**

1. Add `INTENT_FRAUD_CHECK` to intent classifier with English and Chinese patterns:
   - English: `"scam"`, `"fraud"`, `"discount on tuition"`, `"cheap tuition"`, `"rent bank card"`, `"safe account"`, `"private exchange"`
   - Chinese: `"代缴"`, `"打折学费"`, `"优惠学费"`, `"地下钱庄"`, `"私自换汇"`, `"安全账户"`, `"租卡"`, `"借卡"`, `"跑分"`, `"断卡"`, `"公检法"`, `"骗局"`, `"反诈"`
2. Implement intent handler `_handle_fraud_check` in `AutonomousFinTechEngine`:
   - Checks keyword patterns via `check_telecom_fraud_keywords`.
   - Parses discount numbers if tuition discount query.
   - Formats clear, authoritative bilingual response with National Anti-Fraud Center Hotline (96110) and legal citations under the PRC Anti-Telecom Fraud Law.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_fraud_detection.py -v`
Expected: 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/autonomous_engine.py tests/test_fraud_detection.py
git commit -m "feat(nlu): integrate fraud and scam detection intent into autonomous NLU engine"
```

---

### Task 4: UI & Dashboard Integration (Pages 1, 2, 4)

**Files:**
- Modify: `pages/1_📊_Dashboard.py`
- Modify: `pages/2_🤖_AI_Assistant.py`
- Modify: `pages/4_⚙️_Settings.py`
- Test: Verify syntax and regression test suite

**Interfaces:**
- Displays fraud risk tier indicators, quick anti-scam check prompt, and regulatory anti-fraud hotline settings.

- [ ] **Step 1: Update `pages/1_📊_Dashboard.py`**

Add an **Anti-Fraud & Risk Status Card (智能风控与反诈中心)** in the risk & alert section displaying:
- Current account anti-fraud status: 🟢 **LOW RISK / 正常受保护** (0 alert flags).
- Active monitoring: PRC Anti-Telecom Fraud Law compliance, "Card Break" protection, Tuition proxy defense.
- National Anti-Fraud Hotline pill: `📞 96110`.

- [ ] **Step 2: Update `pages/2_🤖_AI_Assistant.py`**

Add a quick action button: `🛡️ Anti-Scam Check / 反诈自查` ("Check if a tuition payment offer or private exchange is safe under Chinese law").

- [ ] **Step 3: Update `pages/4_⚙️_Settings.py`**

Add an **Anti-Fraud & Regulatory Risk Parameters (反电信网络诈骗与风控参数)** section displaying:
- Anti-Telecom and Online Fraud Law (《反电信网络诈骗法》) enforcement status: Active.
- "Card Break Action" (断卡行动) risk monitoring: Enabled.
- Maximum allowable tuition discount before scam lock: 5.0%.
- Anti-Fraud Hotline: 96110.

- [ ] **Step 4: Verify syntax and run tests**

Run:
```bash
python -c "import ast; ast.parse(open('pages/1_📊_Dashboard.py', encoding='utf-8').read()); print('Page 1 OK')"
python -c "import ast; ast.parse(open('pages/2_🤖_AI_Assistant.py', encoding='utf-8').read()); print('Page 2 OK')"
python -c "import ast; ast.parse(open('pages/4_⚙️_Settings.py', encoding='utf-8').read()); print('Page 4 OK')"
python -m pytest tests/ -v
```
Expected: All pages parse cleanly; all 120+ tests pass.

- [ ] **Step 5: Commit**

```bash
git add pages/1_📊_Dashboard.py pages/2_🤖_AI_Assistant.py pages/4_⚙️_Settings.py
git commit -m "feat(ui): add anti-fraud risk cards, anti-scam quick prompts, and settings parameters"
```

---

### Task 5: Competition Deliverables & Documentation Update

**Files:**
- Modify: `docs/security-assessment.md` (Deliverable 05)
- Modify: `docs/technical-documentation.md` (Deliverable 01)
- Modify: `README.md`
- Test: Full regression test run (`python -m pytest tests/ -v`)

- [ ] **Step 1: Update `docs/security-assessment.md` (Deliverable 05)**

Add Section 6: **Anti-Telecom and Online Fraud Architecture (反电信网络诈骗与防洗钱风控体系)**:
- Threat analysis of Tuition Proxy Payment Scams (学费代缴陷阱).
- Defense against "Card Break" (断卡行动) money mule recruitment (跑分洗钱风险).
- Deterministic 4-tier risk classification (LOW, MEDIUM, HIGH, CRITICAL).
- Regulatory grounding in the 2022 PRC Anti-Telecom and Online Fraud Law.

- [ ] **Step 2: Update `docs/technical-documentation.md` (Deliverable 01)**

Document `src/tools/fraud.py` module, signatures, parameters, risk thresholds, and NLU intents.

- [ ] **Step 3: Update `README.md`**

Update badges, features, and test counts to reflect the new fraud detection engine and passing tests.

- [ ] **Step 4: Run full test suite and verify 100% pass rate**

Run: `python -m pytest tests/ -v`
Expected: 100% passing across all 12 test suites.

- [ ] **Step 5: Commit**

```bash
git add docs/security-assessment.md docs/technical-documentation.md README.md
git commit -m "docs: document institutional fraud detection & anti-scam system across deliverables"
```
