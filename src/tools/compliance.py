import re
from datetime import datetime

SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "SD", "MM", "BY", "VE", "ZW", "RU"}
AML_THRESHOLD_USD = 10_000.0


def check_aml_threshold(amount_usd: float) -> dict:
    """Check if a transfer amount exceeds AML reporting threshold."""
    flagged = amount_usd > AML_THRESHOLD_USD
    return {
        "flagged": flagged,
        "threshold_usd": AML_THRESHOLD_USD,
        "amount_usd": amount_usd,
        "reason": (
            "Transfer exceeds $10,000 USD AML reporting threshold. Additional verification required."
            if flagged else None
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def check_sanctioned_destination(country_code: str) -> dict:
    """Check if a destination country is on the sanctions list."""
    blocked = country_code.upper() in SANCTIONED_COUNTRIES
    return {
        "blocked": blocked,
        "country": country_code.upper(),
        "reason": (
            f"Transfers to {country_code.upper()} are blocked under international sanctions regulations."
            if blocked else None
        ),
    }


def mask_pii(text: str) -> str:
    """Mask PII patterns: passport-style patterns and 8+ digit account numbers."""
    # Mask passport-style patterns first: 2 uppercase letters + 6-9 digits
    text = re.sub(r'\b[A-Z]{2}\d{6,9}\b', lambda m: m.group()[:2] + '****', text)
    # Mask standalone 8+ digit sequences
    text = re.sub(r'\b\d{8,}\b', '****', text)
    return text
