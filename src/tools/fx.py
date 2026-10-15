from datetime import datetime

# Mock exchange rates (base: USD)
_RATES_TO_USD = {
    "USD": 1.0,
    "CNY": 1 / 7.28,
    "BDT": 1 / 112.0,
    "PKR": 1 / 278.5,
    "NGN": 1 / 1520.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "JPY": 1 / 149.5,
    "KRW": 1 / 1325.0,
    "INR": 1 / 83.5,
}

FEE_PCT = 0.005  # 0.5% provider fee


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """Get mock exchange rate between two currencies."""
    from_usd = _RATES_TO_USD.get(from_currency.upper())
    to_usd = _RATES_TO_USD.get(to_currency.upper())
    if from_usd is None:
        raise ValueError(f"Unsupported currency: {from_currency}")
    if to_usd is None:
        raise ValueError(f"Unsupported currency: {to_currency}")
    rate = from_usd / to_usd
    return {
        "rate": round(rate, 6),
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "provider": "CrossPay FX (Mock Data)",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fee_pct": FEE_PCT * 100,
    }


def convert_amount(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between currencies, applying provider fee."""
    rate_info = get_exchange_rate(from_currency, to_currency)
    rate = rate_info["rate"]
    gross_converted = amount * rate
    fee_in_from = amount * FEE_PCT
    fee_usd = fee_in_from * _RATES_TO_USD.get(from_currency.upper(), 1.0)
    net_converted = gross_converted * (1 - FEE_PCT)
    return {
        "original": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "rate": rate,
        "converted": round(net_converted, 2),
        "fee_usd": round(fee_usd, 4),
        "provider": rate_info["provider"],
        "timestamp": rate_info["timestamp"],
    }
