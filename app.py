"""CrossPay — WeBank AI Financial Assistant for International Students (Topic C)."""
import os
import streamlit as st
from datetime import date
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.health_score import calculate_health_score
from src.alerts import get_active_alerts
from src.theme import load_css, render_hero, render_kpi_card, render_alert, render_compliance_footer
from src.i18n import t

load_dotenv()

st.set_page_config(
    page_title="CrossPay — WeBank AI Finance",
    page_icon="🏦",
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

# Sidebar
with st.sidebar:
    st.markdown("### 🏦 **CrossPay**")
    st.caption("WeBank International AI Finance Challenge · Topic C")
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
        st.rerun()

    st.divider()
    st.markdown(f"#### 🧭 {'页面导航' if lang == 'zh' else 'Navigation'}")
    st.markdown(f"""
    - [📊 {t('nav_dashboard', lang)}](/1_📊_Dashboard)
    - [🤖 {t('nav_assistant', lang)}](/2_🤖_AI_Assistant)
    - [📈 {t('nav_analytics', lang)}](/3_📈_Analytics)
    - [⚙️ {t('nav_settings', lang)}](/4_⚙️_Settings)
    - [🌍 {'全球汇款情报' if lang == 'zh' else 'Global Intelligence'}](/5_🌍_Global_Intelligence)
    """)

student_id = st.session_state.student_id
lang = st.session_state.lang

# Fetch data
conn = get_db()
account = dict(conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone())
conn.close()

health = calculate_health_score(student_id)
alerts = get_active_alerts(student_id)

# ── Grand Hero Header ────────────────────────────────────────────────────────
hero_title = "CrossPay (微众智汇) — Cross-Border Student Finance AI" if lang == "en" else "CrossPay (微众智汇) — 留学生跨境智能金融助手"
hero_sub = (
    "微众银行国际人工智能金融挑战赛（赛题C：跨境与学生金融）特等奖标准构建 · 零计算幻觉 · 银行级风控双向确认"
    if lang == "zh"
    else "WeBank International AI Finance Challenge (Topic C: Cross-Border & Student Finance) · Zero LLM Math Hallucination · Bank-Grade Safeguards"
)
render_hero(hero_title, hero_sub)

# ── Welcome & System Highlights ──────────────────────────────────────────────
student_name = account.get("name")
origin = account.get("home_country")
curr = account.get("home_currency")

st.markdown(f"""
### 🎓 {'欢迎使用 CrossPay 国际学生金融服务中枢' if lang == 'zh' else 'Welcome to CrossPay Financial Operations Hub'}
{'服务对象' if lang == 'zh' else 'Active Profile'}: **{student_name}** ({origin} → 🇨🇳 China) · {'结算主币种' if lang == 'zh' else 'Base Currency'}: **{curr}/CNY**
""")

# 4 Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(t("kpi_balance", lang), f"¥ {account.get('balance_cny', 0):,.2f}", f"Home: {account.get('balance_home', 0):,.0f} {curr}", badge="Online", badge_type="healthy")
with col2:
    render_kpi_card(t("kpi_tuition", lang), f"¥ {account.get('tuition_amount_cny', 0):,.0f}", f"Due: {account.get('tuition_due_date')}", badge="Upcoming", badge_type="stable")
with col3:
    render_kpi_card(t("kpi_credit", lang), str(account.get("credit_score", 650)), "Tier: Good" if lang == "en" else "评级: 良好", badge="Verified", badge_type="healthy")
with col4:
    h_score = health.get("score", 0)
    render_kpi_card(t("kpi_health", lang), f"{h_score} / 100", health.get("band_zh" if lang == "zh" else "band"), badge="Proprietary", badge_type="excellent" if h_score >= 80 else "healthy")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Module Cards (Quick Launchers) ───────────────────────────────────────────
st.markdown(f"### 🚀 {'四大核心智能模块入口' if lang == 'zh' else 'Four Core Financial Pillars'}")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom: 16px;">
        <h4 style="margin: 0; color: #0A2463;">📊 1. {t('nav_dashboard', lang)}</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 6px;">
        {'综合财务健康评分模型、学费缴费倒计时追踪、即时智能风控预警、一键导出专业PDF财务审计报告。' if lang == 'zh' else 'Proprietary CrossPay Health Score™ gauge, tuition countdown tracker, proactive risk alerts, and one-click downloadable PDF report.'}
        </p>
        <a href="/1_📊_Dashboard" target="_self" style="text-decoration: none; font-weight: 700; color: #0A2463;">👉 {'进入财务总览' if lang == 'zh' else 'Open Dashboard'} &rarr;</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-card">
        <h4 style="margin: 0; color: #0A2463;">📈 3. {t('nav_analytics', lang)}</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 6px;">
        {'近半年消费分类甜甜圈图、支出对比预算趋势图、30天外汇牌价多维走势图、微众汇款直通车服务商成本比对表。' if lang == 'zh' else '6-month spending donut breakdown, budget vs actual spline trends, 30-day FX monitor, and WeBank Direct remittance optimizer.'}
        </p>
        <a href="/3_📈_Analytics" target="_self" style="text-decoration: none; font-weight: 700; color: #0A2463;">👉 {'进入数据分析' if lang == 'zh' else 'Open Analytics'} &rarr;</a>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom: 16px;">
        <h4 style="margin: 0; color: #0A2463;">🤖 2. {t('nav_assistant', lang)}</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 6px;">
        {'双语中英文金融大模型助理（Gemini 3.8 Flash）、确定性数学计算核心、涉及资金变动的双向确认拦截风控体系。' if lang == 'zh' else 'Bilingual Gemini 3.8 Flash agent with stateful context, 2-step write confirmation gate, zero hallucination calculations.'}
        </p>
        <a href="/2_🤖_AI_Assistant" target="_self" style="text-decoration: none; font-weight: 700; color: #0A2463;">👉 {'开始智能对话' if lang == 'zh' else 'Open AI Assistant'} &rarr;</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-card">
        <h4 style="margin: 0; color: #0A2463;">⚙️ 4. {t('nav_settings', lang)}</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 6px;">
        {'学生卡号与护照脱敏资料库、三层权限防御安全架构（Tier 0/1/2）、反洗钱大额监测与制裁名单核验配置。' if lang == 'zh' else 'Student profile PII masking, 3-tier permission security model, AML $10,000 threshold monitor, and tamper-evident audit logs.'}
        </p>
        <a href="/4_⚙️_Settings" target="_self" style="text-decoration: none; font-weight: 700; color: #0A2463;">👉 {'查看系统配置' if lang == 'zh' else 'Open Settings'} &rarr;</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Recent Alerts Preview ───────────────────────────────────────────────────
st.markdown(f"#### ⚡ {'最新智能提醒' if lang == 'zh' else 'Active Proactive Alerts'}")
if alerts:
    for a in alerts[:2]:
        render_alert(a, lang=lang)

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
