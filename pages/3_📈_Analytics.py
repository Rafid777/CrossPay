"""Page 3: Deep Financial Analytics & Trends (数据洞察与趋势分析)."""
import os
import streamlit as st
from dotenv import load_dotenv

from src.db import get_db
from src.mock_data import seed_mock_data
from src.tools.analytics import get_fx_trend, get_spending_trend, get_credit_trend
from src.tools.remittance import compare_remittance_options
from src.charts import (
    create_spending_donut,
    create_monthly_trend,
    create_credit_journey,
    create_fx_trend,
    create_remittance_comparison,
)
from src.theme import load_css, render_hero, render_compliance_footer
from src.i18n import t, get_current_lang

load_dotenv()

st.set_page_config(
    page_title="CrossPay — Analytics",
    page_icon="📈",
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
home_curr = acc.get("home_currency", "BDT")

# Hero Banner
hero_title = "CrossPay Financial Intelligence & Analytics" if lang == "en" else "CrossPay 财务大数据与趋势洞察"
hero_sub = (
    "高精度消费全景剖析 · 汇率智能套保监控 · 跨国征信成长图谱"
    if lang == "zh"
    else "Multi-Dimensional Spending Analysis · 30-Day FX Tracking · Credit Growth Trajectory"
)
render_hero(hero_title, hero_sub)

# ── Row 1: Spending Analytics (Line + Donut) ─────────────────────────────────
st.markdown(f"### 📊 {'支出分析与消费模式' if lang == 'zh' else 'Expenditure Patterns & Budget Discipline'}")

col_line, col_donut = st.columns([7, 5])

with col_line:
    spending_trend = get_spending_trend(student_id, months=6)
    if spending_trend:
        fig_trend = create_monthly_trend(spending_trend, budget_limit=3000.0, lang=lang)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No spending trend data available.")

with col_donut:
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
    else:
        st.info("No categorical data for current month.")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 2: Credit Journey & FX Monitoring ────────────────────────────────────
st.markdown(f"### 💳 {'征信成长曲线与汇率监控' if lang == 'zh' else 'Credit Journey & FX Rate Tracking'}")

col_credit, col_fx = st.columns([6, 6])

with col_credit:
    credit_hist = get_credit_trend(student_id)
    if credit_hist:
        fig_credit = create_credit_journey(credit_hist, lang=lang)
        st.plotly_chart(fig_credit, use_container_width=True)
    else:
        st.info("No credit history records found.")

with col_fx:
    # Allow user to pick currency pair
    pair_choice = st.selectbox(
        "选择外汇币种对 / Currency Pair" if lang == "zh" else "Select Currency Pair",
        options=["BDT", "PKR", "NGN"],
        index=["BDT", "PKR", "NGN"].index(home_curr) if home_curr in ["BDT", "PKR", "NGN"] else 0,
    )
    fx_data = get_fx_trend(pair_choice, "CNY", days=30)
    if fx_data:
        fig_fx = create_fx_trend(fx_data, currency=pair_choice, lang=lang)
        st.plotly_chart(fig_fx, use_container_width=True)
    else:
        st.info(f"No FX data found for {pair_choice}/CNY.")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 3: Remittance Optimizer Comparison ───────────────────────────────────
st.markdown(f"### 🏦 {'跨境汇款服务商综合成本测算' if lang == 'zh' else 'Cross-Border Remittance Cost Optimizer'}")
st.caption(
    "根据固定汇费与汇率点差综合测算 · 推荐微众银行直连汇款 (WeBank Direct) 享极优手续费与快速清算"
    if lang == "zh"
    else "Benchmarking flat fees and FX markups for a $500 USD student transfer to China."
)

remit_opts = compare_remittance_options(amount_usd=500.0, destination_country="CN")
fig_remit = create_remittance_comparison(remit_opts, lang=lang)
st.plotly_chart(fig_remit, use_container_width=True)

# Table breakdown
st.markdown(f"##### 📋 {'详细费用对比明细' if lang == 'zh' else 'Detailed Provider Breakdown'}")
table_rows = []
for o in remit_opts:
    rec_badge = "⭐ Recommended / 推荐" if o["recommended"] else ""
    table_rows.append({
        "Provider / 服务商": o["provider"],
        "Base Fee / 基础汇费": f"${o['fee_usd']:.2f} USD",
        "FX Markup / 汇率点差": f"{o['fx_markup_pct']:.2f}%",
        "FX Cost / 点差折算": f"${o['fx_cost_usd']:.2f} USD",
        "Total Cost / 综合总成本": f"${o['total_cost_usd']:.2f} USD",
        "Speed / 到账时效": f"{o['delivery_days']} Business Day(s) / 工作日",
        "Status / 评级": rec_badge,
    })
st.dataframe(table_rows, use_container_width=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 4: Global Synthetic Transactions Benchmark (5,000 Records) ───────────
st.markdown(f"### 🌐 {'全球留学生交易基准数据集 (5,000条真实仿真数据)' if lang == 'zh' else 'Global Student Financial Benchmark (5,000 Synthetic Records)'}")
st.caption(
    "基于 Faker 与数理金融分布生成的 5,000+ 笔多通道跨境交易基准数据集 · 覆盖微众直通车、支付宝、微信支付、bKash、Wise、银联等通道"
    if lang == "zh"
    else "Faker-generated 5,000+ transaction benchmark dataset covering WeBank Direct, Alipay, WeChat Pay, bKash, Wise, and UnionPay corridors."
)

csv_path = os.path.join("data", "student_finance_transactions_5000.csv")
if os.path.exists(csv_path):
    import pandas as pd
    import plotly.express as px
    
    df_synth = pd.read_csv(csv_path)
    total_volume_usd = df_synth["converted_amount_usd"].sum()
    top_channel = df_synth["channel"].mode()[0]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📦 " + ("总交易笔数" if lang == "zh" else "Total Transactions"), f"{len(df_synth):,}")
    m2.metric("👥 " + ("活跃留学生数" if lang == "zh" else "Unique Students"), f"{df_synth['user_id'].nunique():,}")
    m3.metric("💰 " + ("仿真交易总金额" if lang == "zh" else "Total Volume (USD)"), f"${total_volume_usd:,.0f}")
    m4.metric("🏆 " + ("最高频清算通道" if lang == "zh" else "Top Channel"), top_channel)
    
    col_ch, col_tp = st.columns([6, 6])
    with col_ch:
        ch_counts = df_synth["channel"].value_counts().reset_index()
        ch_counts.columns = ["Channel", "Count"]
        fig_ch = px.bar(
            ch_counts,
            x="Count",
            y="Channel",
            orientation="h",
            color="Count",
            color_continuous_scale=["#3B82F6", "#0A2463"],
            title="<b>" + ("各支付与清算通道交易量分布" if lang == "zh" else "Transaction Volume by Payment Channel") + "</b>"
        )
        fig_ch.update_layout(height=320, margin=dict(t=40, b=20, l=120, r=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ch, use_container_width=True)
        
    with col_tp:
        tp_counts = df_synth["type"].value_counts().reset_index()
        tp_counts.columns = ["Type", "Count"]
        fig_tp = px.pie(
            tp_counts,
            values="Count",
            names="Type",
            hole=0.45,
            color_discrete_sequence=["#0A2463", "#3B82F6", "#E8B84B", "#10B981", "#8B5CF6", "#F97316", "#EC4899"],
            title="<b>" + ("跨境交易类型结构分布" if lang == "zh" else "Transaction Type Composition") + "</b>"
        )
        fig_tp.update_layout(height=320, margin=dict(t=40, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_tp, use_container_width=True)

    # ── Interactive Statistical Anomaly & Cohort Analysis ─────────────────────
    from src.tools.analytics import detect_spending_anomalies, get_cohort_spending_benchmarks
    st.divider()
    
    col_anom, col_bench = st.columns(2)
    with col_anom:
        st.markdown("##### 🔍 " + ("学生资金流水异常波动排查 (Tukey IQR)" if lang == "zh" else "Student Anomaly Screener (Tukey IQR)"))
        anom_res = detect_spending_anomalies(student_id)
        if anom_res["anomaly_count"] > 0:
            st.warning(
                f"⚠️ 检测到 {anom_res['anomaly_count']} 笔超出正常分布的异常支出 (已分析 {anom_res['total_transactions_analyzed']} 笔流水)"
                if lang == "zh"
                else f"⚠️ Flagged {anom_res['anomaly_count']} outlier transaction(s) across {anom_res['total_transactions_analyzed']} records."
            )
            for a in anom_res["anomalies_detected"][:3]:
                st.caption(f"• **{a['date']}** | `{a['type']}`: **{a['amount']:,.0f} {a['currency']}** ({a['deviation_ratio']:.1f}x IQR threshold)")
        else:
            st.success(
                f"🟢 流水正常：已分析 {anom_res['total_transactions_analyzed']} 笔流水，未发现异常消费突增。"
                if lang == "zh"
                else f"🟢 Normal behavior: {anom_res['total_transactions_analyzed']} records analyzed with zero abnormal spikes."
            )

    with col_bench:
        st.markdown("##### 📊 " + ("同行留学生消费基准对比" if lang == "zh" else "Cohort Peer Spend Benchmarks"))
        sel_country = st.selectbox(
            "选择留学目的地" if lang == "zh" else "Select Destination Country",
            options=["China", "Malaysia", "Germany", "UK", "Australia", "USA", "Canada"],
            index=0,
            key="cohort_country_sel"
        )
        c_bench = get_cohort_spending_benchmarks(sel_country)
        cb1, cb2 = st.columns(2)
        cb1.metric("月度生活费中位数" if lang == "zh" else "Median Monthly Living", f"¥{c_bench.get('median_living_expense', 0):,.0f} CNY")
        cb2.metric("学费单笔中位数" if lang == "zh" else "Median Tuition Payment", f"¥{c_bench.get('median_tuition_payment', 0):,.0f} CNY")
        st.caption(f"🏆 " + ("主流结算通道: " if lang == "zh" else "Top Channels: ") + ", ".join(c_bench.get("popular_channels", [])))

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("##### 🔍 " + ("前100笔明细抽样浏览" if lang == "zh" else "Sample Transaction Explorer (Top 100)"))
    st.dataframe(df_synth.head(100), use_container_width=True)
    
    with open(csv_path, "rb") as f:
        csv_bytes = f.read()
    st.download_button(
        label="📥 " + ("下载完整 5,000 笔交易数据集 (CSV)" if lang == "zh" else "Download Full 5,000 Transactions Dataset (CSV)"),
        data=csv_bytes,
        file_name="student_finance_transactions_5000.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )
else:
    st.info("Run `python scripts/generate_synthetic_transactions.py` to generate the 5,000 transaction dataset.")

st.markdown("<br/>", unsafe_allow_html=True)
render_compliance_footer(lang=lang)
