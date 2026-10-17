import pytest
from src.tools.fraud import (
    screen_tuition_proxy_scam,
    screen_peer_exchange_risk,
    evaluate_transaction_fraud_risk,
    check_telecom_fraud_keywords,
)


def test_screen_tuition_proxy_scam_flags_deep_discount():
    # 20% discount offered by third-party proxy
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=8000.0,
        payment_channel="WeChat Private Agent",
        is_official_portal=False
    )
    assert result["scam_detected"] is True
    assert result["risk_tier"] == "CRITICAL"
    assert result["risk_score"] >= 85
    assert any("discount" in flag.lower() for flag in result["red_flags"])
    assert "96110" in result["legal_warning"]


def test_screen_tuition_proxy_scam_passes_official_portal():
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=10000.0,
        payment_channel="University Portal",
        is_official_portal=True
    )
    assert result["scam_detected"] is False
    assert result["risk_tier"] == "LOW"
    assert result["risk_score"] < 20


def test_screen_tuition_proxy_scam_invalid_amount_raises():
    with pytest.raises(ValueError):
        screen_tuition_proxy_scam(
            tuition_amount_cny=0.0,
            quoted_cost_cny=0.0,
            payment_channel="Agent",
            is_official_portal=False
        )


def test_screen_tuition_proxy_scam_moderate_discount():
    # 7% discount
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=9300.0,
        payment_channel="Unofficial Third-Party",
        is_official_portal=False
    )
    assert result["scam_detected"] is True
    assert result["risk_tier"] == "HIGH"
    assert result["risk_score"] == 75


def test_screen_tuition_proxy_scam_minimal_variance_unofficial():
    # 2% discount
    result = screen_tuition_proxy_scam(
        tuition_amount_cny=10000.0,
        quoted_cost_cny=9800.0,
        payment_channel="Third-Party App",
        is_official_portal=False
    )
    assert result["scam_detected"] is False
    assert result["risk_tier"] == "MEDIUM"
    assert result["risk_score"] == 40


def test_screen_peer_exchange_risk_flags_underground_p2p():
    result = screen_peer_exchange_risk(
        amount=5000.0,
        currency="CNY",
        counterparty_type="Private Individual",
        platform="WeChat Group"
    )
    assert result["card_freeze_risk"] is True
    assert result["risk_tier"] in ["HIGH", "CRITICAL"]
    assert "断卡行动" in result["warning_zh"]


def test_screen_peer_exchange_risk_passes_licensed_bank():
    result = screen_peer_exchange_risk(
        amount=5000.0,
        currency="CNY",
        counterparty_type="Licensed Bank",
        platform="WeBank"
    )
    assert result["card_freeze_risk"] is False
    assert result["risk_tier"] == "LOW"


def test_screen_peer_exchange_risk_critical_large_amount():
    result = screen_peer_exchange_risk(
        amount=15000.0,
        currency="CNY",
        counterparty_type="Private Individual",
        platform="Telegram Group"
    )
    assert result["card_freeze_risk"] is True
    assert result["risk_tier"] == "CRITICAL"


def test_evaluate_transaction_fraud_risk_high_velocity_and_night():
    result = evaluate_transaction_fraud_risk(
        student_id="STU001",
        amount_cny=4500.0,
        channel="Alipay Unverified QR",
        recipient_account="622202******9876",
        hour_of_day=3,  # 3 AM off-hours
        recent_txn_count_1h=4  # High velocity
    )
    assert result["risk_score"] >= 70
    assert result["risk_tier"] in ["HIGH", "CRITICAL"]
    assert result["action_required"] in ["STEP_UP_AUTH", "HARD_BLOCK"]


def test_evaluate_transaction_fraud_risk_normal_daytime_single():
    result = evaluate_transaction_fraud_risk(
        student_id="STU001",
        amount_cny=150.0,
        channel="WeBank Direct",
        recipient_account="University Cafeteria",
        hour_of_day=12,
        recent_txn_count_1h=1
    )
    assert result["risk_score"] < 30
    assert result["risk_tier"] == "LOW"
    assert result["action_required"] == "PROCEED"


