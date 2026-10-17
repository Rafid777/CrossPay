"""Page 4: System Settings & Compliance Profile (系统设置与合规配置)."""
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.theme import load_css, render_hero, render_compliance_footer
from src.i18n import t, get_current_lang
from src.ui_components import ensure_session_state

load_dotenv()

st.set_page_config(
    page_title="CrossPay — Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
ensure_session_state()

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
    
    - **🚨 {'反电信网络诈骗与风控拦截 (Anti-Fraud)' if lang == 'zh' else 'Anti-Telecom Fraud & Scam Engine'}:**
      - {'严格贯彻《中华人民共和国反电信网络诈骗法》与“断卡行动”监管准则' if lang == 'zh' else 'Enforces PRC Anti-Telecom Fraud Law & PBOC "Card Break Action" mandates'}
      - {'学费代缴盗卡风险筛查（非官方渠道折扣 ≥ 10% 自动锁定）' if lang == 'zh' else 'Tuition proxy payment scam detection (unauthorized discounts ≥ 10% locked)'}
      - {'社交网络私下换汇“断卡”风险拦截，直联全国反诈劝阻专线 96110' if lang == 'zh' else 'P2P chat exchange freeze defense, connected to China Anti-Fraud Hotline 96110'}
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

# ── AI Model & Autonomous Engine Profile ─────────────────────────────────────
st.markdown(f"### 🧠 {'自研金融大模型与引擎架构' if lang == 'zh' else 'Autonomous AI Model & Architecture'}")
col_m1, col_m2 = st.columns([6, 6])

with col_m1:
    import json
    metrics_path = "models/training_metrics.json"
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

    model_table = [
        {"Parameter / 指标": "Model Architecture / 模型架构", "Value / 数值": metrics.get("model_name", "CrossPay-Autonomous-FinIntent-v1")},
        {"Parameter / 指标": "Offline Execution / 离线自主运行", "Value / 数值": "100% On-Device (Zero API Key)" if lang == "en" else "100% 端侧本地自主运行 (零外部API)"},
        {"Parameter / 指标": "Intent Categories / 意图分类数", "Value / 数值": f"{metrics.get('num_classes', 18)} 类别 (Classes)"},
        {"Parameter / 指标": "Training Samples / 训练样本数", "Value / 数值": f"{metrics.get('training_samples', 204)} 条金融双语语料"},
        {"Parameter / 指标": "Feature Extraction / 特征工程", "Value / 数值": metrics.get("vectorizer", "TF-IDF char_wb (2-5 ngrams)")},
        {"Parameter / 指标": "Classifier Algorithm / 分类算法", "Value / 数值": metrics.get("classifier", "LogisticRegression(C=10.0)")},
        {"Parameter / 指标": "Stratified CV Accuracy / 交叉验证准确率", "Value / 数值": f"{metrics.get('cv_accuracy_pct', 59.31)}%"},
    ]
    st.dataframe(model_table, use_container_width=True)

with col_m2:
    st.markdown(f"""
    - **⚡ {'零API全自主闭环' if lang == 'zh' else 'Zero-API Fully Autonomous'}:**
      - {'评委及用户无需申请或配置任何 Google Gemini API Key，直接启动即可完整体验所有 18 项智能金融功能。' if lang == 'zh' else 'Judges & users do not need to provide any API keys; runs out-of-the-box with 100% self-contained NLP.'}
    - **🔒 {'隐私隔离与数据不出境' if lang == 'zh' else 'Data Privacy & Sovereignty'}:**
      - {'所有学生账单、敏感交易记录和人行征信数据均在本地处理，完全满足中国《数据安全法》与《个人信息保护法 (PIPL)》。' if lang == 'zh' else 'All financial records stay on-device, fully compliant with Chinese data security and PIPL regulations.'}
    - **🤝 {'双模混合驱动 (Hybrid Architecture)' if lang == 'zh' else 'Dual-Engine Hybrid Flexibility'}:**
      - {'支持在侧边栏一键切换【CrossPay 自治大模型】与【Google Gemini 3.8 Flash 云端大模型】，自由对比两代技术架构。' if lang == 'zh' else 'Easily toggle between on-device autonomous engine and cloud Gemini 3.8 Flash in the sidebar.'}
    """)

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
