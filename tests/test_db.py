from src.db import get_db
from src.mock_data import seed_mock_data


def test_db_creates_accounts_table():
    conn = get_db(":memory:")
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
    assert cur.fetchone() is not None


def test_mock_data_seeds_three_accounts():
    conn = get_db(":memory:")
    seed_mock_data(conn)
    count = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    assert count == 3


def test_passport_never_stored_plaintext():
    conn = get_db(":memory:")
    seed_mock_data(conn)
    rows = conn.execute("SELECT passport_number FROM accounts").fetchall()
    for row in rows:
        assert "****" in row[0], f"Passport not masked: {row[0]}"


def test_foreign_keys_enforced():
    import sqlite3
    import pytest
    conn = get_db(":memory:")
    # Attempting to insert an expense for a non-existent student must raise IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (student_id, amount_cny, category, note, timestamp) VALUES (?, ?, ?, ?, ?)",
            ("NON_EXISTENT_STU", 50.0, "food", "lunch", "2026-10-17T00:00:00Z")
        )

