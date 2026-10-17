"""Unit tests for China SAFE regulations, student tuition quota exemptions, and PBOC CIPS clearing."""
import pytest
from src.tools.compliance import (
    check_safe_quota,
    verify_student_tuition_eligibility,
    get_cips_clearing_window,
)


def test_safe_quota_under_threshold():
    res = check_safe_quota("STU001", amount_usd=5000.0, purpose="living_expense")
    assert res["quota_usd"] == 50000.0
    assert res["status"] == "WITHIN_QUOTA"
    assert res["quota_exceeded"] is False
    assert res["remaining_quota_usd"] > 0


def test_safe_quota_exceeded_for_general_purpose():
    # 55,000 USD transfer exceeds 50,000 SAFE annual quota
    res = check_safe_quota("STU001", amount_usd=55000.0, purpose="general_transfer")
    assert res["quota_exceeded"] is True
    assert res["status"] == "QUOTA_EXCEEDED_DOCUMENTATION_REQUIRED"
    assert "SAFE" in res["regulation"]


def test_safe_quota_tuition_exemption():
    # Large tuition transfer of 60,000 USD is exempt under genuine university tuition verification
    res = check_safe_quota("STU001", amount_usd=60000.0, purpose="tuition", university_verified=True)
    assert res["exemption_applied"] is True
    assert res["status"] == "EXEMPT_GENUINE_TUITION_TRANSACTION"
    assert res["quota_exceeded"] is False


def test_verify_student_tuition_eligibility_stu001():
    res = verify_student_tuition_eligibility("STU001")
    assert res["student_id"] == "STU001"
    assert res["is_eligible"] is True
    assert res["visa_type"] in ["X1", "X2"]
    assert "university" in res
    assert "documentation_status" in res


def test_cips_clearing_window_structure():
    cips = get_cips_clearing_window()
    assert "cips_active" in cips
    assert "cips_system" in cips
    assert "next_settlement_window" in cips
    assert "beijing_time" in cips
    assert "operating_hours" in cips
