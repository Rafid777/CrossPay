"""Tests for health score, smart alerts, analytics tools, and PDF generation."""
import pytest
from src.db import get_db
from src.mock_data import seed_mock_data
from src.health_score import calculate_health_score
from src.alerts import get_active_alerts
from src.tools.analytics import get_fx_trend, get_spending_trend, get_credit_trend
from src.pdf_report import generate_pdf_report


@pytest.fixture(autouse=True)
def setup_test_db():
    conn = get_db()
    seed_mock_data(conn)
    conn.close()


def test_calculate_health_score_stu001():
    result = calculate_health_score("STU001")
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "band" in result
    assert "band_zh" in result
    assert "components" in result
    assert "credit" in result["components"]
    assert "spending_discipline" in result["components"]
    assert "savings_rate" in result["components"]
    assert "tuition_readiness" in result["components"]
    assert len(result["insights"]) >= 1


def test_calculate_health_score_all_students():
    for stu in ["STU001", "STU002", "STU003"]:
        res = calculate_health_score(stu)
        assert 0 <= res["score"] <= 100
        assert res["band"] in ["Excellent", "Healthy", "Stable", "At Risk", "Critical"]


def test_get_active_alerts_returns_list():
    alerts = get_active_alerts("STU001")
    assert isinstance(alerts, list)
    assert len(alerts) >= 1
    for a in alerts:
        assert "alert_type" in a
        assert "severity" in a
        assert "title" in a
        assert "message" in a
        assert "title_zh" in a
        assert "message_zh" in a


def test_get_fx_trend():
    trend = get_fx_trend("BDT", "CNY", days=30)
    assert isinstance(trend, list)
    assert len(trend) > 0
    assert "date" in trend[0]
    assert "rate" in trend[0]
    assert trend[0]["rate"] > 0


def test_get_spending_trend():
    trend = get_spending_trend("STU001", months=6)
    assert isinstance(trend, list)
    assert len(trend) > 0
    assert "month" in trend[0]
    assert "total" in trend[0]
    assert "categories" in trend[0]


def test_get_credit_trend():
    trend = get_credit_trend("STU001")
    assert isinstance(trend, list)
    assert len(trend) == 6
    assert trend[-1]["score"] == 680


def test_generate_pdf_report():
    conn = get_db()
    student = dict(conn.execute("SELECT * FROM accounts WHERE id = 'STU001'").fetchone())
    conn.close()
    health = calculate_health_score("STU001")
    alerts = get_active_alerts("STU001")
    spending = {"categories": {"food": 500.0, "transport": 150.0}, "total_cny": 650.0, "vs_budget_pct": 21.7}
    credit_hist = get_credit_trend("STU001")

    pdf_bytes = generate_pdf_report(student, health, alerts, spending, credit_hist)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
