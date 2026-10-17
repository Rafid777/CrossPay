"""Unit tests for 5,000 transaction statistical modeling, anomaly detection, and cohort benchmarks."""
import pytest
from src.tools.analytics import (
    detect_spending_anomalies,
    get_cohort_spending_benchmarks,
)


def test_detect_spending_anomalies_stu001():
    anomalies = detect_spending_anomalies("STU001")
    assert "student_id" in anomalies
    assert anomalies["student_id"] == "STU001"
    assert "total_transactions_analyzed" in anomalies
    assert anomalies["total_transactions_analyzed"] > 0
    assert "anomalies_detected" in anomalies
    assert "anomaly_count" in anomalies
    assert "status" in anomalies
    assert isinstance(anomalies["anomalies_detected"], list)


def test_cohort_spending_benchmarks_china():
    benchmarks = get_cohort_spending_benchmarks("China")
    assert benchmarks["study_country"] == "China"
    assert benchmarks["total_transactions_sampled"] > 0
    assert "median_living_expense" in benchmarks
    assert "median_tuition_payment" in benchmarks
    assert "popular_channels" in benchmarks
    assert "completion_rate_pct" in benchmarks
    assert 85.0 <= benchmarks["completion_rate_pct"] <= 100.0


def test_cohort_spending_benchmarks_invalid_country():
    res = get_cohort_spending_benchmarks("Atlantis")
    assert res["status"] == "NO_DATA" or res["total_transactions_sampled"] == 0
