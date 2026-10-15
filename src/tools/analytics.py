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
