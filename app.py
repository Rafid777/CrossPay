"""CrossPay — AI Financial Assistant for International Students."""
import os
import streamlit as st
from dotenv import load_dotenv
from src.db import get_db
from src.mock_data import seed_mock_data
from src.agent import CrossPayAgent
from src.ui_components import (
    render_quick_stats, render_credit_bar,
    render_message, render_confirmation_banner
)

load_dotenv()

st.set_page_config(
    page_title="CrossPay — Student Finance Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state initialisation ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "student_id" not in st.session_state:
    st.session_state.student_id = os.getenv("STUDENT_ID", "STU001")
if "db_seeded" not in st.session_state:
    conn = get_db()
    seed_mock_data(conn)
    conn.close()
    st.session_state.db_seeded = True

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bank-building.png", width=60)
    st.title("CrossPay")
    st.caption("AI Finance for International Students")
    st.divider()

    # Student selector
    student_options = {"STU001": "Rafi Ahmed (BD)", "STU002": "Ayesha Khan (PK)", "STU003": "Emeka Okafor (NG)"}
    selected = st.selectbox(
        "👤 Select Student",
        options=list(student_options.keys()),
        format_func=lambda x: student_options[x],
        index=list(student_options.keys()).index(st.session_state.student_id),
    )
    if selected != st.session_state.student_id:
        st.session_state.student_id = selected
        st.session_state.agent = None
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📊 Quick Stats")
    conn = get_db()
    row = conn.execute("SELECT * FROM accounts WHERE id = ?", (st.session_state.student_id,)).fetchone()
    conn.close()
    if row:
        student_data = dict(row)
        render_quick_stats(student_data)
        render_credit_bar(student_data.get("credit_score", 650))

    st.divider()
    st.subheader("⚡ Quick Actions")
    quick_actions = [
        ("💱 Check FX Rate", "What is the current BDT to CNY exchange rate?"),
        ("🏦 Compare Remittance", "Compare remittance options to send $300 USD to China."),
        ("📅 Schedule Tuition", "Help me schedule my tuition payment optimally."),
        ("📊 My Budget", "Show my spending summary for this month."),
        ("💳 Credit Tips", "How can I build my credit score in China?"),
        ("🌍 Transfer Check", "Is it safe to transfer money to Bangladesh?"),
    ]
    for label, prompt in quick_actions:
        if st.button(label, use_container_width=True):
            st.session_state._quick_prompt = prompt

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

# ── Initialise agent ──────────────────────────────────────────────────────────
if st.session_state.agent is None:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not set. Add it to your .env file.")
        st.code("GEMINI_API_KEY=your_key_here", language="bash")
        st.stop()
    st.session_state.agent = CrossPayAgent(st.session_state.student_id, api_key)
    welcome = (
        f"👋 Hi! I'm **CrossPay**, your AI finance assistant.\n\n"
        f"I'm helping **{student_options.get(st.session_state.student_id, st.session_state.student_id)}** "
        f"manage finances in China.\n\n"
        f"I can help you with:\n"
        f"- 💱 Exchange rates & currency conversion\n"
        f"- 🏦 Finding the cheapest way to send money\n"
        f"- 📅 Scheduling tuition payments\n"
        f"- 📊 Tracking your budget\n"
        f"- 💳 Building your credit score\n\n"
        f"What would you like to do today?"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

agent: CrossPayAgent = st.session_state.agent

# ── Main area header ──────────────────────────────────────────────────────────
st.title("🏦 CrossPay — Student Finance Assistant")
st.caption(f"Powered by Gemini 3.8 Flash · Student: {student_options.get(st.session_state.student_id, st.session_state.student_id)}")
st.divider()

# ── Confirmation banner (shown above chat when pending) ───────────────────────
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

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# ── Handle quick action button presses ───────────────────────────────────────
quick_prompt = st.session_state.pop("_quick_prompt", None)

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about exchange rates, transfers, budget, or credit...")
if user_input or quick_prompt:
    prompt = quick_prompt or user_input
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)
    with st.spinner("CrossPay is thinking..."):
        try:
            response = agent.chat(prompt)
        except Exception as e:
            response = f"❌ Error: {e}\n\nPlease check your GEMINI_API_KEY and try again."
    st.session_state.messages.append({"role": "assistant", "content": response})
    render_message("assistant", response)
    st.rerun()
