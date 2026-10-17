from src.tools.fx import get_exchange_rate, convert_amount, get_pboc_central_parity_rate, get_fx_volatility_metrics
from src.tools.remittance import compare_remittance_options, schedule_tuition_payment, commit_schedule_tuition_payment
from src.tools.budget import (
    get_spending_summary, set_budget_category, add_expense,
    commit_set_budget_category, commit_add_expense
)
from src.tools.credit import get_credit_profile, simulate_credit_action
from src.tools.compliance import (
    check_aml_threshold, check_sanctioned_destination, check_aml_structuring,
    check_safe_quota, verify_student_tuition_eligibility, get_cips_clearing_window
)
from src.tools.analytics import (
    get_fx_trend, get_spending_trend, get_credit_trend, get_worldbank_remittance,
    detect_spending_anomalies, get_cohort_spending_benchmarks
)
from src.tools.fraud import (
    screen_tuition_proxy_scam, screen_peer_exchange_risk,
    evaluate_transaction_fraud_risk, check_telecom_fraud_keywords
)
from src.logger import log_tool_call


# ---------------------------------------------------------------------------
# Gemini function-calling declarations
# ---------------------------------------------------------------------------
TOOL_DECLARATIONS = [
    {
        "name": "get_exchange_rate",
        "description": "Get the current mock exchange rate between two currencies with fee information. Always use this tool when the user asks about exchange rates — never estimate rates yourself.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_currency": {"type": "string", "description": "ISO 4217 source currency code (e.g. BDT, PKR, USD)"},
                "to_currency": {"type": "string", "description": "ISO 4217 target currency code (e.g. CNY, USD)"},
            },
            "required": ["from_currency", "to_currency"],
        },
    },
    {
        "name": "convert_amount",
        "description": "Convert a specific monetary amount from one currency to another, applying provider fee. Always use this tool for currency conversion — never calculate exchange amounts yourself.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert"},
                "from_currency": {"type": "string", "description": "Source currency code"},
                "to_currency": {"type": "string", "description": "Target currency code"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
    {
        "name": "compare_remittance_options",
        "description": "Compare cross-border remittance providers (SWIFT, WeBank, Wise, UnionPay) by fee and FX cost. Use when the student asks how to send money home or pay tuition.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount_usd": {"type": "number", "description": "Transfer amount in USD equivalent"},
                "destination_country": {"type": "string", "description": "ISO 3166-1 alpha-2 destination country code"},
            },
            "required": ["amount_usd", "destination_country"],
        },
    },
    {
        "name": "schedule_tuition_payment",
        "description": "Find the optimal window to schedule a tuition payment for better FX rates. Returns a preview requiring user confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID (e.g. STU001)"},
                "amount_cny": {"type": "number", "description": "Tuition amount in CNY"},
                "due_date": {"type": "string", "description": "Tuition due date in ISO format (YYYY-MM-DD)"},
            },
            "required": ["student_id", "amount_cny", "due_date"],
        },
    },
    {
        "name": "get_spending_summary",
        "description": "Get the student's spending summary by category for a given month.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "month": {"type": "string", "description": "Month in YYYY-MM format (e.g. 2026-10)"},
            },
            "required": ["student_id", "month"],
        },
    },
    {
        "name": "add_expense",
        "description": "Preview adding an expense to the student's ledger. Returns a preview requiring user confirmation before recording.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "amount_cny": {"type": "number", "description": "Expense amount in CNY"},
                "category": {"type": "string", "description": "Category (food, transport, books, utilities, entertainment, other)"},
                "note": {"type": "string", "description": "Optional description"},
            },
            "required": ["student_id", "amount_cny", "category"],
        },
    },
    {
        "name": "get_credit_profile",
        "description": "Get the student's credit score, tier, actionable tips, and next milestone.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "simulate_credit_action",
        "description": "Simulate how a specific credit-building action (e.g. open_secured_card) would improve the student's credit score.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action key: open_secured_card, pay_on_time_3mo, pay_tuition_early, reduce_utilization, become_authorized_user, report_rent_payments"},
                "student_id": {"type": "string", "description": "Student account ID"},
            },
            "required": ["action", "student_id"],
        },
    },
    {
        "name": "check_aml_threshold",
        "description": "Check if a transfer amount exceeds the $10,000 USD AML reporting threshold. Always call this before any large transfer.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount_usd": {"type": "number", "description": "Transfer amount in USD"},
            },
            "required": ["amount_usd"],
        },
    },
    {
        "name": "check_aml_structuring",
        "description": "Detect AML structuring (smurfing) across a rolling multi-day window. Evaluates aggregate transfer volume against the $10,000 AML limit.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "new_amount_usd": {"type": "number", "description": "Proposed transfer amount in USD"},
                "window_days": {"type": "integer", "description": "Rolling window in days (default 7)"},
            },
            "required": ["student_id", "new_amount_usd"],
        },
    },
    {
        "name": "check_sanctioned_destination",
        "description": "Check if a destination country is on the international sanctions list. Must be called before any cross-border transfer.",
        "parameters": {
            "type": "object",
            "properties": {
                "country_code": {"type": "string", "description": "ISO 3166-1 alpha-2 country code (e.g. CN, US, IR)"},
            },
            "required": ["country_code"],
        },
    },
    {
        "name": "get_fx_trend",
        "description": "Get historical foreign exchange rates for a currency pair against CNY over the past N days.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_currency": {"type": "string", "description": "Source currency code (e.g. BDT, PKR, NGN)"},
                "days": {"type": "integer", "description": "Number of historical days (default 30)"},
            },
            "required": ["from_currency"],
        },
    },
    {
        "name": "get_spending_trend",
        "description": "Get multi-month spending trend grouped by category for a student.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "months": {"type": "integer", "description": "Number of months (default 6)"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "get_credit_trend",
        "description": "Get historical credit score trajectory over recent months.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "get_worldbank_remittance",
        "description": "Look up official World Bank remittance data (2000–2024) for any country. Use when the user asks about global remittance flows, market size, or how much a country sends/receives. Returns amount in USD million and 5-year CAGR.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Country name (e.g. 'Bangladesh', 'Pakistan', 'Nigeria', 'China')"},
                "flow": {"type": "string", "description": "'outflow' for money sent abroad, 'inflow' for money received", "enum": ["outflow", "inflow"]},
                "year": {"type": "integer", "description": "Year between 2000 and 2024 (default 2023)"},
            },
            "required": ["country"],
        },
    },
    {
        "name": "get_pboc_central_parity_rate",
        "description": "Get the official People's Bank of China (PBOC) Central Parity Rate (人民币汇率中间价), +/-2.0% daily trading band, buying rate, and selling rate for a currency against CNY.",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {"type": "string", "description": "Foreign currency ISO code (default USD)"},
            },
        },
    },
    {
        "name": "get_fx_volatility_metrics",
        "description": "Calculate 30-day statistical FX volatility, Bollinger Bands (upper/lower), percentile ranking, and optimal timing recommendations for tuition remittance.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_currency": {"type": "string", "description": "Source currency code"},
                "to_currency": {"type": "string", "description": "Target currency code (default CNY)"},
            },
            "required": ["from_currency"],
        },
    },
    {
        "name": "check_safe_quota",
        "description": "Check China State Administration of Foreign Exchange (SAFE / 国家外汇管理局) $50,000 USD annual facilitation quota, YTD consumption, and genuine tuition exemption status.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "amount_usd": {"type": "number", "description": "Transfer amount in USD"},
                "purpose": {"type": "string", "description": "Transfer purpose (e.g. 'tuition', 'living_expense')"},
                "university_verified": {"type": "boolean", "description": "Whether admission letter and university invoice are attached"},
            },
            "required": ["student_id", "amount_usd"],
        },
    },
    {
        "name": "verify_student_tuition_eligibility",
        "description": "Verify student visa type (X1/X2), university enrollment code, and CIPS direct university clearing eligibility.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "get_cips_clearing_window",
        "description": "Get the operational status and next available settlement window for PBOC Cross-Border Interbank Payment System (CIPS / 人民币跨境支付系统).",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "detect_spending_anomalies",
        "description": "Run Tukey's IQR statistical anomaly detection over the student's transaction history to flag irregular spikes or potential fraud/overspending.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "threshold_iqr": {"type": "number", "description": "IQR multiplier threshold (default 1.5)"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "get_cohort_spending_benchmarks",
        "description": "Query population spending benchmarks (median living expenses, median tuition, popular payment channels) from the 5,000 international student dataset.",
        "parameters": {
            "type": "object",
            "properties": {
                "study_country": {"type": "string", "description": "Host study country (e.g. 'China', 'Malaysia', 'Germany')"},
            },
        },
    },
    {
        "name": "screen_tuition_proxy_scam",
        "description": "Screen tuition payment proposals for proxy payment scams, unauthorized discounts, and stolen credit card fraud.",
        "parameters": {
            "type": "object",
            "properties": {
                "tuition_amount_cny": {"type": "number", "description": "Official university tuition amount in CNY"},
                "quoted_cost_cny": {"type": "number", "description": "Amount requested by payment agent in CNY"},
                "payment_channel": {"type": "string", "description": "Payment channel (e.g. 'WeChat Agent', 'University Portal')"},
                "is_official_portal": {"type": "boolean", "description": "True if paying directly on university portal"},
            },
            "required": ["tuition_amount_cny", "quoted_cost_cny", "payment_channel", "is_official_portal"],
        },
    },
    {
        "name": "screen_peer_exchange_risk",
        "description": "Screen currency exchange channels against PBOC 'Card Break Action' (断卡行动) and illegal underground FX.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Exchange amount"},
                "currency": {"type": "string", "description": "Currency code (e.g. CNY, USD, BDT)"},
                "counterparty_type": {"type": "string", "description": "Type of counterparty (e.g. 'Licensed Bank', 'Private Individual')"},
                "platform": {"type": "string", "description": "Platform used (e.g. 'WeBank', 'WeChat Group', 'Telegram')"},
            },
            "required": ["amount", "currency", "counterparty_type", "platform"],
        },
    },
    {
        "name": "evaluate_transaction_fraud_risk",
        "description": "Evaluate composite multi-factor transaction fraud risk index (0-100) based on velocity, nocturnal off-hours, and channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Student account ID"},
                "amount_cny": {"type": "number", "description": "Transaction amount in CNY"},
                "channel": {"type": "string", "description": "Transaction channel"},
                "recipient_account": {"type": "string", "description": "Recipient account or identifier"},
                "hour_of_day": {"type": "integer", "description": "Hour of transaction in 24-hour CST (0-23)"},
                "recent_txn_count_1h": {"type": "integer", "description": "Number of transactions within the past 1 hour"},
            },
            "required": ["student_id", "amount_cny", "channel", "recipient_account", "hour_of_day", "recent_txn_count_1h"],
        },
    },
    {
        "name": "check_telecom_fraud_keywords",
        "description": "Scan text for PRC Anti-Telecom and Online Fraud keywords (safe accounts, public security impersonation, money mule card leasing).",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "User message or message to analyze for fraud indicators"},
            },
            "required": ["text"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------
_TOOL_MAP = {
    "get_exchange_rate": get_exchange_rate,
    "convert_amount": convert_amount,
    "compare_remittance_options": compare_remittance_options,
    "schedule_tuition_payment": schedule_tuition_payment,
    "get_spending_summary": get_spending_summary,
    "add_expense": add_expense,
    "get_credit_profile": get_credit_profile,
    "simulate_credit_action": simulate_credit_action,
    "check_aml_threshold": check_aml_threshold,
    "check_aml_structuring": check_aml_structuring,
    "check_sanctioned_destination": check_sanctioned_destination,
    "get_fx_trend": get_fx_trend,
    "get_spending_trend": get_spending_trend,
    "get_credit_trend": get_credit_trend,
    "get_worldbank_remittance": get_worldbank_remittance,
    "get_pboc_central_parity_rate": get_pboc_central_parity_rate,
    "get_fx_volatility_metrics": get_fx_volatility_metrics,
    "check_safe_quota": check_safe_quota,
    "verify_student_tuition_eligibility": verify_student_tuition_eligibility,
    "get_cips_clearing_window": get_cips_clearing_window,
    "detect_spending_anomalies": detect_spending_anomalies,
    "get_cohort_spending_benchmarks": get_cohort_spending_benchmarks,
    "screen_tuition_proxy_scam": screen_tuition_proxy_scam,
    "screen_peer_exchange_risk": screen_peer_exchange_risk,
    "evaluate_transaction_fraud_risk": evaluate_transaction_fraud_risk,
    "check_telecom_fraud_keywords": check_telecom_fraud_keywords,
    # Commit variants (used after user confirms)
    "commit_set_budget_category": commit_set_budget_category,
    "commit_add_expense": commit_add_expense,
    "commit_schedule_tuition_payment": commit_schedule_tuition_payment,
}


def dispatch_tool(name: str, args: dict) -> dict:
    """Route a tool name to its function, log the call, and return the result."""
    fn = _TOOL_MAP.get(name)
    if fn is None:
        raise ValueError(f"Unknown tool: {name}")
    result = fn(**args)
    # Ensure result is always a dict (list results wrapped for logging)
    result_for_log = result if isinstance(result, dict) else {"items": result}
    log_tool_call(name, args, result_for_log)
    return result
