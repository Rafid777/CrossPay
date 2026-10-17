"""Analytics tools for FX, spending history, and credit progression."""
from src.db import get_db


def get_fx_trend(from_currency: str, to_currency: str = "CNY", days: int = 30) -> list[dict]:
    """Get historical FX rates over the last N days."""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, rate FROM fx_history "
        "WHERE from_currency = ? AND to_currency = ? "
        "ORDER BY date ASC LIMIT ?",
        (from_currency.upper(), to_currency.upper(), days)
    ).fetchall()
    conn.close()
    return [{"date": r["date"], "rate": r["rate"]} for r in rows]


def get_spending_trend(student_id: str, months: int = 6) -> list[dict]:
    """Get 6-month monthly spending trend by category."""
    conn = get_db()
    rows = conn.execute(
        "SELECT SUBSTR(timestamp, 1, 7) as month, category, SUM(amount_cny) as total "
        "FROM expenses WHERE student_id = ? "
        "GROUP BY month, category ORDER BY month ASC",
        (student_id,)
    ).fetchall()
    conn.close()

    # Aggregate by month
    month_map = {}
    for r in rows:
        m = r["month"]
        if m not in month_map:
            month_map[m] = {"month": m, "total": 0.0, "categories": {}}
        cat = r["category"]
        amt = round(r["total"], 2)
        month_map[m]["categories"][cat] = amt
        month_map[m]["total"] = round(month_map[m]["total"] + amt, 2)

    return list(month_map.values())


def get_credit_trend(student_id: str) -> list[dict]:
    """Get credit score progression history."""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, score FROM credit_history "
        "WHERE student_id = ? ORDER BY date ASC",
        (student_id,)
    ).fetchall()
    conn.close()
    return [{"date": r["date"], "score": r["score"]} for r in rows]


def get_worldbank_remittance(country: str, flow: str = "outflow", year: int = 2023) -> dict:
    """Get World Bank official remittance data for a country and year.

    Args:
        country: Country name (e.g. "Bangladesh", "Pakistan", "Nigeria")
        flow: "outflow" (money sent abroad) or "inflow" (money received)
        year: Year between 2000 and 2024
    """
    import os
    import pandas as pd

    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
    )
    fname = "worldbank_outflows_clean.csv" if flow == "outflow" else "worldbank_inflows_clean.csv"
    path = os.path.join(data_dir, fname)
    if not os.path.exists(path):
        return {"error": "World Bank data file not found", "country": country}

    df = pd.read_csv(path)
    row = df[df["country"].str.lower() == country.lower()]
    if row.empty:
        row = df[df["country"].str.lower().str.contains(country.lower(), na=False)]
    if row.empty:
        return {"error": f"Country '{country}' not found in World Bank dataset"}

    row = row.iloc[0]
    year_str = str(year)
    amount = row.get(year_str, row.get(year, None))
    if amount is None:
        return {"error": f"Year {year} not available", "country": country}

    amount = float(amount) if not pd.isna(amount) else 0.0
    prev_year = year - 5
    prev_amount = row.get(str(prev_year), row.get(prev_year, None))
    cagr = None
    if prev_amount is not None and not pd.isna(prev_amount) and float(prev_amount) > 0 and amount > 0:
        cagr = round(((amount / float(prev_amount)) ** (1 / 5) - 1) * 100, 2)

    return {
        "country": str(row["country"]),
        "year": year,
        "flow_type": flow,
        "amount_usd_million": round(amount, 2),
        "5yr_cagr_pct": cagr,
        "source": "World Bank Group — Migration & Remittances Data (official)",
    }


