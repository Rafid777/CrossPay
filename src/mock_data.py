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
