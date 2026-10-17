"""Currency Fuzz & Boundary Stress Verification Test Suite.
Verifies arithmetic boundaries, micro-amounts, large tuition sums,
and whitespace tolerance across FX conversion tools.
"""

import pytest
from src.tools.fx import convert_amount, get_exchange_rate

def test_convert_amount_micro_values():
    """Verify micro-amounts (0.01 BDT) convert with correct precision and non-negative fees."""
    res = convert_amount(0.01, "BDT", "CNY")
    assert res["original"] == 0.01
    assert res["converted"] >= 0.0
    assert res["fee_usd"] >= 0.0

def test_convert_amount_large_tuition():
    """Verify conversion of large semester tuition sums (e.g. 500,000 NGN)."""
    res = convert_amount(500000.0, "NGN", "CNY")
    assert res["converted"] > 0
    assert res["fee_usd"] > 0

def test_currency_case_insensitivity_and_whitespace():
    """Verify currency codes are sanitized against lowercase and outer whitespace."""
    res = get_exchange_rate(" usd ", " cny ")
    assert res["from_currency"] == "USD"
    assert res["to_currency"] == "CNY"
    assert res["rate"] > 0

def test_unsupported_currency_raises_value_error():
    """Verify unsupported currency raises ValueError with clean message."""
    with pytest.raises(ValueError, match="Unsupported currency"):
        get_exchange_rate("XYZ", "CNY")
