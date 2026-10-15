# CrossPay Execution Evidence Summary

**Deliverable 06 — Competition Submission**  
**Generated:** October 2026  
**Log file:** `logs/execution_log.jsonl`  

---

## Tool Coverage Matrix

| # | Tool Name | Category | Tier | Status | Compliance Feature |
|---|-----------|----------|------|--------|--------------------|
| 1 | `get_exchange_rate` | FX | 0 (Read) | ✅ Executed | Rate timestamped, provider labeled |
| 2 | `convert_amount` | FX | 0 (Read) | ✅ Executed | Deterministic calculation |
| 3 | `compare_remittance_options` | Remittance | 0 (Read) | ✅ Executed | 4 providers, sorted by cost |
| 4 | `schedule_tuition_payment` | Remittance | 2 (Regulated) | ✅ Executed | `confirmation_required=True` |
| 5 | `get_spending_summary` | Budget | 0 (Read) | ✅ Executed | DB query, no LLM arithmetic |
| 6 | `get_credit_profile` | Credit | 0 (Read) | ✅ Executed | Score 680, Good tier, 5 tips |
| 7 | `check_aml_threshold` | Compliance | 2 (Regulated) | 🚩 FLAGGED | $12,500 > $10,000 threshold |
| 8 | `check_sanctioned_destination` | Compliance | 2 (Regulated) | 🚫 BLOCKED | Iran (IR) — sanctioned |

**All 8 tool calls logged to `logs/execution_log.jsonl` with:**
- Timestamp (ISO 8601 UTC)
- Tool name
- PII-masked inputs
- Truncated output summary (≤200 chars)

---

## Sample Log Entries

Each entry in `logs/execution_log.jsonl` follows this format:

```json
{"timestamp": "2026-10-15T15:33:00Z", "tool_name": "get_exchange_rate", "inputs": {"from_currency": "BDT", "to_currency": "CNY"}, "output_summary": "{\"rate\": 0.065179, \"from_currency\": \"BDT\", \"to_currency\": \"CNY\", \"provider\": \"CrossPay FX (Mock Data)\", \"timestamp\": \"...\"..."}
```

---

## Security Evidence

### PII Masking Verified
- All inputs logged through `mask_pii()` before writing
- Account numbers (8+ digits) replaced with `****`
- Passport patterns replaced with `XX****`
- Test: `tests/test_logger.py::test_log_masks_pii_in_inputs` — ✅ PASS

### AML Threshold Enforcement
- Tool call #7: `check_aml_threshold({"amount_usd": 12500.0})` → `flagged: true`
- Test: `tests/test_tools.py::test_aml_flags_above_10000` — ✅ PASS

### Sanctions Screening
- Tool call #8: `check_sanctioned_destination({"country_code": "IR"})` → `blocked: true`
- Test: `tests/test_tools.py::test_sanctioned_destination_blocks_iran` — ✅ PASS

### Confirmation Gate
- Tool call #4: `schedule_tuition_payment(...)` → `confirmation_required: true`
- DB write does NOT occur until `confirm_action()` is called from UI
- Test: `tests/test_tools.py::test_schedule_tuition_requires_confirmation` — ✅ PASS
