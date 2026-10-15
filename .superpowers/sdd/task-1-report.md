# Task 1 Report — Project Scaffolding, Mock Data & Database

## Status: DONE

## Files Created

| File | Description |
|------|-------------|
| `src/__init__.py` | Empty package init |
| `src/db.py` | SQLite database module with `get_db()`, creates accounts/expenses/budgets tables |
| `src/mock_data.py` | Mock student data + `seed_mock_data()` for 3 students with masked passport/bank |
| `data/.gitkeep` | Placeholder for data directory |
| `logs/.gitkeep` | Placeholder for logs directory |
| `tests/__init__.py` | Empty package init |
| `tests/test_db.py` | TDD tests (written before implementation) |
| `requirements.txt` | All project dependencies |
| `.env.example` | Example environment variables |
| `.gitignore` | Excludes .env, DB, logs, pycache |

## Test Results

Command: `python -m pytest tests/test_db.py -v`

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\Project China
plugins: anyio-4.14.1, cov-7.1.0
collecting ... collected 3 items

tests/test_db.py::test_db_creates_accounts_table PASSED                  [ 33%]
tests/test_db.py::test_mock_data_seeds_three_accounts PASSED             [ 66%]
tests/test_db.py::test_passport_never_stored_plaintext PASSED            [100%]

============================== 3 passed in 0.13s
```

## Git Commit

```
Hash: 3ff7f54
Message: feat: project scaffold, mock DB, seeded accounts
Files: 12 files changed, 834 insertions(+)
```

## Notes / Concerns

- `pytest` binary is installed to `C:\Users\shahf\AppData\Roaming\Python\Python314\Scripts` which is not on PATH. Tests run successfully via `python -m pytest` instead.
- `pip install -r requirements.txt` exited with code 1 due to PATH warnings (not errors); all packages installed successfully as confirmed by the output.
- TDD order observed: test file written → confirmed failure (ImportError) → implementation → all 3 passed.
- Passport numbers and bank accounts stored pre-masked in MOCK_STUDENTS constant per spec ("BD****1234", "****4321" pattern).
- All three tables (accounts, expenses, budgets) created in `get_db()` as per spec, ready for future tasks.
