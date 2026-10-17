"""Page 1: Financial Health Dashboard (财务总览仪表盘)."""
import os
import streamlit as st
from datetime import date
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.health_score import calculate_health_score
from src.alerts import get_active_alerts
from src.tools.analytics import get_credit_trend
from src.charts import create_health_gauge, create_spending_donut
from src.pdf_report import generate_pdf_report
from src.theme import load_css, render_hero, render_kpi_card, render_alert, render_compliance_footer
from src.i18n import t, get_current_lang

load_dotenv()

st.set_page_config(
    page_title="CrossPay — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# Initialize DB and Session
if "db_seeded" not in st.session_state:
    conn = get_db()
    seed_mock_data(conn)
    conn.close()
    st.session_state.db_seeded = True

if "student_id" not in st.session_state:
    st.session_state.student_id = os.getenv("STUDENT_ID", "STU001")

if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Sidebar controls
with st.sidebar:
    st.markdown("### 🏦 **CrossPay**")
    st.caption("WeBank AI Finance Challenge · Topic C")
    st.divider()

    # Language Switcher
    lang_choice = st.radio(
        "🌐 Language / 语言",
        options=["English", "简体中文"],
        index=0 if st.session_state.lang == "en" else 1,
        horizontal=True,
    )
    st.session_state.lang = "zh" if lang_choice == "简体中文" else "en"
    lang = st.session_state.lang

    st.divider()

    # Student selector
    student_labels = {
        "STU001": "Rafi Ahmed (🇧🇩 BD → 🇨🇳 CN)",
        "STU002": "Ayesha Khan (🇵🇰 PK → 🇨🇳 CN)",
        "STU003": "Emeka Okafor (🇳🇬 NG → 🇨🇳 CN)",
    }
    selected_stu = st.selectbox(
        t("select_student", lang),
        options=list(student_labels.keys()),
        format_func=lambda x: student_labels[x],
        index=list(student_labels.keys()).index(st.session_state.student_id),
    )
    if selected_stu != st.session_state.student_id:
        st.session_state.student_id = selected_stu
        st.session_state.agent = None
        st.session_state.messages = []
        st.rerun()

student_id = st.session_state.student_id
lang = st.session_state.lang

# Fetch student and health data
conn = get_db()
account = dict(conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone())
conn.close()

health = calculate_health_score(student_id)
alerts = get_active_alerts(student_id)

# ── Hero Banner ──────────────────────────────────────────────────────────────
student_name = account.get("name", "Student")
origin = account.get("home_country", "")
curr = account.get("home_currency", "")
hero_title = f"CrossPay {t('nav_dashboard', lang)} · {student_name}"
hero_sub = (
    f"留学生身份: {origin} → 中国 · 结算本币: {curr} · 微众国际数字金融核心"
    if lang == "zh"
    else f"International Student: {origin} → China · Base Currency: {curr} · Powered by WeBank Core"
)
render_hero(hero_title, hero_sub)

# ── 4 KPI Metric Cards ───────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

# 1. Balance
balance_cny = account.get("balance_cny", 0.0)
balance_home = account.get("balance_home", 0.0)
with col1:
    render_kpi_card(
        title=t("kpi_balance", lang),
        value=f"¥ {balance_cny:,.2f}",
        subtitle=f"{t('home_reserve', lang)}: {balance_home:,.0f} {curr}",
        badge="Active" if lang == "en" else "正常",
        badge_type="healthy",
    )

# 2. Tuition
tuition_cny = account.get("tuition_amount_cny", 0.0)
due_date_str = account.get("tuition_due_date", "")
days_left = 0
if due_date_str:
    try:
        days_left = (date.fromisoformat(due_date_str) - date.today()).days
    except Exception:
        pass

with col2:
    badge_type = "critical" if days_left <= 7 else "stable" if days_left <= 30 else "healthy"
    render_kpi_card(
        title=t("kpi_tuition", lang),
        value=f"¥ {tuition_cny:,.0f}",
        subtitle=f"{due_date_str} ({days_left} {t('tuition_countdown', lang)})",
        badge=f"{days_left}d left" if lang == "en" else f"剩余{days_left}天",
        badge_type=badge_type,
    )

# 3. Credit Score
credit_score = account.get("credit_score", 650)
tier = "Good" if credit_score >= 670 else "Fair" if credit_score >= 580 else "Poor"
tier_zh = "良好" if credit_score >= 670 else "一般" if credit_score >= 580 else "欠佳"
with col3:
    render_kpi_card(
        title=t("kpi_credit", lang),
        value=str(credit_score),
        subtitle=f"Next Milestone: {740 if credit_score >= 670 else 670}" if lang == "en" else f"下阶段评级目标: {740 if credit_score >= 670 else 670}",
        badge=tier if lang == "en" else tier_zh,
        badge_type="healthy" if credit_score >= 670 else "stable",
    )

# 4. Health Score
h_score = health.get("score", 0)
h_band = health.get("band", "Stable")
h_band_zh = health.get("band_zh", "稳定")
with col4:
    badge_type = "excellent" if h_score >= 90 else "healthy" if h_score >= 76 else "stable" if h_score >= 60 else "critical"
    render_kpi_card(
        title=t("kpi_health", lang),
        value=f"{h_score} / 100",
        subtitle=t("health_desc", lang),
        badge=h_band if lang == "en" else h_band_zh,
        badge_type=badge_type,
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ── Main Two-Column Layout ───────────────────────────────────────────────────
left_col, right_col = st.columns([7, 5])

with left_col:
    st.markdown(f"#### ⚡ {'智能风控与即时提醒' if lang == 'zh' else 'Smart Proactive Financial Alerts'}")
    if alerts:
        for alert in alerts:
            render_alert(alert, lang=lang)
    else:
        st.info("✅ All financial metrics within safe parameters.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Spending Donut Preview
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount_cny) as total FROM expenses "
        "WHERE student_id = ? AND timestamp LIKE '2026-10%' GROUP BY category",
        (student_id,)
    ).fetchall()
    conn.close()
    cat_dict = {r["category"]: r["total"] for r in rows}
    if cat_dict:
        fig_donut = create_spending_donut(cat_dict, lang=lang)
        st.plotly_chart(fig_donut, use_container_width=True)

    # PDF Export Section
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(f"#### 📑 {'审计级财务报告导出' if lang == 'zh' else 'Download Audit Financial Report'}")
    st.caption("One-click regulatory compliant PDF report for scholarship, visa, and parental assurance.")
    
    total_spend = sum(cat_dict.values())
    spending_summary = {
        "categories": cat_dict,
        "total_cny": total_spend,
        "vs_budget_pct": round((total_spend / 3000.0) * 100, 1),
    }
    credit_hist = get_credit_trend(student_id)

    pdf_bytes = generate_pdf_report(
        student_data=account,
        health_data=health,
        alerts=alerts,
        spending=spending_summary,
        credit_history=credit_hist,
    )
    
    st.download_button(
        label=t("export_pdf", lang),
        data=pdf_bytes,
        file_name=f"CrossPay_Report_{student_id}_{date.today().isoformat()}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

with right_col:
    st.markdown(f"#### 🛡️ {'财务健康评估模型' if lang == 'zh' else 'Proprietary Health Architecture'}")
    gauge_fig = create_health_gauge(h_score, band=h_band, lang=lang)
    st.plotly_chart(gauge_fig, use_container_width=True)

    # Component Breakdown Bars
    st.markdown(f"##### 📊 {'评估因子加权得分' if lang == 'zh' else 'Component Score Breakdown'}")
    comps = health.get("components", {})
    
    comp_labels = [
        (t("credit_comp", lang), comps.get("credit", 0)),
        (t("spend_comp", lang), comps.get("spending_discipline", 0)),
        (t("save_comp", lang), comps.get("savings_rate", 0)),
        (t("tuition_comp", lang), comps.get("tuition_readiness", 0)),
    ]
    for lbl, val in comp_labels:
        col_lbl, col_val = st.columns([3, 1])
        col_lbl.caption(lbl)
        col_val.caption(f"**{val}/100**")
        st.progress(val / 100.0)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(f"##### 💡 {'AI 智能财务优化建议' if lang == 'zh' else 'AI Actionable Financial Insights'}")
    insights = health.get("insights_zh" if lang == "zh" else "insights", [])
    for ins in insights:
        st.markdown(f"- {ins}")

    # Anti-Fraud & Risk Status Card
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(f"##### 🛡️ {'智能反诈与风控状态' if lang == 'zh' else 'Anti-Fraud & Risk Defense Status'}")
    af_title = "国家反诈中心重点保护中" if lang == "zh" else "Protected by National Anti-Fraud Baseline"
    af_badge = "🟢 正常受控 (LOW RISK)" if lang == "zh" else "🟢 ACTIVE / LOW RISK"
    af_l1 = "• 《反电信网络诈骗法》实时监控已启用" if lang == "zh" else "• PRC Anti-Telecom Fraud Law Monitoring: ACTIVE"
    af_l2 = "• “断卡行动”地下钱庄私自换汇拦截已生效" if lang == "zh" else "• 'Card Break Action' Underground FX Interception: ACTIVE"
    af_l3 = "• 学费代缴骗局（盗卡代充）特征库已同步" if lang == "zh" else "• Tuition Proxy Payment Scam Heuristics: SYNCHRONIZED"
    af_hotline = "全国反诈劝阻预警专线: " if lang == "zh" else "China Anti-Fraud Emergency Hotline: "
    
    st.markdown(
        f"""
        <div style="background: rgba(10, 36, 99, 0.05); border: 1px solid rgba(10, 36, 99, 0.15); border-radius: 10px; padding: 14px; margin-top: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; font-size: 13px; color: #0A2463;">{af_title}</span>
                <span style="background: #E8F5E9; color: #2E7D32; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 600;">{af_badge}</span>
            </div>
            <div style="font-size: 12px; color: #444; margin-top: 8px; line-height: 1.6;">
                {af_l1}<br/>
                {af_l2}<br/>
                {af_l3}
            </div>
            <div style="margin-top: 10px; font-size: 11px; color: #888;">
                {af_hotline}<b>96110</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
