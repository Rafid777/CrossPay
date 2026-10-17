import re
from datetime import datetime, timezone
from src.db import get_db

SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "SD", "MM", "BY", "VE", "ZW", "RU"}
AML_THRESHOLD_USD = 10_000.0


def check_aml_threshold(amount_usd: float) -> dict:
    """Check if a single transfer amount exceeds AML reporting threshold."""
    if amount_usd <= 0:
        raise ValueError("Amount must be greater than zero.")
    flagged = amount_usd > AML_THRESHOLD_USD
    return {
        "flagged": flagged,
        "threshold_usd": AML_THRESHOLD_USD,
        "amount_usd": amount_usd,
        "reason": (
            "Transfer exceeds $10,000 USD AML reporting threshold. Additional verification required."
            if flagged else None
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def check_aml_structuring(student_id: str, new_amount_usd: float, window_days: int = 7) -> dict:
    """
    Check for AML structuring (smurfing) across a rolling multi-day window.
    Detects if aggregate recent transactions plus current transfer exceed the $10,000 threshold.
    """
    if new_amount_usd <= 0:
        raise ValueError("Amount must be greater than zero.")
    conn = get_db()
    # Check expenses/transfers in last window_days
    # Convert CNY expenses to USD (1 USD ≈ 7.28 CNY)
    row = conn.execute(
        "SELECT SUM(amount_cny) as total_cny FROM expenses WHERE student_id = ? AND timestamp >= datetime('now', ?)",
        (student_id, f"-{window_days} days")
    ).fetchone()
    conn.close()
    recent_cny = row["total_cny"] if row and row["total_cny"] else 0.0
    recent_usd = round(recent_cny / 7.28, 2)
    aggregate_usd = round(recent_usd + new_amount_usd, 2)
    structuring_flagged = aggregate_usd > AML_THRESHOLD_USD and new_amount_usd <= AML_THRESHOLD_USD
    single_flagged = new_amount_usd > AML_THRESHOLD_USD

    return {
        "student_id": student_id,
        "new_amount_usd": new_amount_usd,
        "recent_usd_7d": recent_usd,
        "aggregate_usd_7d": aggregate_usd,
        "threshold_usd": AML_THRESHOLD_USD,
        "structuring_detected": structuring_flagged,
        "flagged": single_flagged or structuring_flagged,
        "risk_level": "HIGH" if (single_flagged or structuring_flagged) else "LOW",
        "reason": (
            f"Potential structuring detected: Transfer of ${new_amount_usd:,.2f} USD brings 7-day aggregate to ${aggregate_usd:,.2f} USD, exceeding the $10,000 AML threshold."
            if structuring_flagged else (
                f"Single transfer of ${new_amount_usd:,.2f} USD exceeds the $10,000 AML reporting threshold."
                if single_flagged else None
            )
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


import pycountry

SANCTIONED_NAMES = {
    "iran": "IR", "north korea": "KP", "dprk": "KP", "syria": "SY",
    "cuba": "CU", "sudan": "SD", "myanmar": "MM", "burma": "MM",
    "belarus": "BY", "venezuela": "VE", "zimbabwe": "ZW", "russia": "RU",
    "russian federation": "RU",
    "伊朗": "IR", "朝鲜": "KP", "叙利亚": "SY", "古巴": "CU",
    "苏丹": "SD", "缅甸": "MM", "白俄罗斯": "BY", "委内瑞拉": "VE",
    "津巴布韦": "ZW", "俄罗斯": "RU",
}


def resolve_country_alpha2(country_input: str) -> tuple[str, str]:
    """Resolve country code or name to canonical ISO alpha-2 and full name."""
    cleaned = country_input.strip()
    cl = cleaned.lower()
    if cl in SANCTIONED_NAMES:
        code = SANCTIONED_NAMES[cl]
        c = pycountry.countries.get(alpha_2=code)
        return code, c.name if c else cleaned.capitalize()
    if len(cleaned) == 2:
        c = pycountry.countries.get(alpha_2=cleaned.upper())
        return cleaned.upper(), c.name if c else cleaned.upper()
    try:
        c = pycountry.countries.get(name=cleaned)
        if c:
            return c.alpha_2, c.name
        m = pycountry.countries.search_fuzzy(cleaned)
        if m:
            return m[0].alpha_2, m[0].name
    except Exception:
        pass
    return cleaned.upper(), cleaned


def check_sanctioned_destination(country_code: str) -> dict:
    """Check if a destination country is on the international sanctions list."""
    code, full_name = resolve_country_alpha2(country_code)
    blocked = code in SANCTIONED_COUNTRIES
    return {
        "blocked": blocked,
        "country": code,
        "country_name": full_name,
        "reason": (
            f"Transfers to {full_name} ({code}) are blocked under international sanctions regulations (OFAC / UN / SAFE)."
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