def test_evaluate_transaction_fraud_risk_masks_unmasked_pii():
    result = evaluate_transaction_fraud_risk(
        student_id="STU001",
        amount_cny=55000.0,
        channel="P2P Transfer",
        recipient_account="6222021234567890",
        hour_of_day=2,
        recent_txn_count_1h=2
    )
    assert "6222021234567890" not in result["recipient_account"]
    assert "****" in result["recipient_account"]
    assert result["risk_score"] >= 80
    assert result["risk_tier"] == "CRITICAL"
    assert result["action_required"] == "HARD_BLOCK"


def test_check_telecom_fraud_keywords_triggers_safe_account():
    result = check_telecom_fraud_keywords("Please transfer funds to the safe account 安全账户 for verification")
    assert result["fraud_pattern_detected"] is True
    assert "safe account" in result["pattern_type"].lower()
    assert "96110" in result["hotline"]


def test_check_telecom_fraud_keywords_clean_query():
    result = check_telecom_fraud_keywords("What is the exchange rate for BDT to CNY?")
    assert result["fraud_pattern_detected"] is False


def test_check_telecom_fraud_keywords_other_patterns():
    # Public security impersonation
    r1 = check_telecom_fraud_keywords("公检法调查，请配合资金核查")
    assert r1["fraud_pattern_detected"] is True
    assert "公检法" in r1["pattern_type"]

    # Money mule / card renting
    r2 = check_telecom_fraud_keywords("兼职高薪，提供银行卡跑分租卡")
    assert r2["fraud_pattern_detected"] is True
    assert "跑分" in r2["pattern_type"] or "租卡" in r2["pattern_type"]


def test_dispatch_tool_screen_tuition_proxy_scam():
    from src.tool_registry import dispatch_tool
    result = dispatch_tool("screen_tuition_proxy_scam", {
        "tuition_amount_cny": 10000.0,
        "quoted_cost_cny": 7500.0,
        "payment_channel": "WeChat Agent",
        "is_official_portal": False
    })
    assert "scam_detected" in result
    assert result["scam_detected"] is True


def test_dispatch_tool_evaluate_fraud_risk():
    from src.tool_registry import dispatch_tool
    result = dispatch_tool("evaluate_transaction_fraud_risk", {
        "student_id": "STU001",
        "amount_cny": 12000.0,
        "channel": "P2P",
        "recipient_account": "6222000011112222",
        "hour_of_day": 3,
        "recent_txn_count_1h": 5
    })
    assert "risk_score" in result
    assert result["risk_score"] > 60


def test_fraud_tools_in_tool_declarations():
    from src.tool_registry import TOOL_DECLARATIONS
    names = [d["name"] for d in TOOL_DECLARATIONS]
    assert "screen_tuition_proxy_scam" in names
    assert "screen_peer_exchange_risk" in names
    assert "evaluate_transaction_fraud_risk" in names
    assert "check_telecom_fraud_keywords" in names


def test_autonomous_engine_detects_tuition_scam_query_en():
    from src.autonomous_engine import AutonomousFinEngine
    engine = AutonomousFinEngine("STU001")
    response = engine.chat("Someone on WeChat offered me 20% discount on my tuition, is it a scam?")
    assert "scam" in response.lower() or "fraud" in response.lower()
    assert "96110" in response or "chargeback" in response.lower()


def test_autonomous_engine_detects_card_break_risk_zh():
    from src.autonomous_engine import AutonomousFinEngine
    engine = AutonomousFinEngine("STU001")
    response = engine.chat("有人想租借我的银行卡和微信支付二维码跑分，可以借吗？")
    assert "断卡" in response or "违法" in response or "反诈" in response or "96110" in response


def test_autonomous_engine_telecom_safe_account_warning():
    from src.autonomous_engine import AutonomousFinEngine
    engine = AutonomousFinEngine("STU001")
    response = engine.chat("Police told me my account is frozen and asked to transfer money to a safe account")
    assert "safe account" in response.lower() or "安全账户" in response or "fraud" in response.lower()
    assert "96110" in response
