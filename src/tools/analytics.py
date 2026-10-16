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
