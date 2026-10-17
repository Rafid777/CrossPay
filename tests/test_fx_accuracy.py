"""Unit tests for precision FX, live rates, PBOC parity, and volatility modeling."""
import pytest
from src.tools.fx import (
    get_exchange_rate,
    convert_amount,
    get_pboc_central_parity_rate,
    get_fx_volatility_metrics,
)


def test_get_exchange_rate_real_or_fallback():
    res = get_exchange_rate("USD", "EUR")
    assert "rate" in res and res["rate"] > 0
    assert res["from_currency"] == "USD"
    assert res["to_currency"] == "EUR"
    assert "timestamp" in res
    assert "provider" in res


def test_pboc_central_parity_rate_structure():
    quote = get_pboc_central_parity_rate("USD")
    assert quote["currency"] == "USD"
    assert quote["base"] == "CNY"
    assert 6.5 < quote["central_parity_rate"] < 7.6
    assert quote["band_lower"] < quote["central_parity_rate"] < quote["band_upper"]
    assert quote["fx_buying_rate"] < quote["central_parity_rate"] < quote["fx_selling_rate"]
    assert quote["cash_buying_rate"] < quote["fx_buying_rate"]
    assert quote["statutory_daily_band_pct"] == 2.0


def test_pboc_central_parity_rate_eur_and_gbp():
    eur_quote = get_pboc_central_parity_rate("EUR")
    assert eur_quote["currency"] == "EUR"
    assert eur_quote["central_parity_rate"] > 0
    
    gbp_quote = get_pboc_central_parity_rate("GBP")
    assert gbp_quote["currency"] == "GBP"
    assert gbp_quote["central_parity_rate"] > 0


def test_fx_volatility_metrics_structure():
    metrics = get_fx_volatility_metrics("BDT", "CNY")
    assert "from_currency" in metrics
    assert "to_currency" in metrics
    assert "current_rate" in metrics
    assert "sma_30" in metrics
    assert "std_30" in metrics
    assert "bollinger_upper" in metrics
    assert "bollinger_lower" in metrics
    assert "percentile_30d" in metrics
    assert "recommendation" in metrics
    assert metrics["recommendation"] in ["OPTIMAL_BUY", "NEUTRAL", "WAIT_FOR_DIP"]
    assert metrics["bollinger_lower"] <= metrics["sma_30"] <= metrics["bollinger_upper"]
