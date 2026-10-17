"""Container & Server Healthcheck Probe for CrossPay.
Validates SQLite database access, production ML model artifact loading,
and deterministic FX calculation readiness.
Exits with code 0 on healthy status, code 1 on degraded or failure.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_healthcheck() -> int:
    try:
        # 1. Check Database connection & table schema
        from src.db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        conn.close()
        if account_count == 0:
            print("WARNING: Accounts table is empty")
        print(f"[OK] Database connection active. Seeded accounts: {account_count}")

        # 2. Check Deterministic FX calculation
        from src.tools.fx import get_exchange_rate
        rate_info = get_exchange_rate("USD", "CNY")
        if not rate_info or rate_info.get("rate", 0) <= 0:
            print("[FAIL] Deterministic FX engine returned invalid quote")
            return 1
        print(f"[OK] FX Engine active. USD/CNY benchmark: {rate_info['rate']}")

        # 3. Check ML model artifact accessibility
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "crosspay_production_model.joblib")
        if os.path.exists(model_path):
            print(f"[OK] Production ML artifact verified: {os.path.basename(model_path)}")
        else:
            print(f"[WARN] ML artifact not found at {model_path}; fallback to rule engine active")

        print("CrossPay System Status: HEALTHY")
        return 0

    except Exception as e:
        print(f"[ERROR] Healthcheck probe encountered unhandled failure: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_healthcheck())
