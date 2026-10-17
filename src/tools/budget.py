from datetime import datetime, timezone
from typing import Dict, Any, Optional
from src.db import get_db


def get_spending_summary(student_id: str, month: str) -> dict:
    """Get spending summary by category for a given month (YYYY-MM)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount_cny) as total FROM expenses "
        "WHERE student_id = ? AND timestamp LIKE ? GROUP BY category",
        (student_id, f"{month}%")
    ).fetchall()
    categories = {row["category"]: round(row["total"], 2) for row in rows}
    total_cny = sum(categories.values())
    # Get budget limits
    budgets = conn.execute(
        "SELECT category, limit_cny FROM budgets WHERE student_id = ?",
        (student_id,)
    ).fetchall()
    budget_total = sum(b["limit_cny"] for b in budgets) or 3000.0  # default 3000 CNY/month
    vs_budget_pct = round((total_cny / budget_total) * 100, 1) if budget_total else 0.0
    conn.close()
    return {
        "student_id": student_id,
        "month": month,
        "categories": categories,
        "total_cny": round(total_cny, 2),
        "budget_total_cny": round(budget_total, 2),
        "vs_budget_pct": vs_budget_pct,
    }


def set_budget_category(student_id: str, category: str, amount_cny: float) -> dict:
    """Preview setting a budget limit — requires confirmation before committing."""
    if amount_cny < 0:
        raise ValueError("Budget limit must be non-negative.")
    return {
        "student_id": student_id,
        "category": category,
        "new_limit_cny": amount_cny,
        "confirmation_required": True,
        "action": "set_budget_category",
    }


def commit_set_budget_category(student_id: str, category: str, amount_cny: float) -> dict:
    """Actually commits the budget update after user confirmation."""
    if amount_cny < 0:
        raise ValueError("Budget limit must be non-negative.")
    conn = get_db()
    conn.execute(
        "INSERT INTO budgets (student_id, category, limit_cny) VALUES (?, ?, ?) "
        "ON CONFLICT(student_id, category) DO UPDATE SET limit_cny=excluded.limit_cny",
        (student_id, category, amount_cny)
    )
    conn.commit()
    conn.close()
    return {"success": True, "category": category, "new_limit_cny": amount_cny}


def add_expense(student_id: str, amount_cny: float, category: str, note: str = "") -> dict:
    """Preview adding an expense — requires confirmation before committing."""
    if amount_cny <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    # Read current balance for preview
    conn = get_db()
    row = conn.execute("SELECT balance_cny FROM accounts WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    current = row["balance_cny"] if row else 0.0
    new_bal = round(current - amount_cny, 2)
    return {
        "student_id": student_id,
        "amount_cny": amount_cny,
        "category": category,
        "note": note,
        "recorded": False,
        "current_balance_cny": round(current, 2),
        "new_balance_cny": new_bal,
        "is_overdraft": new_bal < 0,
        "confirmation_required": True,
        "action": "add_expense",
    }


def commit_add_expense(student_id: str, amount_cny: float, category: str, note: str = "") -> dict:
    """Actually commits the expense after user confirmation."""
    if amount_cny <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    conn = get_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO expenses (student_id, amount_cny, category, note, timestamp) VALUES (?, ?, ?, ?, ?)",
        (student_id, amount_cny, category, note, timestamp)
    )
    conn.execute(
        "UPDATE accounts SET balance_cny = balance_cny - ? WHERE id = ?",
        (amount_cny, student_id)
    )
    conn.commit()
    row = conn.execute("SELECT balance_cny FROM accounts WHERE id = ?", (student_id,)).fetchone()
    new_balance = round(row["balance_cny"] if row else 0.0, 2)
    conn.close()
    return {
        "recorded": True,
        "new_balance_cny": new_balance,
        "is_overdraft": new_balance < 0,
    }
