import pytest
from src.tools.fx import get_exchange_rate, convert_amount
from src.tools.remittance import compare_remittance_options, schedule_tuition_payment, commit_schedule_tuition_payment
from src.tools.budget import get_spending_summary, set_budget_category, add_expense, commit_add_expense
from src.tools.credit import get_credit_profile, simulate_credit_action
from src.tools.compliance import check_aml_threshold, check_sanctioned_destination, mask_pii, check_aml_structuring


def test_get_exchange_rate_returns_valid_dict():
    result = get_exchange_rate("BDT", "CNY")
    assert "rate" in result and result["rate"] > 0
    assert "provider" in result
    assert "timestamp" in result
    assert "fee_pct" in result


def test_get_exchange_rate_usd_cny():
    result = get_exchange_rate("USD", "CNY")
    # USD/CNY should be around 7.28
    assert 6.0 < result["rate"] < 9.0


def test_convert_amount_math_is_correct():
    result = convert_amount(1000.0, "BDT", "CNY")
    assert result["original"] == 1000.0
    assert result["converted"] > 0
    # converted ≈ original * rate (within 2% for fees)
    assert abs(result["converted"] - result["original"] * result["rate"]) < result["original"] * result["rate"] * 0.02


def test_convert_amount_has_fee():
    result = convert_amount(1000.0, "USD", "CNY")
    assert "fee_usd" in result
    assert result["fee_usd"] >= 0


def test_compare_remittance_returns_at_least_three():
    options = compare_remittance_options(500.0, "CN")
    assert len(options) >= 3


def test_compare_remittance_sorted_by_cost():
    options = compare_remittance_options(500.0, "CN")
    costs = [o["total_cost_usd"] for o in options]
    assert costs == sorted(costs)


def test_compare_remittance_has_recommended():
    options = compare_remittance_options(500.0, "CN")
    assert any(o["recommended"] for o in options)
    # Only one should be recommended
    assert sum(1 for o in options if o["recommended"]) == 1


def test_schedule_tuition_requires_confirmation():
    result = schedule_tuition_payment("STU001", 8000.0, "2026-11-01")
    assert result["confirmation_required"] is True
    assert "optimal_window" in result
    assert "projected_rate" in result


def test_aml_flags_above_10000():
    result = check_aml_threshold(10001.0)
    assert result["flagged"] is True
    assert result["threshold_usd"] == 10000


def test_aml_flags_exactly_10000_not_flagged():
    result = check_aml_threshold(10000.0)
    assert result["flagged"] is False


def test_aml_passes_below_10000():
    result = check_aml_threshold(9999.99)
    assert result["flagged"] is False


def test_sanctioned_destination_blocks_iran():
    result = check_sanctioned_destination("IR")
    assert result["blocked"] is True
    assert result["reason"] is not None


def test_sanctioned_destination_blocks_north_korea():
    result = check_sanctioned_destination("KP")
    assert result["blocked"] is True


def test_sanctioned_destination_allows_china():
    result = check_sanctioned_destination("CN")
    assert result["blocked"] is False


def test_sanctioned_destination_allows_us():
    result = check_sanctioned_destination("US")
    assert result["blocked"] is False


def test_mask_pii_masks_long_digits():
    masked = mask_pii("Account 12345678 transfer")
    assert "12345678" not in masked
    assert "****" in masked


def test_mask_pii_preserves_short_numbers():
    # numbers shorter than 8 digits should not be masked
    masked = mask_pii("Transfer 500 CNY")
    assert "500" in masked


def test_mask_pii_masks_passport_pattern():
    masked = mask_pii("Passport BD123456")
    assert "123456" not in masked


def test_set_budget_requires_confirmation():
    result = set_budget_category("STU001", "food", 1000.0)
    assert result["confirmation_required"] is True
    assert result["category"] == "food"
    assert result["new_limit_cny"] == 1000.0


def test_add_expense_requires_confirmation():
    result = add_expense("STU001", 50.0, "food", "lunch")
    assert result["confirmation_required"] is True
    assert result["recorded"] is False  # NOT committed until confirmed


def test_credit_profile_has_required_fields():
    result = get_credit_profile("STU001")
    assert "score" in result
    assert "tier" in result
    assert "tips" in result
    assert isinstance(result["tips"], list) and len(result["tips"]) >= 3
    assert "next_milestone" in result


def test_credit_profile_stu001_is_good_tier():
    # STU001 has credit_score=680 → Good tier
    result = get_credit_profile("STU001")
    assert result["tier"] == "Good"
    assert result["score"] == 680


