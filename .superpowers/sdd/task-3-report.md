# Task 3 Report — Audit Logger & Gemini Tool Registry

## Status: DONE

---

## Files Created

| File | Purpose |
|------|---------|
| `src/logger.py` | `log_tool_call()` — appends masked+truncated JSONL audit entries to `logs/execution_log.jsonl` |
| `src/tool_registry.py` | `TOOL_DECLARATIONS` (10 Gemini function-calling schemas) + `dispatch_tool()` router with audit logging |
| `tests/test_logger.py` | 13 TDD tests for logger and registry (written before implementation) |

---

## Test Results

### New tests (`tests/test_logger.py`)
```
python -m pytest tests/test_logger.py -v --tb=short
======================= 13 passed, 14 warnings in 0.20s =======================
```

All 13 tests pass:
- `test_log_creates_jsonl_file` ✅
- `test_log_appends_multiple_entries` ✅
- `test_log_entry_has_required_fields` ✅
- `test_log_masks_pii_in_inputs` ✅
- `test_log_output_summary_truncated` ✅
- `test_dispatch_tool_get_exchange_rate` ✅
- `test_dispatch_tool_convert_amount` ✅
- `test_dispatch_tool_compare_remittance` ✅
- `test_dispatch_tool_check_aml` ✅
- `test_dispatch_tool_check_sanctions` ✅
- `test_dispatch_tool_unknown_raises` ✅
- `test_tool_declarations_is_list` ✅
- `test_tool_declarations_have_required_fields` ✅

### Full suite (regression check)
```
python -m pytest tests/ -v --tb=short
======================= 40 passed, 22 warnings in 0.22s =======================
```

- Prior tests: 27 (test_db.py + test_tools.py) — all still passing ✅
- New tests: 13 — all passing ✅
- Total: **40 passed, 0 failed**

---

## Commits

| Hash | Message |
|------|---------|
| `4714859` | `feat: audit logger and Gemini tool registry` |

---

## Implementation Notes

### `src/logger.py`
- `log_tool_call(tool_name, inputs, output, log_dir="logs")` appends one JSON line per call
- Calls `mask_pii()` from `src.tools.compliance` to redact digits ≥ 5 chars in the serialised inputs before storage
- Truncates `output_summary` to 200 chars (+ `"..."`) to keep log file sizes bounded
- `log_dir` is a keyword parameter so tests can redirect to `tmp_path` without touching `logs/`

### `src/tool_registry.py`
- `TOOL_DECLARATIONS`: list of 10 dicts in Gemini function-calling schema format (name, description, parameters.type/properties/required)
- `_TOOL_MAP`: maps all 10 primary tools + 2 commit variants (`commit_set_budget_category`, `commit_add_expense`)
- `dispatch_tool(name, args)`: looks up function, calls it with `**args`, wraps list results in `{"items": ...}` for uniform logging, calls `log_tool_call`, returns raw result

---

## Concerns / Deviations

- `datetime.utcnow()` produces a `DeprecationWarning` under Python 3.14 — consistent with existing Task 2 code. Not changed to avoid deviation from spec; can be addressed globally in a cleanup pass.
- No concerns otherwise — implementation follows spec exactly.
