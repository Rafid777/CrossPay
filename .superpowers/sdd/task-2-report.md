# Task 2 Report — Financial Tools (Deterministic Core)

**Status:** DONE  
**Commit:** `966bb9c` — `feat: deterministic financial tools (FX, remittance, budget, credit, compliance)`

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `src/tools/__init__.py` | 1 | Package marker |
| `src/tools/compliance.py` | 40 | AML threshold check, sanctions list, PII masking |
| `src/tools/fx.py` | 52 | Mock exchange rates, convert_amount with 0.5% fee |
| `src/tools/remittance.py` | 48 | Multi-provider comparison, tuition scheduling |
| `src/tools/budget.py` | 93 | Spending summary (DB), preview + commit for budget/expense |
| `src/tools/credit.py` | 70 | Credit tier, tips, action simulation |
| `tests/test_tools.py` | 118 | 24 tests covering all modules (TDD — written first) |

---

## Test Results

**Command:**
```
python -m pytest tests/test_tools.py -v --tb=short
```

**Result:** 24 passed, 0 failed, 8 warnings (deprecation: `datetime.utcnow()` in Python 3.14 — retained per spec code)

**Coverage:**
```
python -m pytest tests/test_tools.py -v --cov=src/tools --cov-report=term-missing
```

| Module | Stmts | Miss | Cover |
|--------|-------|------|-------|
| `compliance.py` | 14 | 0 | **100%** |
| `remittance.py` | 16 | 0 | **100%** |
| `credit.py` | 25 | 1 | **96%** |
| `fx.py` | 20 | 2 | **90%** |
| `budget.py` | 36 | 14 | **61%** |
| **TOTAL** | 111 | 17 | **85%** ✓ |

> Coverage target was ≥80% — achieved **85%**. `budget.py` misses cover on `commit_set_budget_category` and `commit_add_expense` (intentionally not tested here — they are called only after user confirmation which is an integration concern for later tasks).

---

## Implementation Notes

### Bug Fix During TDD
The spec's `fx.py` had an inverted rate formula (`to_usd / from_usd` → gave 0.137 for USD→CNY instead of 7.28). Fixed to `from_usd / to_usd` where `_RATES_TO_USD` stores "USD value of 1 unit of currency".

### Global Constraints Verified
- ✅ AML threshold: `amount_usd > 10_000` (strictly greater — exactly 10000 is NOT flagged)
- ✅ Sanctioned countries: `{"IR","KP","SY","CU","SD","MM","BY","VE","ZW","RU"}`
- ✅ `confirmation_required=True` on all transfer/write actions
- ✅ PII masking: 8+ digit sequences and 2-letter+6-9 digit passport patterns
- ✅ All monetary math in pure Python functions, no LLM computation
- ✅ Python 3.14 compatible

### Concerns
- `datetime.utcnow()` is deprecated in Python 3.14 (produces DeprecationWarning). Retained as per spec. Consider migrating to `datetime.now(datetime.UTC)` in a future task.
- `budget.py` `commit_*` functions write to the default `data/crosspay.db` path. Tests use the same live DB (no in-memory isolation). This is fine for now but should be refactored with dependency injection in integration tests.

---

## Commits Made

| Hash | Message |
|------|---------|
| `966bb9c` | `feat: deterministic financial tools (FX, remittance, budget, credit, compliance)` |