def test_simulate_credit_action():
    result = simulate_credit_action("open_secured_card", "STU001")
    assert "projected_score_change" in result
    assert result["projected_score_change"] > 0
    assert "new_score" in result
    assert "timeline_months" in result


def test_get_spending_summary_structure():
    result = get_spending_summary("STU001", "2026-10")
    assert "categories" in result
    assert "total_cny" in result
    assert "vs_budget_pct" in result


def test_add_expense_rejects_negative_or_zero_amount():
    with pytest.raises(ValueError, match="Expense amount must be greater than zero"):
        add_expense("STU001", -50.0, "food")
    with pytest.raises(ValueError, match="Expense amount must be greater than zero"):
        add_expense("STU001", 0.0, "food")


def test_commit_add_expense_rejects_negative_or_zero_amount():
    with pytest.raises(ValueError, match="Expense amount must be greater than zero"):
        commit_add_expense("STU001", -50.0, "food")
    with pytest.raises(ValueError, match="Expense amount must be greater than zero"):
        commit_add_expense("STU001", 0.0, "food")


def test_set_budget_category_rejects_negative_limit():
    with pytest.raises(ValueError, match="Budget limit must be non-negative"):
        set_budget_category("STU001", "food", -100.0)


def test_convert_amount_rejects_negative_or_zero_amount():
    with pytest.raises(ValueError, match="Conversion amount must be greater than zero"):
        convert_amount(-100.0, "BDT", "CNY")
    with pytest.raises(ValueError, match="Conversion amount must be greater than zero"):
        convert_amount(0.0, "BDT", "CNY")


def test_remittance_rejects_negative_or_zero_amount():
    with pytest.raises(ValueError, match="Transfer amount must be greater than zero"):
        compare_remittance_options(-500.0, "CN")
    with pytest.raises(ValueError, match="Tuition amount must be greater than zero"):
        schedule_tuition_payment("STU001", -8000.0, "2026-11-01")


def test_aml_rejects_negative_or_zero_amount():
    with pytest.raises(ValueError, match="Amount must be greater than zero"):
        check_aml_threshold(-100.0)
    with pytest.raises(ValueError, match="Amount must be greater than zero"):
        check_aml_threshold(0.0)


def test_aml_structuring_detection():
    # Single safe amount
    res = check_aml_structuring("STU001", 3000.0, window_days=7)
    assert "structuring_detected" in res
    assert res["new_amount_usd"] == 3000.0
    assert "aggregate_usd_7d" in res
    assert "risk_level" in res

    # Single large amount above 10000
    res_large = check_aml_structuring("STU001", 12000.0, window_days=7)
    assert res_large["flagged"] is True
    assert res_large["risk_level"] == "HIGH"


def test_commit_schedule_tuition_payment():
    from src.db import get_db
    res = commit_schedule_tuition_payment("STU001", 8500.0, "2026-11-20")
    assert res["scheduled"] is True
    assert res["status"] == "CONFIRMED_AND_RESERVED"
    assert res["amount_cny"] == 8500.0
    
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM alerts WHERE student_id = ? AND alert_type = 'tuition_scheduled' ORDER BY id DESC LIMIT 1",
        ("STU001",)
    ).fetchone()
    conn.close()
    assert row is not None
    assert "8,500.00" in row["message"]


def test_convert_amount_same_currency_zero_fee():
    res = convert_amount(500.0, "CNY", "CNY")
    assert res["original"] == 500.0
    assert res["converted"] == 500.0
    assert res["rate"] == 1.0
    assert res["fee_usd"] == 0.0


def test_sanctioned_destination_handles_names_and_safe_countries():
    # Full name safe
    res_de = check_sanctioned_destination("Germany")
    assert res_de["blocked"] is False
    assert res_de["country"] == "DE"
    
    res_my = check_sanctioned_destination("Malaysia")
    assert res_my["blocked"] is False
    assert res_my["country"] == "MY"
    
    # Full name sanctioned
    res_ir = check_sanctioned_destination("Iran")
    assert res_ir["blocked"] is True
    assert res_ir["country"] == "IR"
    
    res_ru = check_sanctioned_destination("Russia")
    assert res_ru["blocked"] is True
    assert res_ru["country"] == "RU"


def test_fx_expanded_currencies():
    for curr in ["CAD", "AUD", "MYR", "SGD", "AED", "SAR", "THB"]:
        res = get_exchange_rate(curr, "CNY")
        assert res["rate"] > 0
        assert res["from_currency"] == curr
        assert res["to_currency"] == "CNY"

