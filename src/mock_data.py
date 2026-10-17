import sqlite3


MOCK_STUDENTS = [
    {
        "id": "STU001",
        "name": "Rafi Ahmed",
        "email": "rafi.ahmed@student.edu",
        "home_currency": "BDT",
        "home_country": "BD",
        "host_country": "CN",
        "host_currency": "CNY",
        "balance_home": 50000.0,
        "balance_cny": 3500.0,
        "tuition_due_date": "2026-11-01",
        "tuition_amount_cny": 8000.0,
        "credit_score": 680,
        "passport_number": "BD****1234",
        "bank_account": "****4321",
    },
    {
        "id": "STU002",
        "name": "Ayesha Khan",
        "email": "ayesha.khan@student.edu",
        "home_currency": "PKR",
        "home_country": "PK",
        "host_country": "CN",
        "host_currency": "CNY",
        "balance_home": 120000.0,
        "balance_cny": 2100.0,
        "tuition_due_date": "2026-11-15",
        "tuition_amount_cny": 12000.0,
        "credit_score": 620,
        "passport_number": "PK****5678",
        "bank_account": "****8765",
    },
    {
        "id": "STU003",
        "name": "Emeka Okafor",
        "email": "emeka.okafor@student.edu",
        "home_currency": "NGN",
        "home_country": "NG",
        "host_country": "CN",
        "host_currency": "CNY",
        "balance_home": 800000.0,
        "balance_cny": 5000.0,
        "tuition_due_date": "2026-12-01",
        "tuition_amount_cny": 15000.0,
        "credit_score": 590,
        "passport_number": "NG****9012",
        "bank_account": "****2109",
    },
]


def seed_mock_data(conn: sqlite3.Connection) -> None:
    """Insert mock student accounts using INSERT OR IGNORE to avoid duplicates."""
    conn.executemany(
        """
        INSERT OR IGNORE INTO accounts (
            id, name, email, home_currency, home_country,
            host_country, host_currency, balance_home, balance_cny,
            tuition_due_date, tuition_amount_cny, credit_score,
            passport_number, bank_account
        ) VALUES (
            :id, :name, :email, :home_currency, :home_country,
            :host_country, :host_currency, :balance_home, :balance_cny,
            :tuition_due_date, :tuition_amount_cny, :credit_score,
            :passport_number, :bank_account
        )
        """,
        MOCK_STUDENTS,
    )
    conn.commit()
    seed_rich_history(conn)
    seed_synthetic_transactions(conn)


def seed_rich_history(conn: sqlite3.Connection) -> None:
    """Seed 6 months of transaction history, FX trends, and credit history."""
    from datetime import date, timedelta
    import math

    # ── 1. Expense history ───────────────────────────────────────────────────
    count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    if count <= 10:
        expense_templates = {
            "STU001": [
                ("food", [88, 95, 72, 110, 65, 90]),
                ("transport", [32, 45, 28, 55, 38, 42]),
                ("books", [120, 0, 85, 0, 95, 45]),
                ("utilities", [298, 302, 295, 310, 288, 305]),
                ("entertainment", [55, 30, 80, 45, 60, 25]),
            ],
            "STU002": [
                ("food", [75, 82, 68, 90, 71, 85]),
                ("transport", [40, 55, 35, 60, 45, 50]),
                ("books", [150, 0, 95, 30, 110, 0]),
                ("utilities", [275, 280, 270, 290, 268, 282]),
                ("entertainment", [40, 25, 60, 35, 45, 20]),
            ],
            "STU003": [
                ("food", [100, 110, 88, 120, 95, 105]),
                ("transport", [28, 35, 22, 40, 30, 32]),
                ("books", [80, 0, 60, 40, 70, 0]),
                ("utilities", [315, 320, 308, 330, 298, 322]),
                ("entertainment", [70, 45, 90, 55, 75, 30]),
            ],
        }
        base_month = date(2026, 5, 1)
        for stu, templates in expense_templates.items():
            for month_offset in range(6):
                raw_month = base_month.month + month_offset
                if raw_month > 12:
                    month_start = date(base_month.year + 1, raw_month - 12, 1)
                else:
                    month_start = date(base_month.year, raw_month, 1)
                for cat, amounts in templates:
                    amt = amounts[month_offset]
                    if amt == 0:
                        continue
                    day = min(month_start.day + (hash(f"{stu}{cat}{month_offset}") % 20), 28)
                    ts = f"{month_start.year}-{month_start.month:02d}-{day:02d}T12:00:00Z"
                    conn.execute(
                        "INSERT INTO expenses (student_id, amount_cny, category, note, timestamp) VALUES (?,?,?,?,?)",
                        (stu, amt, cat, f"{cat.title()} - auto", ts)
                    )
        conn.commit()

    # ── 2. FX history (30 days) ──────────────────────────────────────────────
    fx_count = conn.execute("SELECT COUNT(*) FROM fx_history").fetchone()[0]
    if fx_count == 0:
        pairs = [
            ("BDT", "CNY", 0.0651, 0.0003),
            ("PKR", "CNY", 0.0270, 0.0002),
            ("NGN", "CNY", 0.00480, 0.00005),
        ]
        start = date(2026, 9, 16)
        for i in range(30):
            d = start + timedelta(days=i)
            for fc, tc, base, noise in pairs:
                # Deterministic pseudo-variation
                variation = noise * math.sin(i * 0.4 + hash(fc) % 10)
                rate = round(base + variation, 6)
                conn.execute(
                    "INSERT INTO fx_history (date, from_currency, to_currency, rate) VALUES (?,?,?,?)",
                    (d.isoformat(), fc, tc, rate)
                )
        conn.commit()

    # ── 3. Credit history (6 months) ─────────────────────────────────────────
    ch_count = conn.execute("SELECT COUNT(*) FROM credit_history").fetchone()[0]
    if ch_count == 0:
        credit_journeys = {
            "STU001": [645, 651, 658, 664, 671, 680],
            "STU002": [598, 603, 608, 612, 616, 620],
            "STU003": [570, 574, 578, 582, 586, 590],
        }
        months = ["2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01", "2026-10-01"]
        for stu, scores in credit_journeys.items():
            for month, score in zip(months, scores):
                conn.execute(
                    "INSERT INTO credit_history (student_id, date, score) VALUES (?,?,?)",
                    (stu, month, score)
                )
        conn.commit()


def seed_synthetic_transactions(conn: sqlite3.Connection) -> None:
    """Populate synthetic_transactions table from bundled CSV if missing or empty."""
    import os
    import pandas as pd

    has_table = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='synthetic_transactions'"
    ).fetchone()[0]
    if has_table:
        count = conn.execute("SELECT COUNT(*) FROM synthetic_transactions").fetchone()[0]
        if count > 0:
            return

    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "student_finance_transactions_5000.csv"
    )
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.to_sql("synthetic_transactions", conn, if_exists="replace", index=False)
        conn.commit()


