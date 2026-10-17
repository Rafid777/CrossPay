"""Institutional Fraud Detection & Anti-Scam Engine for CrossPay.

Grounding & Compliance:
- PRC Anti-Telecom and Online Fraud Law (《中华人民共和国反电信网络诈骗法》)
- PBOC & MPS 'Card Break Action' (断卡行动)
- PRC Ministry of Education International Student Tuition Payment Alerts
- China National Anti-Fraud Center (国家反诈中心 - 96110)
"""
from datetime import datetime, timezone
from src.tools.compliance import mask_pii

HOTLINE_96110 = "96110 (China National Anti-Fraud Center / 全国反诈专线)"


def screen_tuition_proxy_scam(
    tuition_amount_cny: float,
    quoted_cost_cny: float,
    payment_channel: str,
    is_official_portal: bool
) -> dict:
    """Screen tuition payment proposals for proxy payment scams and stolen card fraud."""
    if tuition_amount_cny <= 0:
        raise ValueError("Tuition amount must be positive.")
    if quoted_cost_cny < 0:
        raise ValueError("Quoted cost cannot be negative.")

    discount_pct = max(0.0, round((1.0 - (quoted_cost_cny / tuition_amount_cny)) * 100, 2))

    if is_official_portal:
        return {
            "scam_detected": False,
            "risk_tier": "LOW",
            "risk_score": 10,
            "discount_pct": discount_pct,
            "red_flags": [],
            "recommendation": "Payment is routed through an official accredited university channel. Safe to proceed.",
            "legal_warning": "Verified official educational institution channel.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    red_flags = []
    if discount_pct >= 10.0:
        red_flags.append(f"Deep tuition discount of {discount_pct}% offered by unverified third-party proxy (classic stolen credit card chargeback scheme)")
        red_flags.append("Unofficial payment agent intermediary lacking university accreditation")
        red_flags.append("Severe risk of tuition cancellation and university expulsion upon bank chargeback")
        return {
            "scam_detected": True,
            "risk_tier": "CRITICAL",
            "risk_score": 95,
            "discount_pct": discount_pct,
            "red_flags": red_flags,
            "recommendation": "IMMEDIATE REJECTION: Do NOT pay via this agent. Chinese universities never authorize third-party discounts. Use official university portals or WeBank Direct.",
            "legal_warning": "CRITICAL WARNING: Unauthorized tuition proxy payments violate PRC Anti-Telecom and Online Fraud Law. If approached, report immediately to China National Anti-Fraud Center at 96110.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    elif discount_pct >= 5.0:
        red_flags.append(f"Suspicious discount of {discount_pct}% offered via non-official intermediary")
        red_flags.append("Third-party payment channel counterparty risk")
        return {
            "scam_detected": True,
            "risk_tier": "HIGH",
            "risk_score": 75,
            "discount_pct": discount_pct,
            "red_flags": red_flags,
            "recommendation": "HIGH CAUTION: Contact your university international student office before transferring funds.",
            "legal_warning": "Report suspicious financial solicitations to National Anti-Fraud Center at 96110.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        red_flags.append("Non-official payment channel without discount")
        return {
            "scam_detected": False,
            "risk_tier": "MEDIUM",
            "risk_score": 40,
            "discount_pct": discount_pct,
            "red_flags": red_flags,
            "recommendation": "Verify agent accreditation directly with university bursar.",
            "legal_warning": "Unofficial payment channels carry counterparty dispute risks. Always prefer official portals.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def screen_peer_exchange_risk(
    amount: float,
    currency: str,
    counterparty_type: str,
    platform: str
) -> dict:
    """Screen currency exchange channels against PBOC 'Card Break Action' (断卡行动) and illegal underground FX."""
    licensed_keywords = ["licensed", "bank", "webank", "official", "regulat", "cips", "unionpay"]
    is_licensed = any(kw in (counterparty_type + " " + platform).lower() for kw in licensed_keywords)

    if is_licensed:
        return {
            "card_freeze_risk": False,
            "risk_tier": "LOW",
            "risk_score": 10,
            "warning_zh": "经由持牌金融机构进行的合法结售汇与跨境转账，符合国家外汇管理局规定。",
            "warning_en": "Lawful currency exchange conducted via licensed financial institution under SAFE regulations.",
            "official_channel_advice": "Proceed via authorized banking corridors.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    is_critical = amount >= 10000.0
    risk_tier = "CRITICAL" if is_critical else "HIGH"
    risk_score = 90 if is_critical else 80

    return {
        "card_freeze_risk": True,
        "risk_tier": risk_tier,
        "risk_score": risk_score,
        "amount": amount,
        "currency": currency.upper(),
        "warning_zh": "⚠️ 极高风险：根据中国人民银行与公安部“断卡行动”监管要求，私下通过社交群组（如微信群、Telegram）换汇属于非法买卖外汇行为。涉案资金流入将直接导致中国境内银行卡被公安机关司法冻结，情节严重者可追究刑事责任。",
        "warning_en": "⚠️ HIGH/CRITICAL RISK: Under PBOC and Public Security 'Card Break Action' (断卡行动) regulations, private currency swaps in chat groups are classified as illegal underground foreign exchange. Receiving illicit funds leads to immediate bank card freezing and criminal liability.",
        "official_channel_advice": "Always use licensed banking channels (WeBank Direct, BOC, ICBC). Never participate in private currency exchange groups.",
        "hotline": HOTLINE_96110,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_transaction_fraud_risk(
    student_id: str,
    amount_cny: float,
    channel: str,
    recipient_account: str,
    hour_of_day: int,
    recent_txn_count_1h: int
) -> dict:
    """Evaluate composite multi-factor transaction fraud risk (0-100 index)."""
    masked_account = mask_pii(recipient_account)
    base_score = 10
    risk_factors = []

    # 1. Off-hours burst anomaly (01:00 - 05:00 CST)
    if hour_of_day in [1, 2, 3, 4, 5]:
        base_score += 25
        risk_factors.append(f"Nocturnal off-hours transfer at {hour_of_day:02d}:00 CST")

    # 2. Velocity anomaly
    if recent_txn_count_1h > 3:
        base_score += 35
        risk_factors.append(f"High-frequency velocity anomaly ({recent_txn_count_1h} transactions within 1 hour)")
    elif recent_txn_count_1h > 1:
        base_score += 15
        risk_factors.append(f"Accelerated transfer frequency ({recent_txn_count_1h} transactions within 1 hour)")

    # 3. Unverified or high-risk channel
    unverified_kw = ["unverified", "p2p", "qr", "anonymous", "private"]
    if any(k in channel.lower() for k in unverified_kw):
        base_score += 25
        risk_factors.append(f"High-risk unverified channel: {channel}")

    # 4. Large single transfer
    if amount_cny >= 50000.0:
        base_score += 20
        risk_factors.append(f"High single-transaction amount (¥{amount_cny:,.2f} CNY)")

    final_score = min(100, max(0, base_score))

    if final_score >= 80:
        risk_tier = "CRITICAL"
        action_required = "HARD_BLOCK"
        advisory = "Transaction blocked pending manual compliance review. Anti-fraud risk exceeds institutional threshold."
    elif final_score >= 60:
        risk_tier = "HIGH"
        action_required = "STEP_UP_AUTH"
        advisory = "Step-up authentication required (SMS OTP + facial verification). Elevated risk indicators detected."
    elif final_score >= 30:
        risk_tier = "MEDIUM"
        action_required = "WARN"
        advisory = "Advisory notice: ensure recipient details are verified before confirming transfer."
    else:
        risk_tier = "LOW"
        action_required = "PROCEED"
        advisory = "Transaction parameters within normal baseline. Safe to proceed."

    return {
        "student_id": student_id,
        "amount_cny": amount_cny,
        "channel": channel,
        "recipient_account": masked_account,
        "risk_score": final_score,
        "risk_tier": risk_tier,
        "action_required": action_required,
        "risk_factors": risk_factors,
        "advisory": advisory,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def check_telecom_fraud_keywords(text: str) -> dict:
    """Scan natural language text for PRC Anti-Telecom and Online Fraud indicators."""
    lower_text = text.lower()

    patterns = [
        ("Safe Account Impersonation / 安全账户诈骗", [
            "safe account", "安全账户", "安全基金", "监管账户", "公证账户", "资金审查账户"
        ]),
        ("Public Security & Judiciary Impersonation / 冒充公检法", [
            "公检法", "涉案", "洗钱嫌疑", "通缉令", "police investigation", "criminal investigation", "司法冻结", "逮捕令"
        ]),
        ("Money Mule & Account Leasing / 借卡跑分洗钱", [
            "租卡", "借卡", "跑分", "出借银行卡", "rent bank card", "card leasing", "bank card rental", "微信商户借用"
        ]),
        ("Tuition Discount Proxy Scam / 代缴学费陷阱", [
            "代缴学费8折", "8折代缴", "代缴学费", "打折学费", "tuition discount scam", "便宜代交学费"
        ]),
        ("Campus Loan / Tax Refund Scam / 注销贷款与退税", [
            "注销校园贷", "退税", "刷单返现", "返利"
        ]),
    ]

    for pattern_name, keywords in patterns:
        for kw in keywords:
            if kw.lower() in lower_text or kw in text:
                return {
                    "fraud_pattern_detected": True,
                    "pattern_type": pattern_name,
                    "matched_keyword": kw,
                    "severity": "CRITICAL",
                    "warning_zh": (
                        "⚠️ 警惕电信网络诈骗：根据《中华人民共和国反电信网络诈骗法》，"
                        "任何要求将资金转入“安全账户”、声称“公检法查案”、要求“租借银行卡/跑分”或提供“打折代缴学费”的行为均为典型诈骗！"
                        "中国公检法与大学绝无所谓安全账户或打折代缴。请立即中止联系，切勿转账，并拨打全国反诈劝阻专线 96110。"
                    ),
                    "warning_en": (
                        "⚠️ Telecom Fraud Alert: Under the PRC Anti-Telecom and Online Fraud Law, "
                        "demands to transfer funds to a 'safe account', impersonation of police/judiciary, offers to 'rent bank cards/mule accounts', "
                        "or offers of 'discounted tuition proxy payments' are confirmed fraudulent scams. "
                        "Do NOT transfer money. Stop all contact and call China National Anti-Fraud Center at 96110."
                    ),
                    "hotline": HOTLINE_96110,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

    return {
        "fraud_pattern_detected": False,
        "pattern_type": None,
        "matched_keyword": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
