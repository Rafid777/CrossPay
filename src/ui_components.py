"""Reusable Streamlit UI components for CrossPay."""
import streamlit as st
from datetime import datetime, date


def render_quick_stats(student_data: dict) -> None:
    """Render metric cards in the sidebar."""
    balance = student_data.get("balance_cny", 0)
    tuition = student_data.get("tuition_amount_cny", 0)
    due_date_str = student_data.get("tuition_due_date", "")
    credit = student_data.get("credit_score", 0)

    # Days until tuition
    days_left = None
    if due_date_str:
        try:
            due = date.fromisoformat(due_date_str)
            days_left = (due - date.today()).days
        except ValueError:
            pass

    col1, col2 = st.columns(2)
    col1.metric("💰 Balance", f"{balance:,.0f} CNY")
    col2.metric("📊 Credit Score", str(credit))

    if days_left is not None:
        color = "🔴" if days_left < 14 else "🟡" if days_left < 30 else "🟢"
        st.metric(f"{color} Tuition Due", f"{tuition:,.0f} CNY", f"{days_left} days left")
    else:
        st.metric("🎓 Tuition", f"{tuition:,.0f} CNY")


def render_credit_bar(score: int) -> None:
    """Render a credit score progress bar."""
    pct = (score - 300) / (850 - 300)
    tier = (
        "Exceptional" if score >= 800 else
        "Very Good" if score >= 740 else
        "Good" if score >= 670 else
        "Fair" if score >= 580 else "Poor"
    )
    st.caption(f"Credit Score: **{score}** ({tier})")
    st.progress(min(max(pct, 0.0), 1.0))


def render_message(role: str, content: str) -> None:
    """Render a chat message bubble."""
    with st.chat_message(role):
        st.markdown(content)


def render_confirmation_banner(preview_text: str) -> tuple[bool, bool]:
    """Render a confirmation banner. Returns (confirmed, cancelled)."""
    st.warning("⚠️ Action pending — please confirm or cancel below.")
    with st.expander("📋 Action Details", expanded=True):
        st.markdown(preview_text)
    col1, col2 = st.columns(2)
    confirmed = col1.button("✅ Confirm", type="primary", use_container_width=True)
    cancelled = col2.button("❌ Cancel", type="secondary", use_container_width=True)
    return confirmed, cancelled


def ensure_session_state() -> None:
    """Defensively bootstrap all session state variables across any page entry point."""
    import os
    from src.db import get_db
    from src.mock_data import seed_mock_data

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

    if "engine_mode" not in st.session_state:
        st.session_state.engine_mode = "autonomous"

