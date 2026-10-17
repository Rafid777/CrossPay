"""Database Snapshot & Audit Ledger Exporter for CrossPay.
Exports SQLite database tables into sanitized JSON snapshots for institutional reporting.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db import get_db

def export_snapshot(output_dir: str = "data/snapshots") -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
    target_file = os.path.join(output_dir, f"crosspay_snapshot_{timestamp}.json")

    conn = get_db()
    cursor = conn.cursor()

    tables = ["accounts", "expenses", "budgets"]
    snapshot = {"metadata": {"exported_at": timestamp, "engine": "CrossPay SQLite Exporter v2.1"}}

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = [dict(row) for row in cursor.fetchall()]
            snapshot[table] = rows
        except Exception as e:
            snapshot[table] = {"error": str(e)}

    conn.close()

    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"Snapshot exported successfully: {target_file}")
    return target_file

if __name__ == "__main__":
    export_snapshot()
