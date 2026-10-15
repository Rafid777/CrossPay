from src.db import get_db

_TIERS = [
    (800, "Exceptional"),
    (740, "Very Good"),
    (670, "Good"),
    (580, "Fair"),
    (0, "Poor"),
]

_TIPS = [
    "Open a secured credit card with a small deposit — it builds history without risk",
    "Always pay your tuition and rent on time — payment history is 35% of your score",
    "Keep credit utilization below 30% of your credit limit",
    "Ask a trusted friend/family to add you as an authorized user on their card",
    "Sign up for rent-reporting services to get credit for rent payments",
    "Avoid applying for multiple cards at once — each hard inquiry costs 5-10 points",
    "Set up autopay for minimum payments to avoid missed payments",
]

_SCORE_ACTIONS = {
    "open_secured_card": {"change": 25, "months": 6},
    "pay_on_time_3mo": {"change": 15, "months": 3},
    "pay_tuition_early": {"change": 8, "months": 1},
    "reduce_utilization": {"change": 20, "months": 1},
    "become_authorized_user": {"change": 30, "months": 2},
    "report_rent_payments": {"change": 12, "months": 3},
}


def _get_tier(score: int) -> tuple:
    for threshold, name in _TIERS:
        if score >= threshold:
            return name, threshold
    return "Poor", 0


def get_credit_profile(student_id: str) -> dict:
    """Get credit profile for a student."""
    conn = get_db()
    row = conn.execute("SELECT credit_score FROM accounts WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    score = row["credit_score"] if row else 650
    tier, threshold = _get_tier(score)
    # Find next milestone above current score
    next_threshold = next((t for t, _ in _TIERS if t > score), 850)
    return {
        "student_id": student_id,
        "score": score,
        "tier": tier,
        "tips": _TIPS[:5],
        "next_milestone": next_threshold,
        "points_to_next": next_threshold - score,
    }


def simulate_credit_action(action: str, student_id: str) -> dict:
    """Simulate the impact of a credit-building action."""
    conn = get_db()
    row = conn.execute("SELECT credit_score FROM accounts WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    current_score = row["credit_score"] if row else 650
    effect = _SCORE_ACTIONS.get(action, {"change": 10, "months": 3})
    new_score = min(850, current_score + effect["change"])
    return {
        "action": action,
        "current_score": current_score,
        "projected_score_change": effect["change"],
        "new_score": new_score,
        "timeline_months": effect["months"],
        "note": f"Expected +{effect['change']} points in {effect['months']} month(s)",
    }
