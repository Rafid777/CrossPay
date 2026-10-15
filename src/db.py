import sqlite3
import os

CREATE_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    home_currency TEXT NOT NULL,
    home_country TEXT NOT NULL,
    host_country TEXT NOT NULL DEFAULT 'CN',
    host_currency TEXT NOT NULL DEFAULT 'CNY',
    balance_home REAL DEFAULT 0.0,
    balance_cny REAL DEFAULT 0.0,
    tuition_due_date TEXT,
    tuition_amount_cny REAL DEFAULT 0.0,
    credit_score INTEGER DEFAULT 650,
    passport_number TEXT,
    bank_account TEXT
)
"""

CREATE_EXPENSES = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    amount_cny REAL NOT NULL,
    category TEXT NOT NULL,
    note TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES accounts(id)
)
"""

CREATE_BUDGETS = """
CREATE TABLE IF NOT EXISTS budgets (
    student_id TEXT NOT NULL,
    category TEXT NOT NULL,
    limit_cny REAL NOT NULL,
    PRIMARY KEY (student_id, category),
    FOREIGN KEY(student_id) REFERENCES accounts(id)
)
"""

CREATE_FX_HISTORY = """
CREATE TABLE IF NOT EXISTS fx_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    from_currency TEXT NOT NULL,
    to_currency TEXT NOT NULL,
    rate REAL NOT NULL
)
"""

CREATE_ALERTS = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    message_zh TEXT NOT NULL,
    severity TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES accounts(id)
)
"""

CREATE_CREDIT_HISTORY = """
CREATE TABLE IF NOT EXISTS credit_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    date TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES accounts(id)
)
"""


def get_db(path: str = "data/crosspay.db") -> sqlite3.Connection:
    if path != ":memory:":
        os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(CREATE_ACCOUNTS)
    conn.execute(CREATE_EXPENSES)
    conn.execute(CREATE_BUDGETS)
    conn.execute(CREATE_FX_HISTORY)
    conn.execute(CREATE_ALERTS)
    conn.execute(CREATE_CREDIT_HISTORY)
    conn.commit()
    return conn
