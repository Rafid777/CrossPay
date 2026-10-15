"""Page 2: AI Financial Assistant (智能金融助手)."""
import os
import streamlit as st
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.agent import CrossPayAgent
from src.ui_components import render_message, render_confirmation_banner
from src.theme import load_css, render_hero, render_compliance_footer
from src.i18n import t, get_current_lang

load_dotenv()

st.set_page_config(
    page_title="CrossPay — AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# Session State Setup
if "db_seeded" not in st.session_state:
    conn = get_db()
    seed_mock_data(conn)
    conn.close()
    st.session_state.db_seeded = True

if "student_id" not in st.session_state:
    st.session_state.student_id = os.getenv("STUDENT_ID", "STU001")

if "lang" not in st.session_state:
    st.session_state.lang = "en"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

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

    st.divider()
    st.markdown(f"#### ⚡ {'快捷金融指令' if lang == 'zh' else 'Quick Action Shortcuts'}")
    
    conn = get_db()
    acc_row = conn.execute("SELECT home_currency FROM accounts WHERE id = ?", (st.session_state.student_id,)).fetchone()
    conn.close()
    curr = acc_row["home_currency"] if acc_row else "BDT"

    if lang == "zh":
        quick_actions = [
            ("💱 查询实时汇率", f"请查询最新的 {curr} 对人民币 CNY 汇率。"),
            ("🏦 对比跨境汇款", f"我想汇款 $500 美元到中国交学费，请对比各服务商费用和到账速度。"),
            ("📅 规划学费缴纳", "根据当前汇率走势，帮我推荐最佳的学费缴纳窗口期。"),
            ("📊 查看消费预算", "查看我本月的各项生活消费支出与预算使用情况。"),
            ("💳 提升中国征信", "作为国际留学生，我在中国有哪些安全合规建立良好征信的方法？"),
            ("🏛️ 反洗钱合规自查", "请帮我检查单笔 $12,000 美元的汇款是否会触发外汇反洗钱合规申报？"),
        ]
    else:
        quick_actions = [
            ("💱 Real-Time FX Rate", f"What is the current {curr} to CNY exchange rate?"),
            ("🏦 Compare Remittance", f"Compare remittance options to send $500 USD to China for tuition."),
            ("📅 Schedule Tuition", "Help me find the optimal window to pay my tuition based on FX trends."),
            ("📊 Spending Summary", "Show my spending summary and budget breakdown for this month."),
            ("💳 Credit Building Tips", "How can an international student build credit history in China?"),
            ("🏛️ AML Compliance Check", "Check if a $12,000 USD transfer will trigger AML reporting requirements."),
        ]

    for label, prompt in quick_actions:
        if st.button(label, use_container_width=True):
            st.session_state._quick_prompt = prompt

    st.divider()
    if st.button(t("clear_chat", lang), use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

student_id = st.session_state.student_id
lang = st.session_state.lang

# Agent Initialization
if st.session_state.agent is None:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.warning("⚠️ GEMINI_API_KEY is not set in `.env`. Running in mock interactive preview mode.")
        api_key = "demo-placeholder"
    st.session_state.agent = CrossPayAgent(student_id, api_key)
    
    welcome_text = (
        f"👋 您好！我是 **CrossPay** 微众智汇智能金融助手。\n\n"
        f"当前服务对象：**{student_labels.get(student_id)}**。\n\n"
        f"我可以为您提供：\n"
        f"- 💱 **实时汇率换算与汇率走势分析**\n"
        f"- 🏦 **微众跨境汇款直通车与成本对比**\n"
        f"- 📅 **学费缴费最佳时机智能规划**\n"
        f"- 📊 **生活日常开销预算管理与记账**\n"
        f"- 💳 **人行征信与跨国信用积分成长方案**\n"
        f"- 🏛️ **外汇管理局 (SAFE) 与反洗钱 (AML) 政策咨询**\n\n"
        f"今天有什么我可以帮您的？"
        if lang == "zh"
        else
        f"👋 Hi! I'm **CrossPay**, your AI financial assistant powered by WeBank infrastructure.\n\n"
        f"Assisting: **{student_labels.get(student_id)}**.\n\n"
        f"I can help you with:\n"
        f"- 💱 **Foreign Exchange Rates & Trend Tracking**\n"
        f"- 🏦 **Cross-Border Remittance Cost Optimization**\n"
        f"- 📅 **Tuition Payment Window Scheduling**\n"
        f"- 📊 **Expense Tracking & Monthly Budgeting**\n"
        f"- 💳 **Credit Score Building in China**\n"
        f"- 🏛️ **PBOC & SAFE Regulatory Compliance Inquiries**\n\n"
        f"How may I assist your finances today?"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

agent: CrossPayAgent = st.session_state.agent

# Hero Banner
hero_title = "CrossPay AI Financial Assistant" if lang == "en" else "CrossPay 微众智汇 AI 金融助手"
hero_sub = (
    "人机协同双向风控确认 · 严格确定性计算工具 · 零计算幻觉"
    if lang == "zh"
    else "Deterministic Financial Computation · 2-Step Confirmation Gate · Zero LLM Math Hallucination"
)
render_hero(hero_title, hero_sub)

# Confirmation Banner if action is pending
if agent.pending_action:
    preview_text = agent._format_confirmation_preview(
        agent.pending_action["tool"],
        agent.pending_action["preview"]
    )
    confirmed, cancelled = render_confirmation_banner(preview_text)
    if confirmed:
        result = agent.confirm_action()
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()
    if cancelled:
        result = agent.cancel_action()
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()

# Chat History
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# Quick Prompt trigger
quick_prompt = st.session_state.pop("_quick_prompt", None)

# Input Box
user_input = st.chat_input(t("ask_input_placeholder", lang))
if user_input or quick_prompt:
    prompt = quick_prompt or user_input
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)
    
    with st.spinner("CrossPay is thinking..." if lang == "en" else "CrossPay 正在调取微众金融计算引擎..."):
        try:
            response = agent.chat(prompt)
        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str or "fake" in agent.api_key or "demo" in agent.api_key:
                response = (
                    "⚠️ **演示提示 (Demo Notice)**: 请在 `.env` 文件中配置您的 `GEMINI_API_KEY` 以启用实时 Gemini 3.8 Flash 模型。\n\n"
                    "在此期间，所有确定性金融底层工具（外汇、微众汇款、预算、征信模拟、AML大额筛查）均在本地 100% 正常运行！"
                    if lang == "zh"
                    else
                    "⚠️ **Demo Notice**: Please set your valid `GEMINI_API_KEY` in `.env` to connect live with Gemini 3.8 Flash.\n\n"
                    "Meanwhile, all deterministic backend financial tools (FX, WeBank Remittance, Budgeting, Credit Simulation, AML checks) are 100% operational locally!"
                )
            else:
                response = f"❌ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    render_message("assistant", response)
    st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
