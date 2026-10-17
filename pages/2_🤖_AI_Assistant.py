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
            ("🏛️ 央行中间价牌价", "查询今天中国人民银行官方人民币汇率中间价与银行牌价。"),
            ("🏦 对比跨境汇款", f"我想汇款 $500 美元到中国交学费，请对比各服务商费用和到账速度。"),
            ("📅 规划学费缴纳", "根据当前汇率走势，帮我推荐最佳的学费缴纳窗口期。"),
            ("🛡️ 外汇局额度自查", "查询我今年的国家外汇管理局5万美元便利化结汇额度。"),
            ("🔍 消费异常排查", "帮我检测最近的资金流水中是否存在异常消费或突发大额支出。"),
            ("🌐 同行消费基准", "对比来华留学生群体的月度平均生活费与学费基准。"),
            ("💳 提升中国征信", "作为国际留学生，我在中国有哪些安全合规建立良好征信的方法？"),
            ("⚖️ 反洗钱合规自查", "请帮我检查单笔 $12,000 美元的汇款是否会触发外汇反洗钱合规申报？"),
            ("🛡️ 反诈安全排查", "有人在微信群里说可以8折优惠代缴大学学费，还有人想高价租借我的银行卡，这是诈骗吗？"),
        ]
    else:
        quick_actions = [
            ("💱 Real-Time FX Rate", f"What is the current {curr} to CNY exchange rate?"),
            ("🏛️ PBOC Parity Quote", "What is today's PBOC central parity rate for USD/CNY?"),
            ("🏦 Compare Remittance", f"Compare remittance options to send $500 USD to China for tuition."),
            ("📅 Schedule Tuition", "Help me find the optimal window to pay my tuition based on FX trends."),
            ("🛡️ SAFE Quota Check", "Check my SAFE annual facilitation quota for a $5,000 USD transfer."),
            ("🔍 Anomaly Screening", "Check my transaction history for any abnormal spending spikes or anomalies."),
            ("🌐 Cohort Benchmarks", "Show me international student cohort spending benchmarks for China."),
            ("💳 Credit Building Tips", "How can an international student build credit history in China?"),
            ("⚖️ AML Compliance Check", "Check if a $12,000 USD transfer will trigger AML reporting requirements."),
            ("🛡️ Anti-Scam Check", "Someone offered me a 20% discount on tuition on WeChat, and someone asked to rent my bank card. Is this a scam?"),
        ]

    for label, prompt in quick_actions:
        if st.button(label, use_container_width=True):
            st.session_state._quick_prompt = prompt

    st.divider()
    if st.button(t("clear_chat", lang), use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

    st.divider()
    # AI Engine Architecture Selector
    engine_labels = {
        "autonomous": "🧠 CrossPay 自治大模型 (本地训练·零API依赖)" if lang == "zh" else "🧠 CrossPay Autonomous Model (Local Trained · No API Key)",
        "gemini": "⚡ Google Gemini 3.8 Flash (云端协同)" if lang == "zh" else "⚡ Google Gemini 3.8 Flash (Cloud LLM)",
    }
    selected_engine = st.selectbox(
        "🤖 " + ("AI 驱动引擎架构" if lang == "zh" else "AI Engine Architecture"),
        options=["autonomous", "gemini"],
        format_func=lambda x: engine_labels[x],
        index=0,
    )
    if "engine_mode" not in st.session_state or st.session_state.engine_mode != selected_engine:
        st.session_state.engine_mode = selected_engine
        st.session_state.agent = None

student_id = st.session_state.student_id
lang = st.session_state.lang
engine_mode = st.session_state.get("engine_mode", "autonomous")

# Agent Initialization
if st.session_state.agent is None:
    api_key = os.getenv("GEMINI_API_KEY", "")
    st.session_state.agent = CrossPayAgent(student_id, api_key=api_key, engine_mode=engine_mode)
    
    welcome_text = (
        f"👋 您好！我是 **CrossPay** 微众智汇智能金融助手。\n\n"
        f"当前服务对象：**{student_labels.get(student_id)}** · 运行架构：**`{engine_labels[engine_mode]}`**。\n\n"
        f"我可以为您提供：\n"
        f"- 💱 **实时汇率换算与汇率走势分析**\n"
        f"- 🏦 **微众跨境汇款直通车与成本对比**\n"
        f"- 📅 **学费缴费最佳时机智能规划**\n"
        f"- 📊 **生活日常开销预算管理与记账**\n"
        f"- 💳 **人行征信与跨国信用积分成长方案**\n"
        f"- 🏛️ **外汇管理局 (SAFE) 与反洗钱 (AML) 政策咨询**\n"
        f"- 🌍 **世界银行 (World Bank) 官方宏观汇款数据分析**\n\n"
        f"今天有什么我可以帮您的？"
        if lang == "zh"
        else
        f"👋 Hi! I'm **CrossPay**, your on-device AI financial assistant.\n\n"
        f"Assisting: **{student_labels.get(student_id)}** · Architecture: **`{engine_labels[engine_mode]}`**.\n\n"
        f"I can help you with:\n"
        f"- 💱 **Foreign Exchange Rates & Trend Tracking**\n"
        f"- 🏦 **Cross-Border Remittance Cost Optimization**\n"
        f"- 📅 **Tuition Payment Window Scheduling**\n"
        f"- 📊 **Expense Tracking & Monthly Budgeting**\n"
        f"- 💳 **Credit Score Building in China**\n"
        f"- 🏛️ **PBOC & SAFE Regulatory Compliance Inquiries**\n"
        f"- 🌍 **World Bank Official Global Remittance Intelligence**\n\n"
        f"How may I assist your finances today?"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

agent: CrossPayAgent = st.session_state.agent

# Hero Banner
hero_title = "CrossPay AI Financial Assistant" if lang == "en" else "CrossPay 微众智汇 AI 金融助手"
hero_sub = (
    "本地自研自治金融大模型 · 人机协同双向风控确认 · 严格确定性计算工具 · 零计算幻觉 · 零API依赖"
    if lang == "zh"
    else "Autonomous On-Device Financial Model · 2-Step Confirmation Gate · Zero LLM Math Hallucination · 100% Offline"
)
render_hero(hero_title, hero_sub)

# Status notification badge
if engine_mode == "autonomous":
    st.markdown(
        """<div style="background:#0F2B1D; border:1px solid #10B981; border-radius:10px; padding:0.75rem 1.2rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:1.3rem;">🟢</span>
            <div>
              <b style="color:#10B981;">端侧自研自治金融大模型已激活 (100% Offline Autonomous Engine)</b><br/>
              <span style="color:#A7F3D0; font-size:0.85rem;">已加载本地 18 类微众金融意图分类模型 (TF-IDF + LogisticRegression) 与确定性风控中台，完全不依赖外部网络与任何云端 API Key。</span>
            </div>
        </div>""" if lang == "zh" else
        """<div style="background:#0F2B1D; border:1px solid #10B981; border-radius:10px; padding:0.75rem 1.2rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:1.3rem;">🟢</span>
            <div>
              <b style="color:#10B981;">CrossPay Autonomous Financial Model Active (100% Offline)</b><br/>
              <span style="color:#A7F3D0; font-size:0.85rem;">Powered by local 18-class financial intent pipeline and deterministic WeBank computation tools. Zero external API keys or cloud network needed.</span>
            </div>
        </div>""",
        unsafe_allow_html=True
    )
else:
    st.info("⚡ Google Gemini 3.8 Flash Cloud Mode active." if lang == "en" else "⚡ 正在使用 Google Gemini 3.8 Flash 云端大模型模式。")

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
        except Exception:
            resp, pending = agent.autonomous_engine.process_query(prompt)
            if pending:
                agent.pending_action = pending
            response = resp

    st.session_state.messages.append({"role": "assistant", "content": response})
    render_message("assistant", response)
    st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
