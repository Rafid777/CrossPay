#!/usr/bin/env python
"""Synthetic Data Generator for CrossPay (WeBank Topic C).

Generates realistic large-scale cross-border student transactions (5,000+ records)
covering remittances, tuition payments, living expenses, and multi-currency exchanges
across mobile wallets, banks, and remittance corridors.

Usage:
    python scripts/generate_synthetic_transactions.py
"""
import os
import sys
import random
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from faker import Faker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.db import get_db

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_TRANSACTIONS = 5000
NUM_USERS = 200

study_countries = ["China", "Malaysia", "UK", "Canada", "Australia", "USA", "Germany", "Japan"]
currencies = {
    "China": "CNY",
    "Malaysia": "MYR",
    "UK": "GBP",
    "Canada": "CAD",
    "Australia": "AUD",
    "USA": "USD",
    "Germany": "EUR",
    "Japan": "JPY",
}

transaction_types = [
    "Remittance",
    "Tuition Payment",
    "Living Expense",
    "Multi-Currency Exchange",
    "Book & Supplies",
    "Medical",
    "Travel",
]
channels = [
    "WeBank Direct",
    "Alipay",
    "WeChat Pay",
    "bKash",
    "Nagad",
    "Bank Transfer",
    "Wise",
    "Western Union",
    "University Portal",
    "PayPal",
]

exchange_rates = {
    "BDT": 0.0085,
    "CNY": 0.14,
    "MYR": 0.23,
    "GBP": 1.30,
    "CAD": 0.75,
    "AUD": 0.67,
    "USD": 1.0,
    "EUR": 1.08,
    "JPY": 0.0067,
}


def generate_dataset():
    print(f"[CrossPay] Generating {NUM_TRANSACTIONS} synthetic student transactions...")
    os.makedirs("data", exist_ok=True)

    users = []
    # Weighted towards China for WeBank context
    countries_pool = ["China", "China", "China", "Malaysia", "UK", "Canada", "Australia", "USA", "Germany", "Japan"]
    student_home_countries = ["Bangladesh", "Pakistan", "Nigeria", "India", "Indonesia", "Vietnam"]

    for i in range(1, NUM_USERS + 1):
        study_country = random.choice(countries_pool)
        home_country = random.choice(student_home_countries)
        users.append({
            "user_id": f"STU{str(i).zfill(3)}",
            "user_name": fake.name(),
            "student_country": home_country,
            "study_country": study_country,
        })

    data = []
    start_date = datetime(2024, 1, 1)

    for i in range(1, NUM_TRANSACTIONS + 1):
        user = random.choice(users)
        study_country = user["study_country"]
        local_currency = currencies[study_country]

        txn_type = random.choices(
            transaction_types,
            weights=[0.35, 0.20, 0.25, 0.08, 0.05, 0.04, 0.03]
        )[0]

        if txn_type == "Remittance":
            amount = random.randint(40000, 300000)
            currency = "BDT"
            from_currency = "BDT"
            to_currency = local_currency
        elif txn_type == "Tuition Payment":
            if study_country in ["UK", "USA", "Australia", "Canada"]:
                amount = random.randint(3000, 12000)
            else:
                amount = random.randint(4000, 18000)
            currency = local_currency
            from_currency = local_currency
            to_currency = local_currency
        elif txn_type == "Living Expense":
            amount = random.randint(150, 800)
            currency = local_currency
            from_currency = local_currency
            to_currency = local_currency
        elif txn_type == "Multi-Currency Exchange":
            amount = random.randint(200, 2000)
            currency = local_currency
            from_currency = local_currency
            to_currency = random.choice(["USD", "EUR", "GBP", "CNY"])
        else:
            amount = random.randint(50, 500)
            currency = local_currency
            from_currency = local_currency
            to_currency = local_currency

        converted_usd = round(amount * exchange_rates.get(currency, 1.0), 2)
        random_days = random.randint(0, 650)
        txn_date = start_date + timedelta(days=random_days)

        data.append({
            "transaction_id": f"TXN{str(i).zfill(5)}",
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "student_country": user["student_country"],
            "study_country": study_country,
            "date": txn_date.strftime("%Y-%m-%d"),
            "type": txn_type,
            "amount": amount,
            "currency": currency,
            "converted_amount_usd": converted_usd,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "description": f"{txn_type} - {fake.sentence(nb_words=4)}",
            "status": random.choices(["Completed", "Pending", "Failed"], weights=[0.92, 0.05, 0.03])[0],
            "channel": random.choice(channels),
        })

    df = pd.DataFrame(data)
    df = df.sort_values("date").reset_index(drop=True)

    csv_path = os.path.join("data", "student_finance_transactions_5000.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV saved: {csv_path} ({len(df)} rows)")

    # Also sync into SQLite
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS synthetic_transactions (
        transaction_id TEXT PRIMARY KEY,
        user_id TEXT,
        user_name TEXT,
        student_country TEXT,
        study_country TEXT,
        date TEXT,
        type TEXT,
        amount REAL,
        currency TEXT,
        converted_amount_usd REAL,
        from_currency TEXT,
        to_currency TEXT,
        description TEXT,
        status TEXT,
        channel TEXT
    )
    """)
    df.to_sql("synthetic_transactions", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("✅ SQLite table `synthetic_transactions` populated successfully!")
    return df


if __name__ == "__main__":
    generate_dataset()
