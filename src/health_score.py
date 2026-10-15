"""CrossPay Financial Health Score™ calculation engine."""
from src.db import get_db
from src.tools.fx import convert_amount


WEIGHTS = {
    "credit": 0.30,
    "spending_discipline": 0.25,
    "savings_rate": 0.25,
    "tuition_readiness": 0.20,
}

BANDS = [
    (91, "Excellent", "极佳"),
    (76, "Healthy", "健康"),
    (61, "Stable", "稳定"),
    (41, "At Risk", "有风险"),
    (0, "Critical", "危险"),
]


def _get_band(score: int) -> tuple[str, str]:
    for threshold, en, zh in BANDS:
        if score >= threshold:
            return en, zh
    return "Critical", "危险"


def calculate_health_score(student_id: str) -> dict:
    """Calculate the comprehensive CrossPay Financial Health Score™ (0-100)."""
    conn = get_db()
    
    # 1. Fetch student account
    acc = conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone()
    if not acc:
        conn.close()
        raise ValueError(f"Student {student_id} not found")
    
    balance_cny = acc["balance_cny"]
    balance_home = acc["balance_home"]
    home_currency = acc["home_currency"]
    tuition_amount = acc["tuition_amount_cny"]
    credit_score = acc["credit_score"]

    # 2. Credit component (300 to 850 range)
    comp_credit = int(max(0, min(100, (credit_score - 300) / (850 - 300) * 100)))

    # 3. Monthly expenses & budget
    rows = conn.execute(
        "SELECT SUM(amount_cny) as total FROM expenses WHERE student_id = ? AND timestamp LIKE '2026-10%'",
        (student_id,)
    ).fetchone()
    monthly_spend = rows["total"] if rows and rows["total"] else 0.0

    b_row = conn.execute(
        "SELECT SUM(limit_cny) as total FROM budgets WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    budget_total = b_row["total"] if b_row and b_row["total"] else 3000.0

    spend_ratio = monthly_spend / budget_total if budget_total > 0 else 1.0
    if spend_ratio <= 0.70:
        comp_spend = 100
    elif spend_ratio <= 0.85:
        comp_spend = 90
    elif spend_ratio <= 1.00:
        comp_spend = 80
    elif spend_ratio <= 1.15:
        comp_spend = 60
    elif spend_ratio <= 1.30:
        comp_spend = 40
    else:
        comp_spend = 20

    # 4. Savings rate / buffer
    burn_rate = max(monthly_spend, 800.0)
    months_buffer = balance_cny / burn_rate
    if months_buffer >= 3.5:
        comp_save = 100
    elif months_buffer >= 2.5:
        comp_save = 85
    elif months_buffer >= 1.5:
        comp_save = 70
    elif months_buffer >= 1.0:
        comp_save = 55
    elif months_buffer >= 0.5:
        comp_save = 40
    else:
        comp_save = 20

    # 5. Tuition readiness
    try:
        conv = convert_amount(balance_home, home_currency, "CNY")
        home_cny = conv["converted"]
    except Exception:
        home_cny = 0.0

    total_liquidity = balance_cny + home_cny
    if tuition_amount <= 0:
        comp_tuition = 100
    else:
        coverage = total_liquidity / tuition_amount
        if coverage >= 1.20:
            comp_tuition = 100
        elif coverage >= 1.00:
            comp_tuition = 90
        elif coverage >= 0.80:
            comp_tuition = 75
        elif coverage >= 0.50:
            comp_tuition = 50
        else:
            comp_tuition = 30

    conn.close()

    # Composite weighted score
    raw_score = (
        comp_credit * WEIGHTS["credit"] +
        comp_spend * WEIGHTS["spending_discipline"] +
        comp_save * WEIGHTS["savings_rate"] +
        comp_tuition * WEIGHTS["tuition_readiness"]
    )
    score = int(round(raw_score))
    score = max(0, min(100, score))
    band, band_zh = _get_band(score)

    # Actionable insights
    insights = []
    insights_zh = []
    if comp_credit < 70:
        insights.append(f"Credit score ({credit_score}) has room for improvement. Consider a secured credit card.")
        insights_zh.append(f"信用分数 ({credit_score}) 仍有提升空间，建议申请保证金信用卡建立信用历史。")
    if comp_spend < 70:
        insights.append("Monthly spending exceeds 85% of budget. Review discretionary spending.")
        insights_zh.append("本月支出已超过预算的85%，建议优化非必要开支。")
    if comp_tuition < 80:
        insights.append(f"Tuition readiness is low ({coverage*100:.0f}% covered). Plan remittance from home.")
        insights_zh.append(f"学费储备不足（目前覆盖率 {coverage*100:.0f}%），建议提前规划境外汇款。")
    if comp_save >= 85:
        insights.append("Strong emergency cash reserve maintained.")
        insights_zh.append("应急资金储备充足，财务抗风险能力强。")

    if not insights:
        insights.append("All financial indicators are in optimal balance.")
        insights_zh.append("各项财务指标均处于良好均衡状态。")

    return {
        "student_id": student_id,
        "score": score,
        "band": band,
        "band_zh": band_zh,
        "components": {
            "credit": comp_credit,
            "spending_discipline": comp_spend,
            "savings_rate": comp_save,
            "tuition_readiness": comp_tuition,
        },
        "weights": WEIGHTS,
        "insights": insights,
        "insights_zh": insights_zh,
    }
