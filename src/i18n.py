"""Internationalization (i18n) bilingual dictionary for English and Chinese."""
import streamlit as st

TRANSLATIONS = {
    # App General
    "app_title": {"en": "CrossPay — AI Financial Assistant", "zh": "CrossPay — 留学生AI智能金融助手"},
    "app_subtitle": {"en": "WeBank International AI Finance Challenge", "zh": "微众银行国际人工智能金融挑战赛"},
    "powered_by": {"en": "Powered by Gemini 3.8 Flash & WeBank Core", "zh": "基于 Gemini 3.8 Flash 与微众金融核心驱动"},
    "select_student": {"en": "👤 Select Student Profile", "zh": "👤 选择学生档案"},
    "switch_language": {"en": "🌐 Language / 语言", "zh": "🌐 语言 / Language"},
    
    # Navigation & Tabs
    "nav_dashboard": {"en": "📊 Dashboard", "zh": "📊 财务总览"},
    "nav_assistant": {"en": "🤖 AI Assistant", "zh": "🤖 智能助手"},
    "nav_analytics": {"en": "📈 Analytics", "zh": "📈 数据洞察"},
    "nav_settings": {"en": "⚙️ Settings", "zh": "⚙️ 系统设置"},

    # Dashboard Metrics
    "kpi_balance": {"en": "CNY Balance", "zh": "人民币可用余额"},
    "kpi_tuition": {"en": "Tuition Due", "zh": "应缴学费"},
    "kpi_credit": {"en": "Credit Score", "zh": "征信信用分"},
    "kpi_health": {"en": "Financial Health", "zh": "财务健康指数"},
    "tuition_countdown": {"en": "Days until deadline", "zh": "距缴费截止天数"},
    "home_reserve": {"en": "Home Reserve", "zh": "本币储备"},
    
    # Financial Health Score
    "health_title": {"en": "CrossPay Financial Health Score™", "zh": "CrossPay 财务健康评分™"},
    "health_desc": {"en": "Proprietary multi-factor composite risk and liquidity metric", "zh": "基于多因子加权信用、支出与学费流动性评估体系"},
    "credit_comp": {"en": "Credit History", "zh": "征信记录 (30%)"},
    "spend_comp": {"en": "Spending Discipline", "zh": "支出纪律 (25%)"},
    "save_comp": {"en": "Emergency Reserve", "zh": "应急储备 (25%)"},
    "tuition_comp": {"en": "Tuition Readiness", "zh": "学费筹备度 (20%)"},

    # Actions & Buttons
    "export_pdf": {"en": "📥 Export Financial Report (PDF)", "zh": "📥 导出专业财务审计报告 (PDF)"},
    "generating_pdf": {"en": "Generating high-resolution report...", "zh": "正在生成高精度财务报告..."},
    "confirm": {"en": "✅ Confirm Action", "zh": "✅ 确认执行"},
    "cancel": {"en": "❌ Cancel", "zh": "❌ 取消操作"},
    "clear_chat": {"en": "🗑️ Clear Chat History", "zh": "🗑️ 清空对话记录"},
    "ask_input_placeholder": {"en": "Ask about exchange rates, tuition remittance, spending, credit...", "zh": "输入关于汇率、跨境汇款、记账消费或征信提升的问题..."},
    "send": {"en": "Send", "zh": "发送"},

    # Analytics Section
    "analytics_title": {"en": "Financial Intelligence & Trends", "zh": "多维金融智能与趋势洞察"},
    "chart_spending_breakdown": {"en": "Monthly Spending Breakdown (CNY)", "zh": "本月消费支出分布 (人民币)"},
    "chart_spending_trend": {"en": "6-Month Spending Trend vs Budget", "zh": "近半年月度消费支出对比预算"},
    "chart_credit_progression": {"en": "Credit Score Growth Journey", "zh": "学生征信成长与积分跃迁轨迹"},
    "chart_fx_trend": {"en": "30-Day Foreign Exchange Rate Monitor", "zh": "近30日外汇牌价与汇率走势监控"},
    "chart_remittance_cost": {"en": "Cross-Border Remittance Cost Comparison ($500 USD)", "zh": "跨境汇款服务商综合成本对比 ($500 USD)"},

    # Regulatory & Compliance
    "compliance_title": {"en": "Compliance & Security Safeguards", "zh": "合规监管与金融安全护栏"},
    "aml_safe": {"en": "PBOC & SAFE Compliant", "zh": "人民银行及外汇管理局合规支持"},
    "aml_threshold_desc": {"en": "Automated AML threshold screening ($10,000 USD limit)", "zh": "自动反洗钱大额监测与交易穿透（阈值 $10,000 美元）"},
    "pii_masked": {"en": "Zero-Knowledge PII Masking", "zh": "零知识敏感隐私（护照/卡号）脱敏存储"},
    "audit_logged": {"en": "Tamper-Evident Audit Logging", "zh": "全链路不可篡改 JSONL 审计追踪"},
    
    # Students
    "STU001_name": {"en": "Rafi Ahmed", "zh": "拉菲·艾哈迈德"},
    "STU002_name": {"en": "Ayesha Khan", "zh": "阿伊莎·汗"},
    "STU003_name": {"en": "Emeka Okafor", "zh": "埃梅卡·奥卡福"},
}


def t(key: str, lang: str = "en") -> str:
    """Translate a key into target language, fallback to English or key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))


def get_current_lang() -> str:
    """Retrieve the user's selected language from session state."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    return st.session_state.lang