def detect_spending_anomalies(student_id: str, threshold_iqr: float = 1.5) -> dict:
    """
    Empirical Anomaly Detection using Interquartile Range (IQR) on student transactions.
    Identifies abnormal spikes in expenses or suspicious transfer volumes.
    """
    import numpy as np
    conn = get_db()
    # Check if synthetic_transactions table has user data
    has_synth = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='synthetic_transactions'"
    ).fetchone()[0]
    
    txns = []
    if has_synth:
        rows = conn.execute(
            "SELECT transaction_id, date, type, amount, currency, channel, status "
            "FROM synthetic_transactions WHERE user_id = ? ORDER BY date DESC",
            (student_id,)
        ).fetchall()
        txns = [dict(r) for r in rows]
    
    # Fallback to expenses table if no synthetic records
    if not txns:
        rows = conn.execute(
            "SELECT id as transaction_id, timestamp as date, category as type, amount_cny as amount, "
            "'CNY' as currency, 'Local Expense' as channel, 'Completed' as status "
            "FROM expenses WHERE student_id = ? ORDER BY timestamp DESC",
            (student_id,)
        ).fetchall()
        txns = [dict(r) for r in rows]
    conn.close()

    if not txns:
        return {
            "student_id": student_id,
            "status": "INSUFFICIENT_DATA",
            "message": "No transaction history found to perform statistical anomaly detection.",
            "total_transactions_analyzed": 0,
            "anomaly_count": 0,
            "anomalies_detected": [],
        }

    # Group amounts by category/type
    amounts_by_type = {}
    for t in txns:
        t_type = t["type"]
        amounts_by_type.setdefault(t_type, []).append(float(t["amount"]))

    anomalies = []
    for t_type, vals in amounts_by_type.items():
        if len(vals) < 3:
            continue
        q75, q25 = np.percentile(vals, [75, 25])
        iqr = q75 - q25
        cutoff = q75 + (threshold_iqr * iqr) if iqr > 0 else q75 * 1.5
        
        for t in txns:
            if t["type"] == t_type and float(t["amount"]) > cutoff:
                anomalies.append({
                    "transaction_id": t["transaction_id"],
                    "date": t["date"],
                    "type": t_type,
                    "amount": t["amount"],
                    "currency": t["currency"],
                    "channel": t["channel"],
                    "iqr_upper_cutoff": round(cutoff, 2),
                    "deviation_ratio": round(float(t["amount"]) / cutoff, 2),
                    "reason": f"Amount {t['amount']} {t['currency']} exceeds category upper threshold ({cutoff:.2f})",
                })

    return {
        "student_id": student_id,
        "status": "ANOMALIES_FLAGGED" if anomalies else "CLEAN_NO_ANOMALIES",
        "total_transactions_analyzed": len(txns),
        "anomaly_count": len(anomalies),
        "anomalies_detected": anomalies,
        "detection_method": f"Tukey's IQR Outlier Filter ({threshold_iqr}x IQR)",
    }


def get_cohort_spending_benchmarks(study_country: str = "China") -> dict:
    """
    Calculate empirical cohort spending benchmarks from the 5,000 international student transactions.
    Allows students to benchmark their monthly budgets against actual peers in their destination.
    """
    import numpy as np
    conn = get_db()
    has_synth = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='synthetic_transactions'"
    ).fetchone()[0]
    if not has_synth:
        conn.close()
        return {
            "study_country": study_country,
            "status": "NO_DATA",
            "total_transactions_sampled": 0,
            "message": "No synthetic transaction table found.",
        }

    rows = conn.execute(
        "SELECT type, amount, currency, channel, status FROM synthetic_transactions "
        "WHERE study_country = ?",
        (study_country,)
    ).fetchall()
    conn.close()

    if not rows:
        return {
            "study_country": study_country,
            "status": "NO_DATA",
            "total_transactions_sampled": 0,
            "message": f"No peer transaction data found for destination country: {study_country}",
        }

    living_expenses = [r["amount"] for r in rows if r["type"] == "Living Expense"]
    tuition_payments = [r["amount"] for r in rows if r["type"] == "Tuition Payment"]
    
    # Channel distribution
    channels = {}
    completed_count = 0
    for r in rows:
        ch = r["channel"]
        channels[ch] = channels.get(ch, 0) + 1
        if r["status"] == "Completed":
            completed_count += 1

    sorted_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)
    top_channels = [ch for ch, _ in sorted_channels[:4]]

    median_living = float(np.median(living_expenses)) if living_expenses else 0.0
    median_tuition = float(np.median(tuition_payments)) if tuition_payments else 0.0
    completion_rate = round((completed_count / len(rows)) * 100, 2) if rows else 0.0

    return {
        "study_country": study_country,
        "total_transactions_sampled": len(rows),
        "median_living_expense": round(median_living, 2),
        "median_tuition_payment": round(median_tuition, 2),
        "popular_channels": top_channels,
        "completion_rate_pct": completion_rate,
        "benchmark_source": "CrossPay International Student Synthetic Cohort (5,000 Transactions)",
    }

