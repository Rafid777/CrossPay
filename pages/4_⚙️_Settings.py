"""Page 4: System Settings & Compliance Profile (系统设置与合规配置)."""
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.theme import load_css, render_hero, render_compliance_footer
from src.i18n import t, get_current_lang

load_dotenv()

st.set_page_config(
    page_title="CrossPay — Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# Session State
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

    lang_choice = st.radio(
        "🌐 Language / 语言",
        options=["English", "简体中文"],
        index=0 if st.session_state.lang == "en" else 1,
        horizontal=True,
    )
    st.session_state.lang = "zh" if lang_choice == "简体中文" else "en"
    lang = st.session_state.lang

    st.divider()

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

student_id = st.session_state.student_id
lang = st.session_state.lang

# Fetch Account
conn = get_db()
acc = dict(conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone())
conn.close()

hero_title = "CrossPay System & Security Configuration" if lang == "en" else "CrossPay 系统管理与合规安全配置"
hero_sub = (
    "银行级安全基线 · 零信任权限分级 · 留学生档案全生命周期管理"
    if lang == "zh"
    else "Bank-Grade Security Baselines · Zero-Trust Permission Tiering · Lifecycle Student Profiles"
)
render_hero(hero_title, hero_sub)

col_acc, col_sec = st.columns([6, 6])

with col_acc:
    st.markdown(f"### 👤 {'当前学生账户信息' if lang == 'zh' else 'Active Student Profile'}")
    
    info_table = [
        {"Property / 属性": "Student ID / 学号", "Value / 参数值": acc.get("id")},
        {"Property / 属性": "Full Name / 姓名", "Value / 参数值": acc.get("name")},
        {"Property / 属性": "Home Country / 籍贯", "Value / 参数值": acc.get("home_country")},
        {"Property / 属性": "Host Country / 留学国家", "Value / 参数值": "China (CN) / 中国"},
        {"Property / 属性": "Home Currency / 本币", "Value / 参数值": acc.get("home_currency")},
        {"Property / 属性": "Host Currency / 结算币种", "Value / 参数值": "CNY (¥) / 人民币"},
        {"Property / 属性": "Passport (Masked) / 护照脱敏", "Value / 参数值": acc.get("passport_number")},
        {"Property / 属性": "Bank Account (Masked) / 银行卡号", "Value / 参数值": acc.get("bank_account")},
        {"Property / 属性": "Tuition Due / 应缴学费", "Value / 参数值": f"¥ {acc.get('tuition_amount_cny', 0):,.2f}"},
        {"Property / 属性": "Tuition Due Date / 缴费截止日", "Value / 参数值": acc.get("tuition_due_date")},
    ]
    st.dataframe(info_table, use_container_width=True)

with col_sec:
    st.markdown(f"### 🛡️ {'金融安全与监管护栏' if lang == 'zh' else 'Security & Compliance Safeguards'}")

    st.markdown(f"""
    - **🔐 {'权限分级防御模型' if lang == 'zh' else '3-Tier Permission Model'}:**
      - **Tier 0 (Read)**: {'汇率查询、费用对比、账单查阅（自由调用）' if lang == 'zh' else 'FX rates, remittance compare, budget summary (Unrestricted)'}
      - **Tier 1 (Write)**: {'记账、设置预算（Python层强制双向确认框拦截）' if lang == 'zh' else 'Add expense, set budget (Enforced 2-step UI confirmation)'}
      - **Tier 2 (Regulated)**: {'学费大额转账（AML大额申报预检 + 国际制裁国家阻断）' if lang == 'zh' else 'Tuition transfer, remittance (AML check + Sanctions screen)'}
    
    - **🏛️ {'外汇大额穿透监测 (AML)' if lang == 'zh' else 'AML Threshold Monitor'}:**
      - {'单笔超 $10,000 USD 自动标红并提示合规申报流程' if lang == 'zh' else 'Transactions > $10,000 USD automatically flagged for PBOC/SAFE reporting'}
    
    - **🚫 {'国际反制裁名单库' if lang == 'zh' else 'Sanctions Screening Engine'}:**
      - {'已集成 10 个国际受制裁国家/地区代码实时硬拦截' if lang == 'zh' else 'Real-time deterministic blocking for 10 sanctioned ISO destination codes'}
    
    - **📝 {'零知识敏感隐私脱敏 (PII Masking)' if lang == 'zh' else 'PII Masking & Privacy'}:**
      - {'所有护照号、8位以上银行卡号在写入日志前由正则自动掩码为 ****' if lang == 'zh' else 'All 8+ digit bank accounts and passport numbers masked with **** before logging'}
    """)

    # Audit log status
    log_path = "logs/execution_log.jsonl"
    log_count = 0
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_count = len(f.readlines())
    
    st.info(
        f"📋 **{'审计日志状态' if lang == 'zh' else 'Audit Log Status'}:** "
        f"{'已捕获并记录' if lang == 'zh' else 'Captured'} **{log_count}** "
        f"{'条不可篡改金融工具执行痕迹' if lang == 'zh' else 'tamper-evident tool execution entries'} (`{log_path}`)."
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ── Reset / Re-seed Database ─────────────────────────────────────────────────
st.markdown(f"### 🔄 {'系统数据与状态重置' if lang == 'zh' else 'System Maintenance & Mock Reset'}")
col_btn, col_msg = st.columns([3, 7])
with col_btn:
    if st.button("🔄 " + ("重置并重新填充测试数据" if lang == "zh" else "Reset & Reseed Mock Database"), type="secondary", use_container_width=True):
        conn = get_db()
        seed_mock_data(conn)
        conn.close()
        st.session_state.agent = None
        st.session_state.messages = []
        st.success("✅ Database reseeded with 6-month historical data!" if lang == "en" else "✅ 数据库已重置并重新注入6个月丰富交易历史！")

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
