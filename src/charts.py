"""Interactive Plotly charts designed for CrossPay fintech experience."""
import plotly.graph_objects as go
import plotly.express as px

# Theme Colors
COLOR_PRIMARY = "#0A2463"
COLOR_ACCENT = "#E8B84B"
COLOR_BLUE = "#3B82F6"
COLOR_GREEN = "#10B981"
COLOR_RED = "#EF4444"
COLOR_MUTED = "#94A3B8"
PALETTE = ["#0A2463", "#3B82F6", "#E8B84B", "#10B981", "#8B5CF6", "#F97316"]


def create_spending_donut(categories: dict, lang: str = "en") -> go.Figure:
    """Create a sleek donut chart showing expenditure by category."""
    if not categories:
        categories = {"food": 100.0}

    cat_labels_zh = {
        "food": "餐饮美食",
        "transport": "市内交通",
        "books": "书籍文具",
        "utilities": "水电网费",
        "entertainment": "休闲娱乐",
        "other": "其他开支",
    }
    
    labels = [cat_labels_zh.get(k, k.title()) if lang == "zh" else k.title() for k in categories.keys()]
    values = list(categories.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                textinfo="percent+label",
                marker=dict(colors=PALETTE[:len(labels)]),
                hoverinfo="label+value+percent",
                hovertemplate="<b>%{label}</b><br>¥%{value:,.2f} (%{percent})<extra></extra>",
            )
        ]
    )
    title_text = "支出构成比例" if lang == "zh" else "Expense Category Breakdown"
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(size=14, color=COLOR_PRIMARY)),
        margin=dict(t=40, b=20, l=20, r=20),
        showlegend=False,
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_monthly_trend(trend_data: list[dict], budget_limit: float = 3000.0, lang: str = "en") -> go.Figure:
    """Create a 6-month spending line chart with budget baseline."""
    months = [d["month"] for d in trend_data]
    totals = [d["total"] for d in trend_data]

    fig = go.Figure()
    # Actual spend line & fill
    fig.add_trace(
        go.Scatter(
            x=months,
            y=totals,
            mode="lines+markers",
            name="实际月支出" if lang == "zh" else "Actual Spending",
            line=dict(color=COLOR_BLUE, width=3, shape="spline"),
            marker=dict(size=7, color=COLOR_PRIMARY),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.1)",
        )
    )
    # Budget threshold line
    fig.add_trace(
        go.Scatter(
            x=months,
            y=[budget_limit] * len(months),
            mode="lines",
            name="预算基准线" if lang == "zh" else "Budget Limit",
            line=dict(color=COLOR_RED, width=2, dash="dash"),
        )
    )

    title_text = "月度消费走势 vs 预算上限" if lang == "zh" else "Monthly Spending vs. Budget Baseline"
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(size=14, color=COLOR_PRIMARY)),
        yaxis=dict(title="金额 (CNY)" if lang == "zh" else "Amount (CNY)", gridcolor="#F1F5F9"),
        xaxis=dict(gridcolor="#F1F5F9"),
        margin=dict(t=40, b=20, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_credit_journey(credit_history: list[dict], lang: str = "en") -> go.Figure:
    """Create a credit score journey area graph."""
    dates = [d["date"] for d in credit_history]
    scores = [d["score"] for d in credit_history]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers+text",
            name="信用分" if lang == "zh" else "Credit Score",
            text=scores,
            textposition="top center",
            line=dict(color=COLOR_GREEN, width=3, shape="spline"),
            marker=dict(size=8, color=COLOR_PRIMARY),
            fill="tozeroy",
            fillcolor="rgba(16, 185, 129, 0.12)",
        )
    )

    title_text = "跨境信用积分成长记录" if lang == "zh" else "Credit Score Growth Trajectory"
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(size=14, color=COLOR_PRIMARY)),
        yaxis=dict(range=[min(scores) - 20, max(scores) + 30], gridcolor="#F1F5F9"),
        xaxis=dict(gridcolor="#F1F5F9"),
        margin=dict(t=40, b=20, l=40, r=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_fx_trend(fx_data: list[dict], currency: str = "BDT", lang: str = "en") -> go.Figure:
    """Create a 30-day foreign exchange rate chart."""
    dates = [d["date"] for d in fx_data]
    rates = [d["rate"] for d in fx_data]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=rates,
            mode="lines",
            name=f"{currency}/CNY",
            line=dict(color=COLOR_ACCENT, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(232, 184, 75, 0.1)",
        )
    )

    title_text = f"30日汇率波动: {currency}/CNY" if lang == "zh" else f"30-Day FX Trend: {currency}/CNY"
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(size=14, color=COLOR_PRIMARY)),
        yaxis=dict(gridcolor="#F1F5F9"),
        xaxis=dict(gridcolor="#F1F5F9"),
        margin=dict(t=40, b=20, l=50, r=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_remittance_comparison(options: list[dict], lang: str = "en") -> go.Figure:
    """Create a cost comparison bar chart for remittance options."""
    providers = [o["provider"] for o in options]
    costs = [o["total_cost_usd"] for o in options]
    colors = [COLOR_ACCENT if o.get("recommended") else COLOR_PRIMARY for o in options]

    fig = go.Figure(
        data=[
            go.Bar(
                x=costs,
                y=providers,
                orientation="h",
                marker=dict(color=colors),
                text=[f"${c:.2f} USD" for c in costs],
                textposition="auto",
            )
        ]
    )

    title_text = "各服务商到账综合成本比较 (越低越优)" if lang == "zh" else "Total Remittance Cost Comparison ($ USD)"
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", font=dict(size=14, color=COLOR_PRIMARY)),
        xaxis=dict(title="综合费用 (USD)" if lang == "zh" else "Total Cost ($ USD)", gridcolor="#F1F5F9"),
        margin=dict(t=40, b=30, l=120, r=30),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_health_gauge(score: int, band: str = "Healthy", lang: str = "en") -> go.Figure:
    """Create an attractive gauge for the Financial Health Score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(
                text="<b>CrossPay 健康指数</b>" if lang == "zh" else "<b>Health Score™</b>",
                font=dict(size=15, color=COLOR_PRIMARY)
            ),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor=COLOR_MUTED),
                bar=dict(color=COLOR_PRIMARY, thickness=0.25),
                bgcolor="white",
                borderwidth=2,
                bordercolor="#E2E8F0",
                steps=[
                    dict(range=[0, 40], color="#FEE2E2"),
                    dict(range=[40, 60], color="#FFEDD5"),
                    dict(range=[60, 75], color="#FEF3C7"),
                    dict(range=[75, 90], color="#DCFCE7"),
                    dict(range=[90, 100], color="#D1FAE5"),
                ],
            ),
        )
    )
    fig.update_layout(
        margin=dict(t=30, b=20, l=30, r=30),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
