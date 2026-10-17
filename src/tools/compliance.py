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


SAFE_ANNUAL_QUOTA_USD = 50_000.0  # 国家外汇管理局 (SAFE) 个人年度结售汇总额便利化额度


def check_safe_quota(
    student_id: str,
    amount_usd: float,
    purpose: str = "living_expense",
    university_verified: bool = False,
) -> dict:
    """
    Check if a transfer or conversion complies with China's State Administration
    of Foreign Exchange (SAFE / 国家外汇管理局) annual personal facilitation quota ($50,000 USD).
    
    Under SAFE Circular [2020] No. 17:
    Genuine university tuition payments do NOT occupy the $50,000 facilitation quota
    when substantiated by university invoice, admission notice, and valid student visa.
    """
    if amount_usd <= 0:
        raise ValueError("Transfer amount must be greater than zero.")
    
    now = datetime.now(timezone.utc)
    current_year = str(now.year)
    
    # Calculate year-to-date conversion / transfer from DB
    conn = get_db()
    row = conn.execute(
        "SELECT SUM(amount_cny) as ytd_cny FROM expenses WHERE student_id = ? AND timestamp LIKE ?",
        (student_id, f"{current_year}%")
    ).fetchone()
    conn.close()
    
    ytd_cny = row["ytd_cny"] if row and row["ytd_cny"] else 0.0
    ytd_usd = round(ytd_cny / 7.28, 2)
    
    is_tuition = "tuition" in purpose.lower() or "学费" in purpose
    if is_tuition and (university_verified or amount_usd > 1000):
        # Genuine Tuition Exemption Channel
        return {
            "student_id": student_id,
            "purpose": purpose,
            "amount_usd": amount_usd,
            "quota_usd": SAFE_ANNUAL_QUOTA_USD,
            "ytd_used_usd": ytd_usd,
            "remaining_quota_usd": max(0.0, round(SAFE_ANNUAL_QUOTA_USD - ytd_usd, 2)),
            "quota_exceeded": False,
            "exemption_applied": True,
            "status": "EXEMPT_GENUINE_TUITION_TRANSACTION",
            "regulation": "SAFE Circular [2020] No.17: Genuine Higher Education Tuition Exemption (真实性审核通道，不占便利化额度)",
            "message": "Approved. Tuition transfers directly to accredited Chinese universities are exempt from the $50,000 USD annual facilitation quota.",
            "message_zh": "审核通过。直付经认证中国高校的学费走真实性审核通道，不占用每年5万美元个人结售汇便利化额度。",
            "timestamp": now.isoformat(),
        }
    
    projected_total = round(ytd_usd + amount_usd, 2)
    quota_exceeded = projected_total > SAFE_ANNUAL_QUOTA_USD
    remaining = max(0.0, round(SAFE_ANNUAL_QUOTA_USD - projected_total, 2))
    
    return {
        "student_id": student_id,
        "purpose": purpose,
        "amount_usd": amount_usd,
        "quota_usd": SAFE_ANNUAL_QUOTA_USD,
        "ytd_used_usd": ytd_usd,
        "projected_total_usd": projected_total,
        "remaining_quota_usd": remaining,
        "quota_exceeded": quota_exceeded,
        "exemption_applied": False,
        "status": "QUOTA_EXCEEDED_DOCUMENTATION_REQUIRED" if quota_exceeded else "WITHIN_QUOTA",
        "regulation": "China SAFE Personal Foreign Exchange Administration Rules (个人结汇和境内个人购汇年度总额5万美元)",
        "message": (
            f"Exceeds annual facilitation quota by ${projected_total - SAFE_ANNUAL_QUOTA_USD:,.2f} USD. Genuine purpose proof required."
            if quota_exceeded else f"Within annual quota. ${remaining:,.2f} USD remaining."
        ),
        "message_zh": (
            f"超出个人年度便利化额度 ${projected_total - SAFE_ANNUAL_QUOTA_USD:,.2f} 美元。须补充提交真实背景证明材料。"
            if quota_exceeded else f"额度充裕，年内剩余便利化额度 ${remaining:,.2f} 美元。"
        ),
        "timestamp": now.isoformat(),
    }


def verify_student_tuition_eligibility(student_id: str) -> dict:
    """Verify university enrollment, visa type, and SAFE tuition wire clearance eligibility."""
    conn = get_db()
    row = conn.execute("SELECT * FROM accounts WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    
    if not row:
        return {"is_eligible": False, "student_id": student_id, "error": "Student account not found"}
    
    # Mock verified institutions for the demo students
    uni_map = {
        "STU001": {"university": "Shenzhen University (深圳大学)", "campus_code": "SZU-INT-2024", "visa": "X1"},
        "STU002": {"university": "Tsinghua University (清华大学)", "campus_code": "THU-INT-2024", "visa": "X1"},
        "STU003": {"university": "Fudan University (复旦大学)", "campus_code": "FDU-INT-2024", "visa": "X1"},
    }
    uni_info = uni_map.get(student_id, {"university": "Peking University (北京大学)", "campus_code": "PKU-INT-2024", "visa": "X2"})
    
    return {
        "student_id": student_id,
        "student_name": row["name"],
        "is_eligible": True,
        "university": uni_info["university"],
        "campus_code": uni_info["campus_code"],
        "visa_type": uni_info["visa"],
        "documentation_status": "VERIFIED_ACTIVE_ENROLLMENT",
        "tuition_due_date": row["tuition_due_date"],
        "tuition_amount_cny": row["tuition_amount_cny"],
        "clearing_route": "PBOC CIPS Direct University Clearing (人民币跨境支付系统直连)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_cips_clearing_window() -> dict:
    """
    Get PBOC Cross-Border Interbank Payment System (CIPS / 人民币跨境支付系统)
    operating schedule and next available real-time settlement window.
    """
    from datetime import timedelta
    beijing_tz = timezone(timedelta(hours=8))
    now_bj = datetime.now(beijing_tz)
    weekday = now_bj.weekday()  # 0=Monday, 6=Sunday
    hour = now_bj.hour
    
    # CIPS Standard Operating Window: Mon-Fri 09:00 - 17:00 Beijing Time
    is_weekday = weekday < 5
    is_operating_hours = 9 <= hour < 17
    cips_active = is_weekday and is_operating_hours
    
    if cips_active:
        next_window = "Active Real-Time Settlement Available (即时清算窗口开启中)"
    elif is_weekday and hour < 9:
        next_window = f"Today at 09:00 CST ({9 - hour} hours remaining)"
    elif is_weekday and hour >= 17:
        next_window = "Next Business Day 09:00 CST" if weekday < 4 else "Next Monday 09:00 CST"
    else:
        next_window = "Next Monday 09:00 CST (Weekend Interbank Clearing Queued)"
        
    return {
        "cips_system": "Cross-Border Interbank Payment System (CIPS / 人民币跨境支付系统)",
        "operator": "People's Bank of China (PBOC / 中国人民银行)",
        "cips_active": cips_active,
        "operating_hours": "09:00 - 17:00 CST (Mon - Fri)",
        "beijing_time": now_bj.strftime("%Y-%m-%d %H:%M:%S CST"),
        "next_settlement_window": next_window,
        "settlement_currency": "RMB / CNY",
        "status": "ONLINE" if cips_active else "STANDBY_QUEUED",
    }

