"""Unit tests covering the 6-team comprehensive audit fixes and loopholes remediation."""
import pytest
from src.tools.fx import get_pboc_central_parity_rate, _refresh_live_rates
from src.tools.remittance import commit_schedule_tuition_payment
from src.tools.compliance import check_safe_quota
from src.autonomous_engine import AutonomousFinEngine
from src.charts import create_credit_journey, create_monthly_trend, create_fx_trend
from src.theme import inject_css, load_css
from src.pdf_report import generate_pdf_report


def test_pboc_central_parity_rate_unsupported_currency_raises():
    """Unsupported foreign currency must raise ValueError rather than defaulting to 1.0."""
    with pytest.raises(ValueError, match="Unsupported currency"):
        get_pboc_central_parity_rate("INVALID_CURR")


def test_commit_schedule_tuition_payment_rejects_non_positive():
    """commit_schedule_tuition_payment must defensively reject zero or negative amounts."""
    with pytest.raises(ValueError, match="greater than zero"):
        commit_schedule_tuition_payment("STU001", 0.0, "2026-11-01")

    with pytest.raises(ValueError, match="greater than zero"):
        commit_schedule_tuition_payment("STU001", -500.0, "2026-11-01")


def test_safe_quota_with_cny_conversion():
    """300,000 CNY is ~41,200 USD, which is WITHIN the $50,000 USD SAFE personal quota."""
    res = check_safe_quota("STU001", amount_usd=300000.0, purpose="living_expense", currency="CNY")
    assert res["currency"] == "CNY"
    assert res["original_amount"] == 300000.0
    assert 38000 < res["amount_usd"] < 48000
    assert res["quota_exceeded"] is False
    assert res["status"] == "WITHIN_QUOTA"


def test_safe_quota_with_bdt_conversion():
    """500,000 BDT is ~4,450 USD, within quota."""
    res = check_safe_quota("STU001", amount_usd=500000.0, purpose="living_expense", currency="BDT")
    assert res["currency"] == "BDT"
    assert res["original_amount"] == 500000.0
    assert res["amount_usd"] < 10000.0
    assert res["quota_exceeded"] is False


def test_safe_quota_with_usd_default():
    """Default currency USD remains 100% backwards-compatible."""
    res = check_safe_quota("STU001", amount_usd=5000.0)
    assert res["currency"] == "USD"
    assert res["amount_usd"] == 5000.0
    assert res["quota_exceeded"] is False


def test_autonomous_engine_safe_quota_with_cny():
    """Autonomous engine handles CNY queries for SAFE quota accurately."""
    engine = AutonomousFinEngine("STU001")
    resp, _ = engine.process_query("帮我检查 300,000 人民币结汇是否占用外汇局便利化额度")
    assert "300,000" in resp or "300000" in resp
    assert "USD" in resp


def test_charts_empty_input_robustness():
    """All financial charts must gracefully handle empty data without raising ValueError."""
    fig1 = create_credit_journey([])
    assert fig1 is not None

    fig2 = create_monthly_trend([])
    assert fig2 is not None

    fig3 = create_fx_trend([])
    assert fig3 is not None


def test_theme_inject_css_alias():
    """inject_css must be an alias of load_css for multi-page compatibility."""
    assert callable(inject_css)
    assert inject_css == load_css


def test_pdf_report_cjk_support():
    """PDF generator must compile cleanly with Chinese font registration."""
    student_data = {
        "name": "Rafi Ahmed",
        "home_currency": "BDT",
        "home_country": "Bangladesh",
        "balance_cny": 3500.0,
        "tuition_amount_cny": 8000.0,
        "tuition_due_date": "2026-11-01",
        "credit_score": 680,
        "bank_account": "****1234",
    }
    health_data = {
        "score": 85,
        "band": "Excellent",
        "band_zh": "优秀",
        "components": {
            "credit": 80,
            "spending_discipline": 85,
            "savings_rate": 80,
            "tuition_readiness": 90,
        },
        "weights": {
            "credit": 0.3,
            "spending_discipline": 0.25,
            "savings_rate": 0.2,
            "tuition_readiness": 0.25,
        },
    }
    alerts = [
        {
            "severity": "info",
            "icon": "ℹ️",
            "message": "Tuition due date in 14 days",
            "message_zh": "学费缴纳截止日剩余14天，建议尽早安排结汇。",
        }
    ]
    spending = {"categories": {"food": 450.0, "transport": 120.0}, "total_cny": 570.0, "vs_budget_pct": 19.0}
    credit_hist = [{"date": "2026-05", "score": 650}, {"date": "2026-10", "score": 680}]

    pdf_bytes = generate_pdf_report(student_data, health_data, alerts, spending, credit_hist)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")
