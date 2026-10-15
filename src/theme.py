"""Theme management and custom HTML/CSS component renderers for CrossPay."""
import os
import streamlit as st


def load_css() -> None:
    """Inject the custom CSS stylesheet into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_hero(title: str, subtitle: str) -> None:
    """Render a modern gradient hero header."""
    html = f"""
    <div class="hero-banner">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str = "", badge: str = "", badge_type: str = "healthy") -> None:
    """Render a glassmorphic fintech KPI metric card."""
    badge_html = f'<span class="badge badge-{badge_type}">{badge}</span>' if badge else ""
    html = f"""
    <div class="kpi-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="kpi-title">{title}</div>
            {badge_html}
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_alert(alert: dict, lang: str = "en") -> None:
    """Render a styled alert banner with icon and action prompt."""
    sev = alert.get("severity", "info")
    icon = alert.get("icon", "ℹ️")
    title = alert.get("title_zh" if lang == "zh" else "title", "")
    message = alert.get("message_zh" if lang == "zh" else "message", "")

    html = f"""
    <div class="alert-box alert-{sev}">
        <strong>{icon} {title}</strong><br/>
        <span>{message}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_compliance_footer(lang: str = "en") -> None:
    """Render regulatory compliance disclaimer in Chinese and English."""
    if lang == "zh":
        text = """
        🏛️ <strong>监管声明与合规说明：</strong> 所有跨境收付款及结售汇交易均符合中国人民银行 (PBOC) 与国家外汇管理局 (SAFE) 政策框架。
        单笔超过 10,000 美元等值外币转账触发反洗钱 (AML) 穿透核查与大额交易合规留痕。微众银行 WeBank 提供底层可信金融通道支持。
        """
    else:
        text = """
        🏛️ <strong>Regulatory & Compliance Notice:</strong> All cross-border remittances and foreign exchange conversions
        comply with PBOC (People's Bank of China) and SAFE (State Administration of Foreign Exchange) regulatory frameworks.
        Transactions exceeding $10,000 USD are subject to AML statutory reporting and immutable audit logging. Powered by WeBank digital banking infrastructure.
        """
    html = f'<div class="compliance-footer">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)
