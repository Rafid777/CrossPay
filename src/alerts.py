"""Proactive smart alerts engine for CrossPay."""
from datetime import date, datetime
from src.db import get_db


def get_active_alerts(student_id: str) -> list[dict]:
    """Generate dynamic, intelligent financial alerts for the student."""
    conn = get_db()
    acc = conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone()
    if not acc:
        conn.close()
        return []

    balance_cny = acc["balance_cny"]
    tuition_amount = acc["tuition_amount_cny"]
    due_date_str = acc["tuition_due_date"]
    credit_score = acc["credit_score"]
    home_currency = acc["home_currency"]

    alerts = []

    # 1. Tuition deadline countdown
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str)
            days_left = (due_date - date.today()).days
            if days_left <= 7:
                alerts.append({
                    "alert_type": "tuition_deadline",
                    "severity": "critical",
                    "icon": "🚨",
                    "title": "Tuition Due Imminently",
                    "title_zh": "学费截止日迫近",
                    "message": f"Tuition payment of ¥{tuition_amount:,.0f} is due in {days_left} day(s) on {due_date_str}!",
                    "message_zh": f"学费 ¥{tuition_amount:,.0f} 将于 {days_left} 天后 ({due_date_str}) 到期，请尽快缴纳！",
                    "action_prompt": "Help me schedule my tuition payment now.",
                })
            elif days_left <= 30:
                alerts.append({
                    "alert_type": "tuition_countdown",
                    "severity": "warning",
                    "icon": "📅",
                    "title": "Upcoming Tuition Deadline",
                    "title_zh": "学费缴纳提醒",
                    "message": f"Tuition payment of ¥{tuition_amount:,.0f} due in {days_left} days ({due_date_str}). Plan your transfer window.",
                    "message_zh": f"学费 ¥{tuition_amount:,.0f} 距到期还有 {days_left} 天 ({due_date_str})，建议提前规划汇款窗口。",
                    "action_prompt": "What is the optimal window to pay my tuition?",
                })
        except Exception:
            pass

    # 2. Low CNY balance alert
    if balance_cny < 800:
        alerts.append({
            "alert_type": "low_balance",
            "severity": "critical",
            "icon": "⚠️",
            "title": "Low CNY Balance",
            "title_zh": "人民币余额偏低",
            "message": f"Current balance is only ¥{balance_cny:,.2f}. Consider converting funds from your {home_currency} account.",
            "message_zh": f"当前人民币余额仅剩 ¥{balance_cny:,.2f}，建议及时从 {home_currency} 账户结汇补充。",
            "action_prompt": f"How much does it cost to convert {home_currency} to CNY?",
        })
    elif balance_cny < 2500:
        alerts.append({
            "alert_type": "moderate_balance",
            "severity": "info",
            "icon": "ℹ️",
            "title": "Balance Notice",
            "title_zh": "余额变动提醒",
            "message": f"Current balance is ¥{balance_cny:,.2f}. Estimated ~3 weeks of average student living expenses remaining.",
            "message_zh": f"当前余额 ¥{balance_cny:,.2f}，按平均生活水平预计还可持续约3周。",
            "action_prompt": "Show my budget and spending summary for this month.",
        })

    # 3. FX Market Opportunity alert
    fx_row = conn.execute(
        "SELECT rate FROM fx_history WHERE from_currency = ? ORDER BY date DESC LIMIT 2",
        (home_currency,)
    ).fetchall()
    if len(fx_row) >= 2:
        latest = fx_row[0]["rate"]
        prev = fx_row[1]["rate"]
        if latest >= prev:
            alerts.append({
                "alert_type": "fx_opportunity",
                "severity": "success",
                "icon": "💹",
                "title": f"Favorable {home_currency}/CNY Rate",
                "title_zh": f"{home_currency}/CNY 汇率优势提醒",
                "message": f"{home_currency} is trending stronger against CNY (current: {latest:.4f}). Excellent window for tuition remittance.",
                "message_zh": f"{home_currency} 对人民币汇率走高（现价: {latest:.4f}），是汇入中国资金的有利窗口。",
                "action_prompt": f"Compare remittance providers for {home_currency} to China.",
            })

    # 4. Credit Score Growth milestone
    next_milestone = 740 if credit_score >= 670 else 670 if credit_score >= 580 else 580
    diff = next_milestone - credit_score
    if diff > 0:
        alerts.append({
            "alert_type": "credit_growth",
            "severity": "info",
            "icon": "💳",
            "title": "Credit Score Milestone",
            "title_zh": "信用提升目标",
            "message": f"You are {diff} points away from the '{next_milestone}' tier! On-time utility payments boost your score.",
            "message_zh": f"距离下一个信用评级（{next_milestone}分）仅差 {diff} 分！按时缴纳水电费可稳步提升信用分。",
            "action_prompt": "How can I build my credit score in China?",
        })

    conn.close()
    return alerts
