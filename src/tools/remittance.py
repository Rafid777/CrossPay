from datetime import datetime, timedelta, timezone

_PROVIDERS = [
    {"name": "SWIFT Bank Transfer", "fee_usd": 25.0, "fx_markup_pct": 0.025, "delivery_days": 3},
    {"name": "WeBank Direct", "fee_usd": 5.0, "fx_markup_pct": 0.008, "delivery_days": 1},
    {"name": "Wise", "fee_usd": 4.2, "fx_markup_pct": 0.004, "delivery_days": 1},
    {"name": "UnionPay Cross-border", "fee_usd": 8.0, "fx_markup_pct": 0.006, "delivery_days": 2},
]


def compare_remittance_options(amount_usd: float, destination_country: str) -> list:
    """Compare remittance providers sorted by total cost (cheapest first)."""
    if amount_usd <= 0:
        raise ValueError("Transfer amount must be greater than zero.")
    options = []
    for p in _PROVIDERS:
        fx_cost = amount_usd * p["fx_markup_pct"]
        total_cost = p["fee_usd"] + fx_cost
        options.append({
            "provider": p["name"],
            "fee_usd": round(p["fee_usd"], 2),
            "fx_markup_pct": p["fx_markup_pct"] * 100,
            "fx_cost_usd": round(fx_cost, 2),
            "total_cost_usd": round(total_cost, 2),
            "delivery_days": p["delivery_days"],
            "recommended": False,
            "destination": destination_country,
        })
    options.sort(key=lambda x: x["total_cost_usd"])
    options[0]["recommended"] = True
    return options


def schedule_tuition_payment(student_id: str, amount_cny: float, due_date: str) -> dict:
    """Suggest optimal window to schedule a tuition payment."""
    if amount_cny <= 0:
        raise ValueError("Tuition amount must be greater than zero.")
    # Optimal window: next Monday (FX typically better at start of week)
    today = datetime.now(timezone.utc).date()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    optimal_date = today + timedelta(days=days_until_monday)
    return {
        "student_id": student_id,
        "amount_cny": amount_cny,
        "due_date": due_date,
        "optimal_window": optimal_date.isoformat(),
        "projected_rate": 7.31,  # slightly better than today 7.28
        "estimated_savings_usd": round(amount_cny / 7.28 * 0.003, 2),
        "confirmation_required": True,
        "note": "FX rates are typically 0.3% better at the start of the trading week.",
    }
